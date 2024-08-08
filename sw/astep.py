"""
Central module of astropix for use with A-STEP FW. Built from astropix.py wrapper. This incorporates all of the various modules from the original 'module' directory backend (now 'core')
The class methods of all the other modules/cores are inherited here. 

Author:  Amanda Steinhebel, amanda.l.steinhebel@nasa.gov
"""
# Needed modules. They all import their own suppourt libraries, 
# and eventually there will be a list of which ones are needed to run
from tqdm import tqdm
import pandas as pd
import time
import os, sys, binascii

import drivers.boards
import drivers.astep.serial
import drivers.astropix.decode

# Logging stuff
import logging
logger = logging.getLogger(__name__)

class astepRun:

    # Init just opens the chip and gets the handle. After this runs
    # asic_config also needs to be called to set it up. Seperating these 
    # allows for simpler specifying of values. 
    def __init__(self, chipversion=3, clock_period_ns = 5, SR:bool=True): 
        """
        Initalizes astropix object. 
        No required arguments
        Optional:
        clock_period_ns:int - period of main clock in ns
        inject:bool - if set to True will enable injection for the whole array.
        SR:bool - if True, configure with shift registers. If False, configure with SPI
        """

        # _asic_start tracks if the inital configuration has been run on the ASIC yet.
        # By not handeling this in the init it simplifies the function, making it simpler
        # to put in custom configurations and allows for less writing to the chip,
        # only doing it once at init or when settings need to be changed as opposed to 
        # each time a parameter is changed.
        self._asic_start = False
        self.asics = []

        self._geccoBoard = None

        self.sampleclock_period_ns = clock_period_ns
        self.chipversion = chipversion
        self.SR = SR #define how to configure. If True, shift registers. If False, SPI


    async def open_fpga(self, cmod:bool, uart:bool): 
        """Create the Board Driver, open a connection to the hardware and performs a read test"""
        if cmod and uart:
            #self.boardDriver = drivers.boards.getCMODUartDriver(drivers.astep.serial.getFirstCOMPort())
            self.boardDriver = drivers.boards.getCMODUartDriver("COM4")
        elif cmod and not uart:
            self.boardDriver = drivers.boards.getCMODDriver()
        elif not cmod and uart:
            self.boardDriver = drivers.boards.getGeccoUARTDriver(drivers.astep.serial.getFirstCOMPort())
        elif not cmod and not uart:
            self.boardDriver = drivers.boards.getGeccoFTDIDriver()

        self._geccoBoard = True if not cmod else False

        self.boardDriver.open()
        logger.info("Opened FPGA, testing...")
        await self._test_io()
        logger.info("FPGA test successful.")
        
        # This method asserts the reset signal for .5s by default then deasserts it
        await self.boardDriver.resetLayer(layer = 0)

##################### YAML INTERACTIONS #########################
#reading done in core/asic.py
#writing done here
    """
    def write_conf_to_yaml(self, filename:str = None):
        #Write ASIC config to yaml
        #:param chipversion: chip version
        #:param filename: Name of yml file in config folder

        dicttofile ={self.asic.chip:
            {
                "telescope": {"nchips": self.asic.num_chips},
                "geometry": {"cols": self.asic.num_cols, "rows": self.asic.num_rows}
            }
        }

        if self.asic.num_chips > 1:
            for chip in range(self.asic.num_chips):
                dicttofile[self.asic.chip][f'config_{chip}'] = self.asic.asic_config[f'config_{chip}']
        else:
            dicttofile[self.asic.chip]['config'] = self.asic.asic_config

        with open(f"{filename}", "w", encoding="utf-8") as stream:
            try:
                yaml.dump(dicttofile, stream, default_flow_style=False, sort_keys=False)

            except yaml.YAMLError as exc:
                logger.error(exc)
        
    """
##################### FW INTERFACING #########################
    # Method to enable timestamp and sample clocks, and configure SPI clock for the layers (if necessary)
    async def setup_clocks(self) -> None:
        # Enable TS and Sample clock
        await self.boardDriver.enableSensorClocks(flush = True)
        logger.info("Timestamp and SPI clocks enabled")

    async def enable_spi(self, spiFreq:int = 1000000) -> None :
        """
        Sets the Clocks divider for the SPI clock.
        Sets the clock to 1Mhz by default
        """
        # Set the SPI Clock to 1Mhz (the value must be passed in Hz)
        await self.boardDriver.configureLayerSPIFrequency(targetFrequencyHz = spiFreq , flush = True)
        logger.info(f"SPI clock set to {spiFreq}Hz ({spiFreq/1000000:.2f})MHz")

    async def asic_configure(self, layer:int):
        await self.asic_update(layer)

