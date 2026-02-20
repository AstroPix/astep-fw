"""
Central module of astropix for use with A-STEP FW. Built from astropix.py wrapper. This incorporates all of the various modules from the original 'module' directory backend (now 'core')
The class methods of all the other modules/cores are inherited here.

Author:  Amanda Steinhebel, amanda.l.steinhebel@nasa.gov
Updates: Adrien Laviron, adrien.laviron@nasa.gov
"""

# Needed modules. They all import their own suppourt libraries,
# and eventually there will be a list of which ones are needed to run
import binascii

# Logging stuff
import logging
import os
import sys
import time
import xml.etree.ElementTree as ET

import pandas as pd
from tqdm import tqdm

import drivers.astep.serial
import drivers.astropix.decode
import drivers.boards
from drivers.cmod import CMODBoard
from drivers.gecco import GeccoCarrierBoard

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class AstropixRun:
    # Init just opens the chip and gets the handle. After this runs
    # asic_config also needs to be called to set it up. Seperating these
    # allows for simpler specifying of values.
    def __init__(self, fpgaxml):
        """
        Initalizes AstropixRun object from xml config file
        """
        self.config = ET.parse(fpgaxml).getroot()
        self.config.find("chipversion").attrib["value"] = int(self.config.find("chipversion").attrib["value"])
        self.config.find("SR").attrib["value"] = self.config.find("SR").attrib["value"]=="True"  # define how to configure. If True, shift registers. If False, SPI

    ##################### FPGA INTERACTIONS #########################
    async def open_fpga(self, cmod: bool|None=None, uart: bool|None=None):
        """Create the Board Driver, open a connection to the hardware and performs a read test"""
        if cmod or self.config.find("fpga").attrib["value"] == "cmod":
            if uart or self.config.find("protocol").attrib["value"] == "uart":
                self.boardDriver = drivers.boards.getCMODUartDriver(self.config.find("port").attrib["value"])
            elif self.config.find("protocol").attrib["value"] == "spi":
                raise NotImplementedError("CMOD/SPI not yet supported")
                #self.boardDriver = drivers.boards.getCMODSPIDriver(*self.config??)
            else:
                self.boardDriver = drivers.boards.getCMODDriver()
        elif self.config.find("fpga").attrib["value"] == "gecco":
            if self.config.find("protocol").attrib["value"] == "uart":
                self.boardDriver = drivers.boards.getGeccoUARTDriver(
                    drivers.astep.serial.getFirstCOMPort()
                )
            elif self.config.find("protocol").attrib["value"] == "ftdi":
                self.boardDriver = drivers.boards.getGeccoFTDIDriver()
            else:
                self.boardDriver.getGeccoDriver()
        else:
            raise RuntimeError(f"""Unsupported or unrecognized protocol \
                                  {self.config.find("protocol").attrib["value"]} \
                                  or FPGA board \
                                  {self.config.find("fpga").attrib["value"]}.""")

        await self.boardDriver.open()
        logger.info("Opened FPGA, testing...")
        await self._test_io()
        logger.info("FPGA test successful.")
        
        return self.boardDriver

    async def fpga_configure_chipversion(self):
        """Configure chip version"""
        await self.boardDriver.rfg.write_chip_version(
            value=self.config.find("chipversion").attrib["value"], flush=True
        )

    async def fpga_configure_clocks(self, flush: bool = True):
        """
        Configure FPGA TS clock (frequency and source), SPI clock frequency
        """
        await self.boardDriver.setSampleClock(enable=True, flush=flush)
        await self.boardDriver.setTimestampClock(enable=True, flush=flush)
        # Setup FPGA timestamps
        await self.boardDriver.layersConfigFPGATimestampFrequency(
            targetFrequencyHz=int(self.config.find("FPGATSfreq").attrib["value"]), flush=flush
        )

        await self.boardDriver.layersConfigFPGATimestamp(
            enable=True,
            use_divider=True,
            use_tlu=self.config.find("useTLU").attrib["value"]=="True",
            flush=flush,
        )
        # await self.boardDriver.layersConfigFPGATimestamp(
        #    enable=True,
        #    force=False,
        #    source_match_counter=True,
        #    source_external=externalTS,
        #    flush=flush,
        # )
        # Configure SPI readout
        await self.boardDriver.configureLayerSPIFrequency(int(self.config.find("SPIfreq").attrib["value"]), flush=flush)

    async def fpga_configure_autoread_keepalive(
        self, nchips: int | None = None, flush=False
    ):
        """
        Compute number of bytes needed between interrupt high and end of data stream in autoread mode
        :param nchips: number of chips in the daisy chain, default=None to compute from the configurations files if alerady loaded.
        """
        if nchips is not None:
            pass #nchips is already set, priority to script-provided values
        elif self.config.find("autoread_keepalive") is not None:
            nchips = int(self.config.find("autoread_keepalive").attrib["value"])
        elif len(self.boardDriver.asics) > 0:
            nchips = self.get_nchips()
        else:
            logger.warning(
                "configure_autoread: No chips number provided and asic configuration not loaded - Setting for 1 chip, may cause issues if more are present!"
            )
            nchips = 1
        nbytes = 5 + nchips - 1
        await self.boardDriver.rfg.write_layers_cfg_nodata_continue(
            value=nbytes, flush=flush
        )

    # close connection with FPGA
    async def fpga_close_connection(self) -> None:
        """
        Closes the FPGA board driver connection
        This is optional, connections are closed automatically upon script ending
        """
        await self.boardDriver.close()

    ##################### YAML INTERACTIONS #########################
    # Will be handled by the new configuration class in the future
    # For now we just stick to Asic

    # Method to initalize the asic. This is taking the place of asic.py.
    def load_yaml(self, yaml:list, chipsPerLane: list, lanes: list|None = None):
        """
        Initalize the asic configuration. Must be called first
        Positional arguments:
        yaml:list of str - Name of yml file(s) with configuration values (one file per bus)
        chipsPerRow:list of int - Number of arrays per SPI bus (one int per bus)
        Optional:
        lanes: list of lane numbers, default=None=range(n_lanes)
        """
        if lanes is None: lanes = range(len(yaml))

        # Define YAML path variables - INPUT SANITIZATION DONE IN MAIN.PY
        # If the provided yaml string is already a file, don't create the default path
        #pathdelim = os.path.sep  # determine if Mac or Windows separators in path name
        #if os.path.exists(yaml) is False:
        #    ymlpath = f"{os.getcwd()}{pathdelim}scripts{pathdelim}config{pathdelim}{yaml}.yml"
        #else:
        #    ymlpath = yaml
        #assert os.path.exists(ymlpath) , f"Config File {ymlpath} was not found, pass the name of a config file from the scripts/config folder"

        # Get config values from YAML and set chip properties
        try:
            for y, nchips, lane in zip(yaml, chipsPerLane, lanes):
                ## Init asic
                self.boardDriver.setupASIC(
                    version=self.config.find("chipversion").attrib["value"],
                    lane=lane,
                    chipsPerLane=nchips,
                    configFile=y,
                )
        except FileNotFoundError as e:
            logger.error(
                "Config File %s was not found, pass the name of a config file from the scripts/config folder", ymlpath
            )
            raise e
        # except Exception as e:
        #     logger.error("An error occured while setting up the asics")
        #     raise e

        ## Test to see whether the yml file can be read
        # try:
        #    self.asics[0].enable_pixel(0,0,0)
        #    self.asics[0].disable_pixel(0,0,0)
        # except KeyError: #could not find expected dictionary in yml file
        #    logger.error(f"Configure file of unexpected form. Make sure proper entries (esp. config -> config_0) and try again")
        #    sys.exit(1)

    def get_nchips(self):
        """
        Returns the maximum number of chips of all daisy chains
        """
        return max(
            map(lambda x: getattr(x, "_num_chips"), self.boardDriver.asics.values())
        )  # dict
        # return max(map(lambda x: getattr(x, "_num_chips"), self.boardDriver.asics)) # list

    # Interface with asic.py
    def cfg_enable_pixel(self, layer: int, chip: int, row: int, col: int):
        self.boardDriver.asics[layer].enable_pixel(chip, col, row)

    # enable pixels for injection. Must be called once per pixel
    def cfg_enable_injection(self, layer: int, chip: int, row: int, col: int):
        try:
            self.boardDriver.asics[layer].enable_inj_col(chip, col)
            self.boardDriver.asics[layer].enable_inj_row(chip, row)
        except (IndexError, KeyError):
            logger.error(
                "Cannot enable injection in pixel layer %d, chip %d, row %d, col %d. Ensure layer, chip, and column values all passed.", layer, chip, row, col
            )
            #sys.exit(1)

    # enable pixels for analog readout. Must be called once per pixel
    def cfg_enable_analog(self, layer: int, chip: int, col: int):
        try:
            # Enable analog pixel from given chip in the daisy chain
            logger.info(
                "enabling analog output in layer %d, chip %d, column %d of  in ", layer, chip, col
            )
            self.boardDriver.asics[layer].enable_ampout_col(chip, col)
            self.cfg_enable_pixel(layer, chip, 0, col)
        except (IndexError, KeyError):
            logger.error(
                "Cannot enable analog pixel - chip does not exist. Ensure layer, chip, and column values all passed."
            )
            #sys.exit(1)

    ##################### CHIP INTERACTIONS #########################
    async def chips_reset(self):
        """
        This method asserts the reset signal for .5s by default then deasserts it
        """
        await self.boardDriver.resetLayers(float(self.config.find("RSTdelay").attrib["value"]))

    async def chips_hold(self, hold: bool):
        """ """
        await self.boardDriver.holdLayers(hold)

    async def chips_select(self, cs: bool):
        """ """
        await self.boardDriver.layersSetSPICSN(cs)

    async def chips_disable_readout(self):
        """ """
        await self.boardDriver.disableLayersReadout(True)

    async def chips_enable_readout(self, autoread: bool|None = None, layerlst: list|None = None):
        """
        Enables data readout from the chips
        :param autoread: bool, default=None
        :Multi-lane setups (CMOD): param layerlst: list of int, layers for which to enable readout, default=None = all configured layers
        """
        if autoread is None: autoread = self.config.find("autoread").attrib["value"]=="True"
        self.layerlst = self.boardDriver.asics.keys() if layerlst is None else layerlst
        if isinstance(self.boardDriver, GeccoCarrierBoard):
            await self.boardDriver.enableLayersReadout(autoread, True)
        elif isinstance(self.boardDriver, CMODBoard):
            await self.boardDriver.enableLayersReadout(self.layerlst, autoread, True)
        else:
            await self.boardDriver.enableLayersReadout()

    ##################### CHIP COMMUNICATIONS #########################
    # Set chip routing
    async def chips_setID(self, layer: int = 0, firstChip: int = 0) -> None:
        logger.info("Writting SPI Routing frame for Layer %d", layer)
        await self.boardDriver.writeRoutingFrame(lane=layer, firstChipID=firstChip)

    # The method to write data to the asic.
    async def chips_setcfg(self):
        """This method resets the chip then writes the configuration - After this method, ASIC will be in Hold with MISO disabled, user must setup for readout mode"""
        if self.config.find("SR").attrib["value"]:
            for layer in self.boardDriver.asics.keys():
                await self.boardDriver.writeSRAsicConfig(lane=layer)
            if self.config.find("chipversion").attrib["value"]==4:
                self.boardDriver.asics[0].ram_set_all(0b00001)
                await self.boardDriver.writeSRAsicConfig(tdac=True)
        else:
            # Set Chip ID
            await self.boardDriver.layersSelectSPI(flush=True)  # Set CS
            for layer in self.boardDriver.asics.keys():
                await self.chips_setID(layer)
            await self.boardDriver.layersDeselectSPI(flush=True)  # Unset CS
            # Configure chips in parallel
            for chip in range(self.get_nchips()):
                await self.boardDriver.layersSelectSPI(flush=True)  # Set CS
                for layer in self.boardDriver.asics.keys():
                    if chip < self.boardDriver.asics[layer].num_chips:
                        await self.boardDriver.writeSPIAsicConfig(
                            lane=layer, targetChip=chip
                        )
                await self.boardDriver.layersDeselectSPI(flush=True)  # Unset CS

    async def chips_reset_configure(self):
        # Reset
        await self.chips_reset()
        # Set FPGA to neutral
        await self.chips_disable_readout()
        # Set chip config
        await self.chips_setcfg()

    async def chips_flush(self):
        """This method will ensure the layer interrupt is not low and flush buffer, and reset counters"""
        # Flush data from sensor
        logger.info("Flush chip before data collection")
        for layer in self.boardDriver.asics.keys():
            await self.boardDriver.setLayerConfig(
                layer,
                reset=False,
                hold=False,
                chipSelect=True,
                autoread=False,
                disableMISO=True,
                flush=True,
            )
            await self.boardDriver.writeSPIBytesToLane(lane=layer, bytes=[0x00] * 128)
            counter = 1
            while (
                await self.boardDriver.getLayerStatus(layer) & 0x1
            ) == 0 and counter < 20:
                await self.boardDriver.writeSPIBytesToLane(
                    lane=layer, bytes=[0x00] * 128
                )
                counter += 1
            await self.boardDriver.setLayerConfig(
                layer,
                reset=False,
                hold=True,
                chipSelect=False,
                autoread=False,
                disableMISO=True,
                flush=True,
            )

    async def buffer_flush(self):
        """
        Flushes the data already present in chips digital periphery, then the FPGA buffer
        """
        await self.chips_flush()
        buff = await self.boardDriver.readoutGetBufferSize()
        await self.boardDriver.readoutReadBytes(buff)

    ## Methods to update the internal variables. Please don't do it manually
    ## This updates the dac config
    # async def update_asic_config(self, layer:int, chip:int, bias_cfg:dict = None, idac_cfg:dict = None, vdac_cfg:dict = None):
    #    #Updates and writes confgbits to asic
    #    #layer, chip indicate which layer and chip in the daisy chain to update
    #    #bias_cfg:dict - Updates the bias settings. Only needs key/value pairs which need updated
    #    #idac_cfg:dict - Updates iDAC settings. Only needs key/value pairs which need updated
    #    #vdac_cfg:dict - Updates vDAC settings. Only needs key/value pairs which need updated
    #
    #    if self._asic_start:
    #        if bias_cfg is not None:
    #            for key in bias_cfg:
    #                self.asics[layer].asic_config[f'config_{chip}']['biasconfig'][key][1]=bias_cfg[key]
    #        if idac_cfg is not None:
    #            for key in idac_cfg:
    #                self.asics[layer].asic_config[f'config_{chip}']['idacs'][key][1]=idac_cfg[key]
    #        if vdac_cfg is not None:
    #            for key in vdac_cfg:
    #                self.asics[layer].asic_config[f'config_{chip}']['vdacs'][key][1]=vdac_cfg[key]
    #        else:
    #            logger.info("update_asic_config() got no arguments, nothing to do.")
    #            return None
    #    else: raise RuntimeError("Asic has not been initalized")

    ################## Voltageboard Methods ############################
    # convert a voltage value to a DAC value
    def get_internal_vdac(self, v_in, v_ref: float = 1.8, nbits: float = 10):
        return int(v_in * 2**nbits / v_ref)

    # Change a pixel threshold value in the global dictionary of configs
    async def update_pixThreshold(self,  vThresh: int, layer: int = 0, chip: int = 0):
        # vThresh = comparator threshold provided in mV
        if self.config.find("fpga").attrib["value"]=="gecco":
            self.init_voltages(vthreshold=vThresh)
        else:
            dacThresh = self.get_internal_vdac(vThresh / 1000.0)  # convert from mV to V
            dacBL = self.boardDriver.asics[layer].asic_config[f"config_{chip}"]["vdacs"]["blpix"][1]
            self.boardDriver.asics[layer].asic_config[f"config_{chip}"]["vdacs"]["thpix"][1] = dacBL + dacThresh
            # await self.update_asic_config(
            #     layer, chip, vdac_cfg={"thpix": dacBL + dacThresh}
            # )

    # initialize voltages with GECCO HW (voltagecard)
    async def init_voltages(
        self,
        vcal: float = 0.989,
        vsupply: float = 2.7,
        vthreshold: float | None  = None,
        dacvals: tuple[int, list[float]] | None = None,
    ):
        """
        Configures the voltage board
        No required parameters. No return.

        vcal:float = 0.908 - Calibration of the voltage rails
        vsupply = 2.7 - Supply Voltage
        vthreshold:float = None - ToT threshold value. Takes precedence over dacvals if set. UNITS: mV
        dacvals:tuple[int, list[float] - vboard dac settings. Must be fully specified if set.
        """
        # The default values to pass to the voltage dac. Last value in list is threshold voltage, default 100mV or 1.1
        # Included in YAML for v3 (not v2)

        # Check the required HW is available
        if not isinstance(self.boardDriver, GeccoCarrierBoard):
            logger.error(
                "No GECCO board configured, so a voltageboard cannot be configured. Check FPGA settings."
            )
            raise RuntimeError(
                "No GECCO board configured, so a voltageboard cannot be configured. Check FPGA settings."
            )

        # From nicholas's beam_test.py:
        # 1=thpmos (comparator threshold voltage), 3 = Vcasc2, 4=BL, 7=Vminuspix, 8=Thpix
        try:
            volt_slot = self.asic.asic_configcards['voltagecard']['pos']
            default_vdac = (len(self.asic.asic_configcards['voltagecard']['dacs']), self.asic.asic_configcards['voltagecard']['dacs'])
        except KeyError: #values not included in yml
            volt_slot = 4
            if self.config.find("chipversion").attrib["value"] == 2:
                default_vdac = (8, [0, 0, 1.1, 1, 0, 0, 1, 1.100])
            elif self.config.find("chipversion").attrib["value"] == 4:
                default_vdac = (8, [  0, 0, 1.1, 1, 0, 0, 0.8, 1.2]) # default for v4
            else:  # increase thpmos for v3 pmos pixels
                default_vdac = (8, [1.1, 0, 1.1, 1, 0, 0, 1,   1.100]) # default for v3
            

        # used to ensure this has been called in the right order:
        self._voltages_exist = True

        # Set dacvals
        if dacvals is None:
            dacvals = default_vdac
            # dacvals takes precidence over vthreshold
            if vthreshold is not None:
                # Turns from mV to V with the 1V offset normally present
                vthreshold = (vthreshold / 1000) + default_vdac[1][3]
                if vthreshold > 1.5 or vthreshold < 0:
                    logger.warning("Threshold voltage out of range of sensor!")
                    if vthreshold <= 0:
                        vthreshold = 1.100
                        logger.error(
                            "Threshold value too low, setting to default 100mV"
                        )
                dacvals[1][-1] = vthreshold

        # Voltage Board is provided by the board Driver
        self.vboard = self.boardDriver.geccoGetVoltageBoard(volt_slot=volt_slot)
        self.vboard.dacvalues = dacvals
        # Set calibrated values
        self.vboard.vcal = vcal
        self.vboard.vsupply = vsupply

        # Send config to the chip
        await self.vboard.update()

    # Setup Injections with GECCO HW (injection card)
    async def init_injection(
        self,
        layer: int,
        chip: int,
        inj_voltage: float|None = None,
        dac_config: tuple[int, list[float]] = None,
    ):
        """
        Configure injections
        Required Arguments:
        layer: int - layer/row of chips
        chip: int - which chip in the daisy chain to inject into
        Optional Arguments:
        inj_voltage: float - Injection Voltage. Range from 0 to 1.8. If dac_config is set inj_voltage will be overwritten
        dac_config:tuple[int, list[float]]: injdac settings. Must be fully specified if set.
        """
        if inj_voltage is not None and self.config.find("injector").attrib["ismV"]=="True":  # Needs conversion to vdac units
            inj_voltage = inj_voltage / 1000.0

        self.injector = self.boardDriver.getInjector()
        self.injector.period = int(self.config.find("injector").attrib["period"])
        self.injector.clkdiv = int(self.config.find("injector").attrib["clkdiv"])
        self.injector.initdelay = int(self.config.find("injector").attrib["initdelay"])
        self.injector.cycle = int(self.config.find("injector").attrib["cycle"])
        self.injector.pulsesperset = int(self.config.find("injector").attrib["pulsesperset"])

        if isinstance(self.boardDriver, GeccoCarrierBoard) and self.config.find("injector").attrib["onchip"]=="False":
            # Injection Board is provided by the board Driver
            # The Injection Board provides an underlying Voltage Board
            await self.boardDriver.ioSetInjectionToGeccoInjBoard(
                enable=True, flush=True
            )
            self.injectorBoard = self.injector.vBoard
            self.injectorBoard.dacvalues = (
                2,
                [inj_voltage, 0.0],
            )
            self.injectorBoard.vcal = self.vboard.vcal
            self.injectorBoard.vsupply = self.vboard.vsupply
            await self.injectorBoard.update()
            logger.info("Injection: Configured to use GECCO card")
        else:
            # Injection provided through integrated features on chip
            if inj_voltage is not None:
                self.boardDriver.asics[layer].asic_config[f"config_{chip}"]["vdacs"]["vinj"][1] = int(inj_voltage * 1024 / 1.8)  # 1.8 V coded on 10 bits
            await self.boardDriver.ioSetInjectionToChip(enable=True, flush=True)
            logger.info("Injection: Configured to use onchip circuit")

    # update injection settings via injectionboard after object is already created
    async def update_injection(
        self,
        layer: int,
        chip: int,
        inj_voltage: float = None,
        inj_period: int = None,
        clkdiv: int = None,
        initdelay: int = None,
        cycle: float = None,
        pulseperset: int = None,
    ):
        """
        Update injections after injector object is created
        Required Arguments:
        layer: int - layer/row of chips
        chip: int - which chip in the daisy chain to inject into
        Optional Arguments:
        inj_voltage: float - Injection Voltage. Range from 0 to 1.8. If dac_config is set inj_voltage will be overwritten
        inj_period: int
        clkdiv: int
        initdelay: int
        cycle: float
        pulseperset: int
        """

        ## DAN - WIP. I don't think this method works yet

        if inj_voltage is not None:
            # elifs check to ensure we are not injecting a negative value because we don't have that ability
            if inj_voltage < 0:
                raise ValueError("Cannot inject a negative voltage!")
            elif inj_voltage > 1800:
                logger.warning("Cannot inject more than 1800mV, will use defaults")
                inj_voltage = 300  # Sets to 300 mV

        if inj_voltage:
            # Update vdac value from yml
            await self.update_asic_config(
                layer,
                chip,
                vdac_cfg={"vinj": self.get_internal_vdac(inj_voltage / 1000.0)},
            )

        if inj_period and inj_period != self.injector.period:
            self.injector.period = inj_period
        if clkdiv and clkdiv != self.injector.clkdiv:
            self.injector.clkdiv = clkdiv
        if initdelay and initdelay != self.injector.initdelay:
            self.injector.initdelay = initdelay
        if cycle and cycle != self.injector.cycle:
            self.injector.cycle = cycle
        if pulseperset and pulseperset != self.injector.pulseperset:
            self.injector.pulseperset = pulseperset

    # Start injection
    async def start_injection(self):
        """
        Starts Injection.
        Takes no arguments and no return
        """
        await self.injector.start()
        #        # Check the required HW is available
        #        if self._geccoBoard:
        #            await self.injector.start()
        #            #print("INJ_WDATA AFTER START")
        #            #print(await self.boardDriver.rfg.read_layers_inj_wdata(1024))
        #        else:
        #            await self.injector.start()
        #            print("STARTING WITH REGISTERS")
        #            ## DAN - unfinished beginning of controlling injection with registers instead of injection card. Necessary for CMOD and parallel in 'stop_injection' method
        #            #layers_inj_val = await self.boardDriver.rfg.read_layers_inj_ctrl()
        #            #if layers_inj_val>0: #injection not running
        #            #    await self.boardDriver.rfg.write_layers_inj_ctrl(0b0)
        #            #    await self.boardDriver.rfg.write_layers_inj_ctrl(0b1)
        #            #    await self.boardDriver.rfg.write_layers_inj_ctrl(0b0)
        logger.info("Began injection")

    # Stop injection
    async def stop_injection(self):
        """
        Stops Injection.
        Takes no arguments and no return
        """
        await self.injector.stop()
        #        # Check the required HW is available
        #        if self._geccoBoard:
        #            await self.injector.stop()
        #        else:
        #            print("STOPPING WITH REGISTERS")
        #            #layers_inj_val = await self.boardDriver.rfg.read_layers_inj_ctrl()
        #            #if layers_inj_val==0: #injection running
        #            #    await self.boardDriver.rfg.write_layers_inj_ctrl(3)
        #
        logger.info("Stopped injection")

    ########################### Input and Output #############################

    # Returns header for use in a log file with all settings.
    # Get config dictionaries from yaml
    def get_log_header(self, layer: int, chip: int):
        vdac_str = ""
        digitalconfig = {}
        for key in self.boardDriver.asics[layer].asic_config[f"config_{chip}"]["digitalconfig"]:
            digitalconfig[key] = self.boardDriver.asics[layer].asic_config[f"config_{chip}"][
                "digitalconfig"
            ][key][1]
        biasconfig = {}
        for key in self.boardDriver.asics[layer].asic_config[f"config_{chip}"]["biasconfig"]:
            biasconfig[key] = self.boardDriver.asics[layer].asic_config[f"config_{chip}"][
                "biasconfig"
            ][key][1]
        idacconfig = {}
        for key in self.boardDriver.asics[layer].asic_config[f"config_{chip}"]["idacs"]:
            idacconfig[key] = self.boardDriver.asics[layer].asic_config[f"config_{chip}"]["idacs"][
                key
            ][1]
        if self.config.find("chipversion").attrib["value"] > 2:
            vdacconfig = {}
            for key in self.boardDriver.asics[layer].asic_config[f"config_{chip}"]["vdacs"]:
                vdacconfig[key] = self.boardDriver.asics[layer].asic_config[f"config_{chip}"][
                    "vdacs"
                ][key][1]
            vdac_str = f"vDAC: {vdacconfig}\n"
        arrayconfig = {}
        for key in self.boardDriver.asics[layer].asic_config[f"config_{chip}"]["recconfig"]:
            arrayconfig[key] = self.boardDriver.asics[layer].asic_config[f"config_{chip}"][
                "recconfig"
            ][key][1]

        # This is not a nice line, but its the most efficent way to get all the values in the same place.
        return (
            f"Digital: {digitalconfig}\n"
            + f"Biasblock: {biasconfig}\n"
            + f"iDAC: {idacconfig}\n"
            + vdac_str
            + f"Receiver: {arrayconfig}"
        )

    ############################ Data Collection / Processing ##############################
    # Properly set up layer config for data collection
    async def setup_readout(self, layer: int, autoread: bool = True):
        # Take take layer out of reset and hold
        await self.boardDriver.setLayerConfig(
            layer=layer, reset=False, autoread=autoread, hold=False, flush=True
        )

    # Read FPGA buffer and return buffer length and data stored within it
    async def get_readout(self, counts: int|None = None):
        if self.config.find("autoread").attrib["value"] != "True":
            for layer in self.layerlst:
                await self.boardDriver.writeSPIBytesToLane(lane=layer, bytes=[0x00] * 50)
        bufferSize = await self.boardDriver.readoutGetBufferSize()
        if counts is None:
            readout = await self.boardDriver.readoutReadBytes(bufferSize)
        else:
            readout = await self.boardDriver.readoutReadBytes(counts)
        return bufferSize, readout
    
    async def get_buffer(self):
        bufferSize = await self.boardDriver.readoutGetBufferSize()
        readout = await self.boardDriver.readoutReadBytes(bufferSize)
        return bufferSize, readout

    # Print status register
    async def print_status_reg(self):
        status = await self.boardDriver.rfg.read_layer_0_status()
        ctrl = await self.boardDriver.rfg.read_layer_0_cfg_ctrl()
        print(
            f"Layer Status:  {hex(status)},interruptn={status & 0x1},decoding={(status >> 1) & 0x1},reset={(ctrl >> 1) & 0x1},hold={(ctrl) & 0x1},buffer={await self.boardDriver.readoutGetBufferSize()}"
        )
        # logger.info(f"Layer Status:  {hex(status)},interruptn={status & 0x1},decoding={(status >> 1) & 0x1},reset={(ctrl>>1) & 0x1},hold={(ctrl) & 0x1},buffer={await (self.boardDriver.readoutGetBufferSize())}")

    # Parse raw data readouts to remove railing. Moved to postprocessing method to avoid SW slowdown when using autoread
    async def dataParse_autoread(self, data, buffer_lst, bitfile: str = None):
        allData = b""
        for i, buff in enumerate(buffer_lst):
            if buff > 0:
                readout_data = data[i][:buff]
                logger.info(binascii.hexlify(readout_data))
                allData += readout_data
                if bitfile:
                    bitfile.write(f"{str(binascii.hexlify(readout_data))}\n")

        ## DAN - could also return buffer index to keep track of whether multiple hits occur in the same readout. Would need to propagate forward

        return allData

    ############################ Decoder ##############################
    # Send data for decoding from raw
    def decode_readout(self, readout: bytearray, i: int, printer: bool = True):
        if self.chipversion==4:
            return drivers.astropix.decode.Decode().decode_readout_v4(logger, readout, i, printer)
        else:
            return drivers.astropix.decode.Decode().decode_readout(logger, readout, i, printer)

    ################## Housekeeping ############################

    async def every(__seconds: float, func, *args, **kwargs):
        # scheduler
        while True:
            func(*args, **kwargs)
            await asyncio.sleep(__seconds)

    async def callHK(
        self, flipped: bool = True
    ):  # adding a setting that can change the byte ordering in the future if we ever fix/change this
        """
        Calls housekeeping from TI ADC128S102 ADC. Loops over each of the 8 input channels.
        Input is two bytes:
        First 2 bits: ignored
        Next 3 bits: Set Channel #
        Last 11 bits: ignored

        Shift register input style requires bytes to be read in left to right. May be fixed in future versions
        """
        assert isinstance(self.boardDriver, CMODBoard), (
            "No housekeeping exists on the Gecco board"
        )
        await driver.houseKeeping.selectADC()

        ## Loop over ADC Settings
        for chan in range(0, 8):
            bits = format(chan, "08b")
            if flipped == True:
                byte1 = int(bits[::-1], 2)  # this is a hex string is this ok?
            else:
                byte1 = int(bits, 2)  # this is a hex string is this ok?

            await driver.houseKeeping.writeADCDACBytes([byte1, 0x00])
            adcBytesCount = await driver.houseKeeping.getADCBytesCount()
            adcBytes = await driver.houseKeeping.readADCBytes(
                adcBytesCount
            )  # still need to output this from task
            print(f"Got ADC bytes {adcBytes}")

    ###################### INTERNAL METHODS ###########################

    # Below here are internal methods used for constructing things and testing

    # _test_io(): A function to read and write a register on the chip to see if
    # everything is working.
    # It takes no arguments
    async def _test_io(self):
        """Reads a register to check a write and readback to the firmware is working"""
        try:  # Attempts to write to and read from a register
            ## Try to read the firmware ID and or Version
            fwId = await self.boardDriver.readFirmwareID()
            logger.info("Reading FWID successful: %s", fwId)
            # self.nexys.write_register(0x09, 0x55, True)
            # self.nexys.read_register(0x09)
            # self.nexys.spi_reset()
            # self.nexys.sr_readback_reset()
        except Exception as e:
            logger.error("Testing FPGA I/O Failed, is the FW flashed?")
            raise RuntimeError("Could not read or write from FW,  is the FW flashed?")

    # progress bar
    def _wait_progress(self, seconds: int):
        for _ in tqdm(range(seconds), desc=f"Wait {seconds} s"):
            time.sleep(1)

    # Check of general functionality esp of SPI lines, as inspired from documentation
    async def functionalityCheck(self, holdBool: bool = True):
        # Take take layer out of reset but keep in hold
        await self.boardDriver.setLayerConfig(
            layer=0, reset=False, hold=holdBool, autoread=False, flush=True
        )

        # Write 16 NULL bytes to the sensor
        await self.boardDriver.writeSPIBytesToLane(lane=0, bytes=[0x00] * 16)

        # Reads the Idle counter  register for the layer 0
        idleCount = await self.boardDriver.rfg.read_layer_0_stat_idle_counter()
        print(f"Actual IDLE counter: {idleCount}")

        # Reads the Frame Counter register for the layer 0
        framesCount = await self.boardDriver.rfg.read_layer_0_stat_frame_counter()
        print(f"Actual Frame counter: {framesCount}")

    # Print values of registers associated with enable/disable injection
    async def checkInjBits(self):
        io_ctrl_val = await self.boardDriver.rfg.read_io_ctrl()
        print(f"io_ctrl value = {io_ctrl_val} = {bin(io_ctrl_val)}")

        layers_inj_val = await self.boardDriver.rfg.read_layers_inj_ctrl()
        print(f"layers_inj value = {layers_inj_val} = {bin(layers_inj_val)}")

    ########## Sanity Helpers ###############
    async def sanity_check_idle(self, layer: int):
        """This method sends some SPI bytes to layer while on Hold, the IDLE byte counter should increase"""
        # Set layer on Hold
        await self.boardDriver.setLayerConfig(
            layer=layer,
            reset=False,
            autoread=False,
            hold=True,
            disableMISO=False,
            flush=True,
        )

        idleBytes = await self.boardDriver.getLayerStatIDLECounter(layer)
        frameBytes = await self.boardDriver.getLayerStatFRAMECounter(layer)
        logger.info(
            f"[Sanity-IDLE {layer}] Before SPI activity, IDLE Bytes counter={idleBytes},Frame Bytes Counter={frameBytes}"
        )

        # Write Some SPI Bytes
        await self.boardDriver.layersSelectSPI(flush=True)
        await self.boardDriver.writeSPIBytesToLane(lane=layer, bytes=[0x00] * 8)
        await self.boardDriver.layersDeselectSPI(flush=True)
        idleBytes = await self.boardDriver.getLayerStatIDLECounter(layer)
        frameBytes = await self.boardDriver.getLayerStatFRAMECounter(layer)
        logger.info(
            f"[Sanity-IDLE {layer}] After SPI activity, IDLE Bytes counter={idleBytes},Frame Bytes Counter={frameBytes}"
        )
        assert idleBytes == 16