##################### ASIC METHODS FOR USERS #########################

    # Method to initalize the asic. This is taking the place of asic.py. 
    async def asic_init(self, yaml:str = None, rows:int = 1, chipsPerRow:int = 1):
        """
        self.asic_init() - initalize the asic configuration. Must be called first
        Positional arguments: None
        Optional:
        yaml:str - Name of yml file with configuration values
        rows:int - Number of SPI busses / ASIC objects to create
        chipsPerRow:int - Number of arrays per SPI bus, must all be equal
        analog_col: list[int] - Define layer, chip, col (in that order) of pixel to enable analog output (only one per row) 
        """

        # Now that the asic has been initalized we can go and make this true
        self._asic_start = True

        # Define YAML path variables
        pathdelim=os.path.sep #determine if Mac or Windows separators in path name
        ymlpath=os.getcwd()+pathdelim+"scripts"+pathdelim+"config"+pathdelim+yaml+".yml"

        #Get config values from YAML and set chip properties
        try:
            ## Init asic
            self.boardDriver.setupASICS(version = self.chipversion, rows = rows, chipsPerRow = chipsPerRow , configFile = ymlpath )
            ## Get asic for each row aka each daisy chain
            for r in range(rows):
                self.asics.append(self.boardDriver.getAsic(row = r-1))
        except Exception:
            logger.error('Must pass a configuration file in the form of *.yml')
            sys.exit(1)

        # Test to see whether the yml file can be read
        try:
            self.asics[0].enable_pixel(0,0,0)
            self.asics[0].disable_pixel(0,0,0)
        except KeyError: #could not find expected dictionary in yml file
            logger.error(f"Configure file of unexpected form. Make sure proper entries (esp. config -> config_0) and try again")
            sys.exit(1)

    #Interface with asic.py 
    async def enable_pixel(self, layer:int, chip:int, row: int, col: int):
       self.asics[layer].enable_pixel(chip, col, row)

    # Set chip routing
    async def set_routing(self, layer):
            await self.boardDriver.setLayerConfig(layer = layer, reset = False , autoread = False, hold = True, disableMISO=True, chipSelect=True, flush = True)
            await self.boardDriver.getAsic(row = layer).writeSPIRoutingFrame()
            await self.boardDriver.layersDeselectSPI(flush=True)
            self._wait_progress(1)
            await self.boardDriver.layersSelectSPI(flush=True)

    async def buffer_flush(self, layer):
        #Flush data from sensor
        logger.info("Flush chip before data collection")
        status = await self.boardDriver.rfg.read_layer_0_status() ## DAN - need to make the hardcoded 'layer_0' dynamic?
        interruptn = status & 0x1
        while interruptn == 0:
            logger.info("interrupt low")
            await self.boardDriver.writeLayerBytes(layer = layer, bytes = [0x00] * 128, flush=True)
            nmbBytes = await self.boardDriver.readoutGetBufferSize()
            if nmbBytes > 0:
                    await self.boardDriver.readoutReadBytes(1024)
            status = await self.boardDriver.rfg.read_layer_0_status()
            interruptn = status & 0x1 
        logger.info("interrupt recovered, ready to collect data")


    # The method to write data to the asic. 
    async def asic_update(self, layer):
        """This method resets the chip then writes the configuration"""
        await self.boardDriver.resetLayer(layer = layer )
        await self.set_routing(layer)
        if self.SR:
            try:
                await self.boardDriver.getAsic(row = layer).writeConfigSR()
                await self.boardDriver.layersDeselectSPI(flush=True)
            except OverflowError:
                logger.error(f"Tried to configure an array that is not connected! Code thinks there should be {self.asics[layer].num_chips} chips. Check chipsPerRow from asic_init")
                sys.exit(1)
        else:     
            try:
                #disable MISO line to ensure all config is written, enable chip select
                for chip in range(self.asics[layer].num_chips):
                    await self.boardDriver.getAsic(row = layer).writeConfigSPI(targetChip=chip)
                    await self.boardDriver.layersDeselectSPI(flush=True)
                    await self.boardDriver.layersSelectSPI(flush=True)
                await self.boardDriver.layersDeselectSPI(flush=True)
            except OverflowError:
                logger.error("Tried to configure an array that is not connected! Check chipsPerRow from asic_init")
                sys.exit(1)    
        await self.buffer_flush(layer)


    # Methods to update the internal variables. Please don't do it manually
    # This updates the dac config
    async def update_asic_config(self, layer:int, chip:int, bias_cfg:dict = None, idac_cfg:dict = None, vdac_cfg:dict = None):
        #Updates and writes confgbits to asic
        #layer, chip indicate which layer and chip in the daisy chain to update
        #bias_cfg:dict - Updates the bias settings. Only needs key/value pairs which need updated
        #idac_cfg:dict - Updates iDAC settings. Only needs key/value pairs which need updated
        #vdac_cfg:dict - Updates vDAC settings. Only needs key/value pairs which need updated
        
        if self._asic_start:
            if bias_cfg is not None:
                for key in bias_cfg:
                    self.asics[layer].asic_config[f'config_{chip}']['biasconfig'][key][1]=bias_cfg[key]
            if idac_cfg is not None:
                for key in idac_cfg:
                    self.asics[layer].asic_config[f'config_{chip}']['idacs'][key][1]=idac_cfg[key]
            if vdac_cfg is not None:
                for key in vdac_cfg:
                    self.asics[layer].asic_config[f'config_{chip}']['vdacs'][key][1]=vdac_cfg[key]
            else: 
                logger.info("update_asic_config() got no arguments, nothing to do.")
                return None
        else: raise RuntimeError("Asic has not been initalized")

    #enable pixels for injection. Must be called once per pixel
    async def enable_injection(self, layer:int, chip:int, row: int, col: int):
        try:
            self.asics[layer].enable_inj_col(chip, col, inplace=False)
            self.asics[layer].enable_inj_row(chip, row, inplace=False)
        except (IndexError, KeyError):
            logger.error(f"Cannot enable injection in pixel layer {layer+1}, chip {chip}, row {row}, col {col}. Ensure layer, chip, and column values all passed. Layer counting begins at 1, not 0.")
            sys.exit(1)
        
    
    #enable pixels for analog readout. Must be called once per pixel
    async def enable_analog(self, layer:int, chip:int, col: int):
        try:
            #Enable analog pixel from given chip in the daisy chain
            logger.info(f"enabling analog output in column {col} of chip {chip} in layer {layer+1}")
            self.asics[layer].enable_ampout_col(chip, col, inplace=False)
        except (IndexError, KeyError):
            logger.error(f"Cannot enable analog pixel - chip does not exist. Ensure layer, chip, and column values all passed. Layer counting begins at 1, not 0.")
            sys.exit(1)
        

    #close connection with FPGA
    def close_connection(self) -> None :
        """
        Closes the FPGA board driver connection
        This is optional, connections are closed automatically upon script ending
        """
        self.boardDriver.close()


################## Voltageboard Methods ############################
    #convert a voltage value to a DAC value
    def get_internal_vdac(self, v_in, v_ref:float = 1.8, nbits:float = 10):
        return int(v_in * 2**nbits / v_ref)
        
    #Change a pixel threshold value in the global dictionary of configs
    async def update_pixThreshold(self, layer:int, chip:int, vThresh:int): 
        #vThresh = comparator threshold provided in mV
        dacThresh = self.get_internal_vdac(vThresh/1000.) #convert from mV to V
        dacBL = self.asics[layer].asic_config[f'config_{chip}']['vdacs']['blpix'][1]
        await self.update_asic_config(layer, chip, vdac_cfg={'thpix':dacBL+dacThresh})

    #initialize voltages with GECCO HW (voltagecard)
    async def init_voltages(self, vcal:float = .989, vsupply: float = 2.7, vthreshold:float = None, dacvals: tuple[int, list[float]] = None):
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
        if not self._geccoBoard:
            logger.error("No GECCO board configured, so a voltageboard cannot be configured. Check FPGA settings.")
            raise RuntimeError("No GECCO board configured, so a voltageboard cannot be configured. Check FPGA settings.")

        # From nicholas's beam_test.py:
        # 1=thpmos (comparator threshold voltage), 3 = Vcasc2, 4=BL, 7=Vminuspix, 8=Thpix 
        if self.chipversion == 2:
            default_vdac = (8, [0, 0, 1.1, 1, 0, 0, 1, 1.100])
        else: #increase thpmos for v3 pmos pixels
            default_vdac = (8, [1.1, 0, 1.1, 1, 0, 0, 1, 1.100])

        # used to ensure this has been called in the right order:
        self._voltages_exist = True

        # Set dacvals
        if dacvals is None:
            dacvals = default_vdac
            # dacvals takes precidence over vthreshold
            if vthreshold is not None:
                # Turns from mV to V with the 1V offset normally present
                vthreshold = (vthreshold/1000) + default_vdac[1][3]
                if vthreshold > 1.5 or vthreshold < 0:
                    logger.warning("Threshold voltage out of range of sensor!")
                    if vthreshold <= 0: 
                        vthreshold = 1.100
                        logger.error("Threshold value too low, setting to default 100mV")
                dacvals[1][-1] = vthreshold

        # Voltage Board is provided by the board Driver
        self.vboard = self.boardDriver.geccoGetVoltageBoard()
        self.vboard.dacvalues = dacvals
        # Set calibrated values
        self.vboard.vcal = vcal
        self.vboard.vsupply = vsupply

        # Send config to the chip
        await self.vboard.update()

    # Setup Injections with GECCO HW (injection card)
    async def init_injection(self, layer:int, chip:int, inj_voltage:float = None, inj_period:int = 100, clkdiv:int = 300, initdelay: int = 100, cycle: float = 0, pulseperset: int = 1, dac_config:tuple[int, list[float]] = None, onchip:bool = True):
        """
        Configure injections
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
        dac_config:tuple[int, list[float]]: injdac settings. Must be fully specified if set. 
        onchip: bool (generate signal on chip or on GECCO card)
        """

        """
        # Check the required HW is available
        if not self._geccoBoard:
            logger.error("No GECCO board configured, so an injectionboard cannot be configured. Check FPGA settings.")
            raise   

        if (inj_voltage is not None) and (dac_config is None):
            # elifs check to ensure we are not injecting a negative value because we don't have that ability
            if inj_voltage < 0:
                raise ValueError("Cannot inject a negative voltage!")
            elif inj_voltage > 800:
                logger.warning("Cannot inject more than 800mV, will use defaults")
                inj_voltage = 300 #Sets to 300 mV     
        """

        if inj_voltage:
            #Update vdac value from yml 
            await self.update_asic_config(layer, chip, vdac_cfg={'vinj':self.get_internal_vdac(inj_voltage/1000.)})

        #self._geccoBoard = False
        #print("INJ_WDATA BEFORE CONF")
        #print(await self.boardDriver.rfg.read_layers_inj_wdata(1024))

        if self._geccoBoard:
            # Injection Board is provided by the board Driver
            # The Injection Board provides an underlying Voltage Board
            self.injector = self.boardDriver.geccoGetInjectionBoard()
            if not onchip:
                await self.boardDriver.ioSetInjectionToGeccoInjBoard(enable = True, flush = True)
                self.injectorBoard = self.injector.vBoard
                self.injectorBoard.dacvalues = (8, [inj_voltage/1000.,0.0]) #defaults from Nicolas
                self.injectorBoard.vcal = self.vboard.vcal
                self.injectorBoard.vsupply = self.vboard.vsupply
                await self.injectorBoard.update()
            else:
                await self.boardDriver.ioSetInjectionToGeccoInjBoard(enable = False, flush = True)

            self.injector.period = inj_period
            self.injector.clkdiv = clkdiv
            self.injector.initdelay = initdelay
            self.injector.cycle = cycle
            self.injector.pulsesperset = pulseperset 
        else:
            #Injection provided through integrated features on chip
            print("SET INJ WITH REGISTERS")
            await self.boardDriver.ioSetInjectionToGeccoInjBoard(enable = False, flush = True)


    #update injection settings via injectionboard after object is already created
    async def update_injection(self, layer:int, chip:int, inj_voltage:float = None, inj_period:int = None, clkdiv:int = None, initdelay: int = None, cycle: float = None, pulseperset: int = None):
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
                inj_voltage = 300 #Sets to 300 mV

        if inj_voltage:
            #Update vdac value from yml 
            await self.update_asic_config(layer, chip, vdac_cfg={'vinj':self.get_internal_vdac(inj_voltage/1000.)})

        if inj_period and inj_period!=self.injector.period:
            self.injector.period = inj_period
        if clkdiv and clkdiv!=self.injector.clkdiv:
            self.injector.clkdiv = clkdiv
        if initdelay and initdelay!=self.injector.initdelay:
            self.injector.initdelay = initdelay
        if cycle and cycle!=self.injector.cycle:
            self.injector.cycle = cycle
        if pulseperset and pulseperset!=self.injector.pulseperset:
            self.injector.pulseperset = pulseperset
        

    # Start injection
    async def start_injection(self):
        """
        Starts Injection.
        Takes no arguments and no return
        """
        # Check the required HW is available
        if self._geccoBoard:
            await self.injector.start()
            #print("INJ_WDATA AFTER START")
            #print(await self.boardDriver.rfg.read_layers_inj_wdata(1024))
        else:
            print("STARTING WITH REGISTERS") 
            ## DAN - unfinished beginning of controlling injection with registers instead of injection card. Necessary for CMOD and parallel in 'stop_injection' method
            layers_inj_val = await self.boardDriver.rfg.read_layers_inj_ctrl()
            if layers_inj_val>0: #injection not running
                await self.boardDriver.rfg.write_layers_inj_ctrl(0b0)
                await self.boardDriver.rfg.write_layers_inj_ctrl(0b1)
                await self.boardDriver.rfg.write_layers_inj_ctrl(0b0)
        logger.info("Began injection")

    # Stop injection
    async def stop_injection(self):
        """
        Stops Injection.
        Takes no arguments and no return
        """
        # Check the required HW is available
        if self._geccoBoard:
            await self.injector.stop()
        else:
            print("STOPPING WITH REGISTERS")
            layers_inj_val = await self.boardDriver.rfg.read_layers_inj_ctrl()
            if layers_inj_val==0: #injection running
                await self.boardDriver.rfg.write_layers_inj_ctrl(3)

        logger.info("Stopped injection")


########################### Input and Output #############################

    #Returns header for use in a log file with all settings.
    #Get config dictionaries from yaml
    def get_log_header(self, layer:int,chip:int):

        vdac_str=""
        digitalconfig = {}
        for key in self.asics[layer].asic_config[f'config_{chip}']['digitalconfig']:
                digitalconfig[key]=self.asics[layer].asic_config[f'config_{chip}']['digitalconfig'][key][1]
        biasconfig = {}
        for key in self.asics[layer].asic_config[f'config_{chip}']['biasconfig']:
                biasconfig[key]=self.asics[layer].asic_config[f'config_{chip}']['biasconfig'][key][1]
        idacconfig = {}
        for key in self.asics[layer].asic_config[f'config_{chip}']['idacs']:
                idacconfig[key]=self.asics[layer].asic_config[f'config_{chip}']['idacs'][key][1]
        if self.chipversion>2:
            vdacconfig = {}
            for key in self.asics[layer].asic_config[f'config_{chip}']['vdacs']:
                    vdacconfig[key]=self.asics[layer].asic_config[f'config_{chip}']['vdacs'][key][1]
            vdac_str=f"vDAC: {vdacconfig}\n"
        arrayconfig = {}
        for key in self.asics[layer].asic_config[f'config_{chip}']['recconfig']:
                arrayconfig[key]=self.asics[layer].asic_config[f'config_{chip}']['recconfig'][key][1]

        # This is not a nice line, but its the most efficent way to get all the values in the same place.
        return f"Digital: {digitalconfig}\n" +f"Biasblock: {biasconfig}\n" + f"iDAC: {idacconfig}\n"+ vdac_str + f"Receiver: {arrayconfig}" 


############################ Data Collection / Processing ##############################
    #Properly set up layer config for data collection
    async def setup_readout(self, layer:int, autoread:int = 1):
        #Take take layer out of reset and hold
        await self.boardDriver.setLayerConfig(layer = layer , reset = False , autoread  = autoread, hold=False, flush = True )
   
   #Read FPGA buffer and return buffer length and data stored within it
    async def get_readout(self, counts:int = 4096):
        bufferSize = await(self.boardDriver.readoutGetBufferSize())
        readout = await(self.boardDriver.readoutReadBytes(counts))
        return bufferSize, readout
   
   #Print status register
    async def print_status_reg(self):
        status = await(self.boardDriver.rfg.read_layer_0_status())
        ctrl = await(self.boardDriver.rfg.read_layer_0_cfg_ctrl())
        print(f"Layer Status:  {hex(status)},interruptn={status & 0x1},decoding={(status >> 1) & 0x1},reset={(ctrl>>1) & 0x1},hold={(ctrl) & 0x1},buffer={await (self.boardDriver.readoutGetBufferSize())}")
        #logger.info(f"Layer Status:  {hex(status)},interruptn={status & 0x1},decoding={(status >> 1) & 0x1},reset={(ctrl>>1) & 0x1},hold={(ctrl) & 0x1},buffer={await (self.boardDriver.readoutGetBufferSize())}")

    #Parse raw data readouts to remove railing. Moved to postprocessing method to avoid SW slowdown when using autoread
    async def dataParse_autoread(self, data, buffer_lst, bitfile:str = None):
        allData = b''
        for i, buff in enumerate(buffer_lst):
            if buff>0:
                readout_data = data[i][:buff]
                logger.info(binascii.hexlify(readout_data))
                allData+=readout_data
                if bitfile:
                    bitfile.write(f"{str(binascii.hexlify(readout_data))}\n")

        ## DAN - could also return buffer index to keep track of whether multiple hits occur in the same readout. Would need to propagate forward

        return allData

############################ Decoder ##############################
    #Send data for decoding from raw
    def decode_readout(self, readout:bytearray, i:int, printer: bool = True):
        return drivers.astropix.decode.decode_readout(self, logger, readout, i, printer)

    ################## Housekeeping ############################
    async def every(__seconds: float, func, *args, **kwargs):
        #scheduler
        while True:
            func(*args, **kwargs)
            await asyncio.sleep(__seconds)
        
    async def callHK(self, flipped:bool = True): # adding a setting that can change the byte ordering in the future if we ever fix/change this
        """
        Calls housekeeping from TI ADC128S102 ADC. Loops over each of the 8 input channels.
        Input is two bytes:
        First 2 bits: ignored
        Next 3 bits: Set Channel #
        Last 11 bits: ignored

        Shift register input style requires bytes to be read in left to right. May be fixed in future versions
        """

        await driver.houseKeeping.selectADC()
        
        ## Loop over ADC Settings
        for chan in range(0,8):
            bits = format(chan,'08b')
            if flipped == True:
                byte1 = int(bits[::-1],2) #this is a hex string is this ok?
            else:
                byte1 = int(bits,2) #this is a hex string is this ok?

            await driver.houseKeeping.writeADCDACBytes([byte1,0x00])
            adcBytesCount = await driver.houseKeeping.getADCBytesCount()
            adcBytes = await driver.houseKeeping.readADCBytes(adcBytesCount) #still need to output this from task
            print(f"Got ADC bytes {adcBytes}")
        

###################### INTERNAL METHODS ###########################

# Below here are internal methods used for constructing things and testing

    # _test_io(): A function to read and write a register on the chip to see if 
    # everything is working. 
    # It takes no arguments 
    async def _test_io(self):
        """Reads a register to check a write and readback to the firmware is working"""
        try:    # Attempts to write to and read from a register
            ## Try to read the firmware ID and or Version
            await self.boardDriver.readFirmwareID()
            #self.nexys.write_register(0x09, 0x55, True)
            #self.nexys.read_register(0x09)
            #self.nexys.spi_reset()
            #self.nexys.sr_readback_reset()
        except Exception: 
            raise RuntimeError("Could not read or write from astropix!")

    # progress bar 
    def _wait_progress(self, seconds:int):
        for _ in tqdm(range(seconds), desc=f'Wait {seconds} s'):
            time.sleep(1)

    #Check of general functionality esp of SPI lines, as inspired from documentation
    async def functionalityCheck(self, holdBool:bool = True):
        #Take take layer out of reset but keep in hold
        await self.boardDriver.setLayerConfig(layer = 0 , reset = False , hold = holdBool, autoread = False , flush = True)

        # Write 16 NULL bytes to the sensor
        await self.boardDriver.writeBytesToLayer(layer = 0 , bytes = [0x00]*16)

        # Reads the Idle counter  register for the layer 0
        idleCount = await self.boardDriver.rfg.read_layer_0_stat_idle_counter()
        print(f"Actual IDLE counter: {idleCount}")

        # Reads the Frame Counter register for the layer 0 
        framesCount = await self.boardDriver.rfg.read_layer_0_stat_frame_counter()
        print(f"Actual Frame counter: {framesCount}")

    #Print values of registers associated with enable/disable injection
    async def checkInjBits(self):
        io_ctrl_val = await self.boardDriver.rfg.read_io_ctrl()
        print(f"io_ctrl value = {io_ctrl_val} = {bin(io_ctrl_val)}")

        layers_inj_val = await self.boardDriver.rfg.read_layers_inj_ctrl()
        print(f"layers_inj value = {layers_inj_val} = {bin(layers_inj_val)}")
