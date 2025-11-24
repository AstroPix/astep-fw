import asyncio
import logging
import math
import time

import rfg.core
import rfg.io
from bitstring import BitArray
from bitstring import Array
from deprecated import deprecated

 



import drivers.astep.housekeeping
from drivers.astropix.asic import Asic
from drivers.astropix.loopback_model import Astropix3LBModel

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def debug():
    logger.setLevel(logging.DEBUG)


class BoardDriver:
    def __init__(self, rfg):
        self.rfg = rfg
        self.houseKeeping = drivers.astep.housekeeping.Housekeeping(self, rfg)
        self.asics = {}

        ## By default the FW is reset with 32 bits
        self.fpgaTimeStampBytesCount = 4

        # Synchronisation Utils
        ########

        ## Opened Event -> Set/unset by close/open
        ## Useful to start or stop tasks dependent on open/close state of the driver
        self.openedEvent = asyncio.Event()
        
        
    async def utilWaitSeconds(self,wait:int):
        """This method can be override for example in simulation to wait using proper mechanism"""
        await asyncio.sleep(wait)

    async def open(self):
        """Open the Register File I/O Connection to the underlying driver"""
        await self.rfg.io.open()
        self.openedEvent.set()

    async def close(self):
        """Close the Register File I/O Connection to the underlying driver"""
        self.openedEvent.clear()
        await self.rfg.io.close()

    async def waitOpened(self):
        await self.openedEvent.wait()

    def isOpened(self) -> bool:
        return self.openedEvent.is_set()

    def debug_full(self):
        rfg.core.debug()

    def flush(self):
        """Flushed the RFG instance, use to be sure no bytes are pending writting"""
        self.rfg.flush()

    async def readFirmwareVersion(self):
        """Returns the raw integer with the firmware Version"""
        return await self.rfg.read_hk_firmware_version()

    async def readFirmwareID(self):
        """Returns the raw integer with the firmware id"""
        return await self.rfg.read_hk_firmware_id()

    async def readFirmwareIDName(self):
        """"""
        boards = {
            0xAB02: "Nexys GECCO Astropix v2",
            0xAB03: "Nexys GECCO Astropix v3",
            0xAC03: "CMOD Astropix v3",
        }
        boardID = await self.readFirmwareID()
        return boards.get(boardID, "Firmware ID unknown: {0}".format(hex(boardID)))

    async def checkFirmwareVersionAfter(self, v):
        return await self.readFirmwareVersion() >= v

    def getFPGACoreFrequency(self):
        """Returns the Core Clock frequency to help clock divider configuration - this method is overriden by implementation class (Gecco or Cmod)"""
        return 80000000


    ## Clock and IO enablement
    # #################
    async def enableSensorClocks(self, flush: bool = False):
        """Writes the I/O Control register to enable both Timestamp and Sample clock outputs"""
        await self.setSampleClock(enable=True, flush=flush)
        await self.setTimestampClock(enable=True, flush=flush)
        
    async def setExternalClock(self,enable:bool,ext_clock_is_differential:bool=True, waitForClockChange:bool = True ):
        """If enable is True, allow the external clock to be used. If the FW switches to external clock ,a reset happends, this method will warn the user"""

        # First Read current state
        # If external clock requested and already selected, emit a warning 
        #
        currentClockCtrl1 = await self.rfg.read_clock_ctrl()
        if ext_clock_is_differential is True:
            currentClockCtrl1 |= 0x2 
        else 
            currentClockCtrl1 &= ~(0x2)
            
        currentClockIsExternal = (currentClockCtrl1>>2) & 0x1 == 1 
        
        if enable is True and not currentClockIsExternal:
            logger.warning("Enabling external clock - do this before any configuration, the FW will reset upon clock switching - make sure the external clock is running")
            
            await self.rfg.write_clock_ctrl((currentClockCtrl1 | (1)),flush=True)
            
            # Now wait a bit and check if the selected clock changed
            if waitForClockChange:
                await self.utilWaitSeconds(1)
                
            # Read the register again
            currentClockCtrl2 = await self.rfg.read_clock_ctrl()
            currentClockIsExternal = (currentClockCtrl2>>2) & 0x1 == 1 
            
            if (not currentClockIsExternal):
                logger.warning("After enabling external clock, the FW didn't switch - maybe the clock is not running - disabling external clock now to avoid switch over and reset at an unpredictable time")
                await self.rfg.write_clock_ctrl(currentClockCtrl1,flush=True)
                return False
            else: 
                logger.warning("FW Switched to external clock - a reset was issued, you can now configure the system and run measurements")
                return True 
        elif enable is True and currentClockIsExternal:
            logger.warning("Not Enabling External Clock, FW is already running on the external clock")
            return False
        else:
            logger.warning("Disabling external clock")
            if currentClockIsExternal:
                logger.warning("- FW is running on the external clock, it will switch back to board clock only when the external clock is removed or a full reset is issued")
            
            await self.rfg.write_clock_ctrl(currentClockCtrl1 & ~(1<<2),flush=True)
            
            return True
        
        # Read the status register
        
    async def getIOControlRegister(self):
        return await self.rfg.read_io_ctrl()

    async def setSampleClock(self, enable: bool, flush: bool = False):
        v = await self.rfg.read_io_ctrl()
        if enable:
            v |= 0x1
        else:
            v &= ~(0x1)
        await self.rfg.write_io_ctrl(v, flush)

    async def setTimestampClock(self, enable: bool, flush: bool = True):
        v = await self.rfg.read_io_ctrl()
        if enable:
            v |= 0x2
        else:
            v &= ~(0x2)
        await self.rfg.write_io_ctrl(v, flush)

    async def ioSetSampleClockSingleEnded(self, enable: bool, flush: bool = True):
        v = await self.rfg.read_io_ctrl()
        if enable:
            v |= 0x4
        else:
            v &= ~(0x4)
        await self.rfg.write_io_ctrl(v, flush)

    async def ioSetInjectionToChip(self,enable:bool = True,flush:bool = True):
        v = await self.rfg.read_io_ctrl()
        if enable: v &= ~(0x8)
        else: v |= 0x8
        await self.rfg.write_io_ctrl(v,flush) 

    async def ioSetFPGAExternalTSClockDifferential(
        self, enable: bool, flush: bool = False
    ):
        """If an external clock input is used for the FPGA TS counter, it is differential or not"""
        v = await self.rfg.read_io_ctrl()
        if enable:
            v |= 0x10
        else:
            v &= ~(0x10)
        await self.rfg.write_io_ctrl(v, flush)

    async def ioSetAstropixTSToFPGATS(self, enable: bool, flush: bool = False):
        """The Astropix TS clock can be sourced from the external FPGA TS clock (it true) or from the internal TS clock (if false)"""
        v = await self.rfg.read_io_ctrl()
        if enable:
            v |= 0x20
        else:
            v &= ~(0x20)
        await self.rfg.write_io_ctrl(v, flush)
        
    ## Loopback Model
    ################
    def getLoopbackModelForLayer(self, layer):
        return Astropix3LBModel(self, layer)

    ## Chips config
    ################
    def setupASICS(
        self,
        version: int,
        lanes: int = 1,
        chipsPerLane: int = 1,
        configFile: str | None = None,
    ):
        """Configure one or multiple lanes with a single config file

        Args:
            version: int, AstroPix chip version
            lanes: int, number of lanes, default=1
            chipsPerLane: int, number of chips per row (aka daisy chain), default=1
            configFile: srt, path to yaml config file, defaults to None (no configuration applied?)
        """
        assert version >= 2 and version < 4, "Only Astropix 2,3 and 4 Supported"

        # OLD -> init of gecco voltage board for v2 -> this is one somewhere else here
        # if version == 2:
        #    self.geccoGetVoltageBoard().dacvalues = (8, [0, 0, 1.1, 1, 0, 0, 1, 1.100])

        for i in range(lanes):
            self.setupASIC(
                version, lane=i, chipsPerLane=chipsPerLane, configFile=configFile
            )

    def setupASIC(
        self,
        version: int,
        lane: int = 0,
        chipsPerLane: int = 1,
        configFile: str | None = None,
    ):
        """Configures one lane (aka daisy chain) with a single config file
        This method creates the asic model or updates the existing one if this method is called multiple times

        Args:
            version: int, AstroPix chip version
            lanes: int, number of the current row, default=0
            chipsPerLane: int, number of chips per row (aka daisy chain), default=1
            configFile: srt, path to yaml config file, defaults to None (no configuration applied?)
        """

        ## Get ASIC or create it
        asic = self.asics.setdefault(
            lane, Asic(chipversion=version, nchips=chipsPerLane)
        )
        asic.num_chips = chipsPerLane

        if configFile is not None:
            asic.load_conf_from_yaml(configFile)

    def getAsic(self, lane=0):
        """Returns the Asic Model for the Given Row - Other chips in the Daisy Chain are handeled by the returned 'front' model"""
        return self.asics[lane]

    async def writeRoutingFrame(self, lane: int = 0, firstChipID: int = 0):
        spiBytes = self.getAsic(lane).getRoutingFrame(
            firstChipID=firstChipID,
            paddingBytes=((self.asics[lane].num_chips - 1) * 2 + 2),
        )

        await self.writeSPIBytesToLane(lane=lane, bytes=spiBytes)

    async def writeSRAsicConfig(self, lane: int = 0, ckdiv=8, limit: int | None = None):
        """
        Write ASIC Config via Shift Register - This method must write configuration for at least all the chips until the target chip
        In this first new version, it will always write configuration for all the Chips.

            Args:
                ckdiv(int) : Repeats the write for ck1/ck2/load ckdiv times to strech the signal. Set this value higher for faster software interface
                limit(int) : Only write limit bits to SR - Mostly useful in simulation to limit runtime which checking the I/O are correctly driven

        """

        ## Generate Bit vector for config
        ## If limit is used, retain only a few bits from the resuklt
        bits = self.getAsic(lane).getConfigBits(msbfirst=False,limit=limit)
        

        logger.info("Writing SR Config for row=%d,len=%d", lane, len(bits))

        ## Save target register for the write here - this can be easily updated in case some hardware platforms have different names for registers
        targetRegister = self.rfg.Registers["LAYERS_SR_OUT"]

        ## Write to SR using register
        sinValue = 0
        for bit in bits:
            # SIN (bit 3 in register)
            sinValue = (1 if bit else 0) << 2
            self.rfg.addWrite(
                register=targetRegister, value=sinValue, repeat=ckdiv
            )  # ensure SIN has higher delay than CLK1 to avoid setup violation / incorrect sampling

            # CK1
            self.rfg.addWrite(
                register=targetRegister, value=sinValue | 0x1, repeat=ckdiv
            )
            self.rfg.addWrite(register=targetRegister, value=sinValue, repeat=ckdiv)

            # CK2
            self.rfg.addWrite(
                register=targetRegister, value=sinValue | 0x2, repeat=ckdiv
            )
            self.rfg.addWrite(register=targetRegister, value=sinValue, repeat=ckdiv)

        ## Set Load (loads start bit 4) for the correct lane
        self.rfg.addWrite(
            register=targetRegister, value=sinValue | (0x1 << (lane + 3)), repeat=ckdiv
        )
        self.rfg.addWrite(register=targetRegister, value=0, repeat=ckdiv)

        await self.rfg.flush()

    async def writeSPIAsicConfig(
        self,
        lane: int,
        load: bool = True,
        n_load: int = 10,
        broadcast: bool = False,
        targetChip: int = 0,
        config: BitArray | None = None,
    ):
        # Get SPI Frame Configs
        spiBytes = self.getAsic(lane).getSPIConfigFrame(
            load=load,
            n_load=n_load,
            broadcast=broadcast,
            targetChip=targetChip,
            config=config,
        )

        # Write all configs
        # Write to layer
        await self.writeSPIBytesToLane(lane, spiBytes)
        
        
    async def writeSRReadback(self, lane: int = 0, ckdiv=8, limit: int | None = None):
        """
        This method drivers the Config SR Readback by: 
            - setting RB to 1, then CK1/CK2 toggling once 
            - RB back to 0, then enale the readback CRC module
            - Write hte config with SIN always 0, no load and the number of bits left padded to a full byte

            Args:
                ckdiv(int) : Repeats the write for ck1/ck2/load ckdiv times to strech the signal. Set this value higher for faster software interface
                limit(int) : Only write limit bits to SR - Mostly useful in simulation to limit runtime which checking the I/O are correctly driven

        """

        ## Generate Bit vector for config
        ## If limit is used, retain only a few bits from the resuklt
        bits = self.getAsic(lane).getConfigBits(msbfirst=False)
        

        logger.info("Reading SR Config for lane=%d,len=%d", lane, len(bits))

        ## Save target register for the write here - this can be easily updated in case some hardware platforms have different names for registers
        targetRegister = self.rfg.Registers["LAYERS_SR_OUT"]
        targetInRegister = self.rfg.Registers["LAYERS_SR_IN"]
        targetRBControlRegister = self.rfg.Registers["LAYERS_SR_RB_CTRL"]
        
        ## Set Readback
        # #############
        
        # RB=1
        self.rfg.addWrite(register=targetRBControlRegister, value=0x1, repeat=ckdiv )  
        
        # CK1
        self.rfg.addWrite( register=targetRegister, value=0x1, repeat=ckdiv )
        self.rfg.addWrite(register=targetRegister, value=0, repeat=ckdiv)

        # CK2
        self.rfg.addWrite( register=targetRegister, value= 0x2, repeat=ckdiv )
        self.rfg.addWrite(register=targetRegister, value=0, repeat=ckdiv)
        
        # RB=0 and CRC enable and SOUT selection based on Lane input parameter
        self.rfg.addWrite(register=targetRBControlRegister, value=0x2 | ((lane <<2) & 0x1F), repeat=ckdiv ) 
        
        await self.rfg.flush()
        
        ## Write Config 
        #bitsPaddedLen = bits + [0x00] * (8- (len(bits)%8))
        bitsPaddedLen = len(bits) +  (8- (len(bits)%8))
        logger.debug(f"Padded bits to len={bitsPaddedLen},bytes={bitsPaddedLen/8.0}")
        
        ## Write to SR using register
        sinValue = 0
        for i in range(bitsPaddedLen):
            

            # CK1
            self.rfg.addWrite(
                register=targetRegister, value=sinValue | 0x1, repeat=ckdiv
            )
            self.rfg.addWrite(register=targetRegister, value=sinValue, repeat=ckdiv)

            # CK2
            self.rfg.addWrite(
                register=targetRegister, value=sinValue | 0x2, repeat=ckdiv
            )
            self.rfg.addWrite(register=targetRegister, value=sinValue, repeat=ckdiv)


        await self.rfg.flush()
        
        
        # RB=0 and CRC disable
        self.rfg.addWrite(register=targetRBControlRegister, value=0, repeat=ckdiv ) 
        await self.rfg.flush()
        
        ## Now Read CRC and number of bytes available 
        return await self.rfg.read_layers_sr_crc()
        
    async def readSRReadbackBytes(self,len:int ):
        """Returns the bytes from FIFO containing the SR config bits read back via CRC module.
        Pass to len argument the lenght returned by writeSRReadback"""
        
        return await self.rfg.read_layers_sr_bytes_raw(len)
        
    async def readSRReadbackBits(self,lane:int, targetChip=-1):
        """Returns the read back bits as a bit string in correct order with the number of padding bits stripped ,and the same bits as expected"""
        
        ## Get the bits in bytes
        bitsAsBytes = await self.readSRReadbackBytes(await self.rfg.read_layers_sr_bytes_read_size())
        
        ## Get the Number of config bits
        # 
        expectedBits = self.getAsic(lane).getConfigBits(msbfirst=True,targetChip=targetChip) # MsbFirst here is used to get the bits in real order, not order to be send to chip
        bitsPaddedLen =  (8- (len(expectedBits)%8))
        
        
        ## Pack the read bits in bitstring array, reverse then return sliced removing the first x bits which are padding for byte
        a = Array('uint8', bitsAsBytes)
        a.data.reverse() 
        
        readBackBits = a.data[bitsPaddedLen:]
        
        logger.info(f"SR Readback, expectedBits={len(expectedBits)},paddingLength={bitsPaddedLen},number of bytes={len(bitsAsBytes)},result bits={len(readBackBits)}")
        
        return (readBackBits,expectedBits)
        
    

    ## Clock Dividers
    ####################
    
        
    def calculateClockDivider(self, targetFrequencyHz: int) -> int:
        """Calculates the SPI Divider for a target frequency, valid for both Astropix Lane and Housekeeping dividers"""
        coreFrequency = self.getFPGACoreFrequency()
        divider = int((coreFrequency / 2) / ( 2 * targetFrequencyHz)) -1
        assert divider >= 0 and divider <= 255, (
            f"Divider {divider} is not allowed, frequency {targetFrequencyHz} is wrnog, min. clock frequency: {int(coreFrequency / 2 / 255)}"
        )
        return divider
        
        
    def calculateMatchClockDivider(self, targetFrequencyHz: int) -> int:
        """Calculates the SPI Divider for a target frequency, valid for both Astropix Lane and Housekeeping dividers"""
        coreFrequency = self.getFPGACoreFrequency()
        divider = int(coreFrequency / ( targetFrequencyHz))
        assert divider > 0 and divider <= pow(2,32)-1, (
            f"Divider {divider} is not allowed, frequency {targetFrequencyHz} is wrnog, min. clock frequency: {int(coreFrequency / 2 / 255)}"
        )
        return divider

    async def configureLayerSPIFrequency(self, targetFrequencyHz: int, flush=True):
        """Calculated required divider to reach the provided target SPI clock frequency"""
        await self.configureLayerSPIDivider(
            self.calculateClockDivider(targetFrequencyHz), flush
        )

    async def configureLayerSPIDivider(self, divider: int, flush=True):
        await self.rfg.write_spi_layers_ckdivider(divider, flush)

    async def configureHKSPIFrequency(self, targetFrequencyHz: int, flush=True):
        """Calculated required divider to reach the provided target SPI clock frequency"""
        await self.configureHKSPIDivider(
            self.calculateClockDivider(targetFrequencyHz), flush
        )

    async def configureHKSPIDivider(self, divider: int, flush=True):
        await self.rfg.spi_hk_ckdivider(divider, flush)

    ## Layers
    ##################

    # async def layerSelectSPI(self, layer , cs : bool, flush = False):
    #     """This helper method asserts the shared CSN to 0 by selecting CS on layer 0
    #     it's a helper to be used only if the hardware uses a shared Chip Select!!
    #     If any Layer is in autoread mode, chip select will be already asserted
    #     """
    #     layerCfg = await getattr(self.rfg, f"read_layer_{layer}_cfg_ctrl")()
    #     layerCfg = (layerCfg | (1 << 3)) if cs else (layerCfg & ~(1 << 3))
    #     await getattr(self.rfg, f"write_layer_{layer}_cfg_ctrl")(layerCfg,flush)

    async def layersSetSPICSN(self, cs=False, flush=False):
        """This helper method asserts the shared CSN to 0 by selecting CS on layer 0
        it's a helper to be used only if the hardware uses a shared Chip Select!!
        If any Layer is in autoread mode, chip select will be already asserted
        """
        layer0Cfg = await self.rfg.read_layer_0_cfg_ctrl()
        if cs:
            layer0Cfg = layer0Cfg | (1 << 3)
        else:
            layer0Cfg = layer0Cfg & ~(1 << 3)

        await self.rfg.write_layer_0_cfg_ctrl(layer0Cfg, flush)

    async def layersSelectSPI(self, flush=False):
        """This helper method asserts the shared CSN to 0 by selecting CS on layer 0
        it's a helper to be used only if the hardware uses a shared Chip Select!!
        If any Layer is in autoread mode, chip select will be already asserted
        """
        layer0Cfg = await self.rfg.read_layer_0_cfg_ctrl()
        layer0Cfg = layer0Cfg | (1 << 3)
        await self.rfg.write_layer_0_cfg_ctrl(layer0Cfg, flush)

    async def layersDeselectSPI(self, flush=True):
        """This helper method deasserts the shared CSN to 1 by deselecting CS on layer 0
        it's a helper to be used only if the hardware uses a shared Chip Select!!
        If any Layer is in autoread mode, chip select will stay asserted
        """
        layer0Cfg = await self.rfg.read_layer_0_cfg_ctrl()
        layer0Cfg = layer0Cfg & ~(1 << 3)
        await self.rfg.write_layer_0_cfg_ctrl(layer0Cfg, flush)

    # async def resetLayer(self, layer : int , waitTime : float = 0.5 ):
    #     """Sets Layer in Reset then Remove reset after a wait time. The registers are written right now.

    #     Args:
    #         layer (int): layer to reset
    #         waitTime (float):  Reset duration - Default 0.5s
    #     """
    #     #await self.setLayerReset(layer = layer, reset = True , flush = True )
    #     await self.setLayerConfig(layer=layer, reset=True, autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)
    #     await asyncio.sleep(waitTime)
    #     #await self.setLayerReset(layer = layer, reset = False , flush = True )
    #     await self.setLayerConfig(layer=layer, reset=False, autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)

    async def resetLayers(self, waitTime: float = 0.5, flush=True):
        """Reset all layers because the reset line is shared.

        Args:
            waitTime (float):  Reset duration - Default 0.5s
        """
        layer0Cfg = await self.rfg.read_layer_0_cfg_ctrl()
        layer0Cfg |= 1 << 1
        await self.rfg.write_layer_0_cfg_ctrl(layer0Cfg, flush)
        await asyncio.sleep(waitTime)
        layer0Cfg &= ~(1 << 1)
        await self.rfg.write_layer_0_cfg_ctrl(layer0Cfg, flush)

    async def resetLayersFull(
        self, waitTime: float = 0.5, wait: bool = True, flush=True
    ):
        """Reset all layers because the reset line is shared.

        Args:
            waitTime (float):  Reset duration - Default 0.5s
            wait(bool,optional): Wait before driving reset 1 and 0 - Useful in simulation, asyncio.sleep doesn't work there
        """
        layersCfg = [
            await getattr(self.rfg, f"read_layer_{layer}_cfg_ctrl")()
            for layer in range(3)
        ]
        for layer in range(3):
            layersCfg[layer] |= 1 << 1
            await getattr(self.rfg, f"write_layer_{layer}_cfg_ctrl")(
                layersCfg[layer], flush
            )

        if wait:
            await asyncio.sleep(waitTime)

        for layer in range(3):
            layersCfg[layer] &= ~(1 << 1)
            await getattr(self.rfg, f"write_layer_{layer}_cfg_ctrl")(
                layersCfg[layer], flush
            )

    # @deprecated("Please use clearer setLayerConfig method")
    # async def setLayerReset(self,layer:int, reset : bool, disable_autoread : bool  = True, modify : bool = False, flush = False):
    #     """Asserts/Deasserts the Reset output for the given layer

    #     Args:
    #         disable_autoread (int): By default 1, disables the automatic layer readout upon interruptn=0 condition
    #         modify (bool): Reads the Control register first and only change the required bits
    #         flush (bool): Write the register right away

    #     """
    #     regval = 0xff if reset is True else 0x00
    #     if modify is True:
    #         regval =  await getattr(self.rfg, f"read_layer_{layer}_cfg_ctrl")()

    #     if reset is True:
    #         regval |= (1<<1)
    #     else:
    #         regval &= ~(1<<1)

    #     if disable_autoread is True:
    #         regval |= (1<<2)
    #     else:
    #         regval &= ~(1<<2)

    #     #if not reset:
    #     #    regval = regval | ( disable_autoread << 2 )
    #     await getattr(self.rfg, f"write_layer_{layer}_cfg_ctrl")(regval,flush)

    async def setLayerConfig(
        self,
        layer: int,
        reset: bool,
        autoread: bool,
        hold: bool,
        chipSelect: bool = False,
        disableMISO: bool = False,
        flush=False,
    ):
        """Modified the layer config with provided bools
            Since Reset and hold are shared and only connected to layer #0 and CSN is shared and or-ed between layers, you better avoid this command unless you know what you are doing
        Args:
            layer (int): layer to reset
            reset (bool): Assert/deassert reset I/O to ASIC
            autoread (bool): Enables or Disables interrupt-based automatic reading
            hold (bool): Assert/deassert hold I/O to ASIC
            chipSelect (bool): Assert/deassert Chip Select for this layer (I/O is inverted in firmware to produce low-active signal)
            disableMISO (bool): Disable SPI MISO bytes reading. Setting this bit to 1 prevents the Firmware from reading bytes
            flush (bool): Write the register right away

        """
        regval = await getattr(self.rfg, f"read_layer_{layer}_cfg_ctrl")()

        if reset is True:
            regval |= 1 << 1
        else:
            regval &= ~(1 << 1)

        if hold is True:
            regval |= 1
        else:
            regval &= 0xFE

        # Autoread is "disable" in config, so True here means False in the register
        if autoread is False:
            regval |= 1 << 2
        else:
            regval &= ~(1 << 2)

        if chipSelect is True:
            regval |= 1 << 3
        else:
            regval &= ~(1 << 3)

        if disableMISO is True:
            regval |= 1 << 4
        else:
            regval &= ~(1 << 4)

        await getattr(self.rfg, f"write_layer_{layer}_cfg_ctrl")(regval, flush)

    # async def holdLayer(self,layer:int,hold:bool = True,flush:bool = False):
    #     """Asserts/Deasserts the hold signal for the given layer - This method reads the ctrl register and modifies it
    #     ACTUALLY does not work for astep because hold is chared
    #     """
    #     ctrl = await getattr(self.rfg, f"read_layer_{layer}_cfg_ctrl")()
    #     if hold:
    #         ctrl |= 1
    #     else:
    #         ctrl &= 0XFE
    #     await getattr(self.rfg, f"write_layer_{layer}_cfg_ctrl")(ctrl,flush=flush)

    async def holdLayers(self, hold: bool, flush: bool = False):
        """ """
        ctrl = await getattr(self.rfg, f"read_layer_0_cfg_ctrl")()
        if hold:
            ctrl |= 1
        else:
            ctrl &= 0xFE
        await getattr(self.rfg, f"write_layer_0_cfg_ctrl")(ctrl, flush=flush)

    async def enableLayersReadout(
        self, layerlst: list, autoread: bool, flush: bool = False
    ):
        """
        Enables readout for a list of layers:
         - Disable autoread and chipselect for all layers
         - Disable MISO for all layers
         - Enable autoread and chipselect for selected layers
         - Enable MISO for select layers
         - Lower shared hold
        :param layerlst: list of layers numbers (int) for which readout will be enabled
        :param autoread: bool, True for autoread
        :param flush:
        """
        await self.disableLayersReadout(flush=True)
        if 0 in layerlst:
            await self.setLayerConfig(
                layer=0,
                hold=True,
                reset=False,
                autoread=autoread,
                chipSelect=True,
                disableMISO=False,
                flush=True,
            )
        if 1 in layerlst:
            await self.setLayerConfig(
                layer=1,
                hold=False,
                reset=False,
                autoread=autoread,
                chipSelect=True,
                disableMISO=False,
                flush=True,
            )
        if 2 in layerlst:
            await self.setLayerConfig(
                layer=2,
                hold=False,
                reset=False,
                autoread=autoread,
                chipSelect=True,
                disableMISO=False,
                flush=True,
            )
        await self.holdLayers(hold=False, flush=True)
        # regval =  [await getattr(self.rfg, f"read_layer_{layer}_cfg_ctrl")() for layer in range(3)]
        # for layer in range(3):
        #     regval[layer] = (regval[layer] | 0b010100) & 0b110111
        # for layer in layerlst:
        #     regval[layer] = (regval[layer] | 0b001000) & 0b101011 if autoread else (regval[layer] | 0b001100) & 0b101111
        # for layer in range(3):
        #     await getattr(self.rfg, f"write_layer_{layer}_cfg_ctrl")(regval[layer],flush)
        # await self.holdLayers(hold=False, flush=flush)

    async def disableLayersReadout(self, flush: bool = True):
        """
        Disable readout for all layers
         - Raise shared Hold
         - Disable autoread, chipselect and MISO
        """
        await self.setLayerConfig(
            layer=0,
            hold=True,
            reset=False,
            autoread=False,
            chipSelect=False,
            disableMISO=True,
            flush=flush,
        )
        await self.setLayerConfig(
            layer=1,
            hold=False,
            reset=False,
            autoread=False,
            chipSelect=False,
            disableMISO=True,
            flush=flush,
        )
        await self.setLayerConfig(
            layer=2,
            hold=False,
            reset=False,
            autoread=False,
            chipSelect=False,
            disableMISO=True,
            flush=flush,
        )

    async def writeSPIBytesToLane(
        self,
        lane: int,
        bytes: bytearray,
        timeout: int = 5,
        waitForLastChunk: bool = True,
    ):
        """
        This method writes SPI Bytes to a layer - this updated version now chunks data to accomodate the buffer size
        The method will flush bytes to the firmware automatically since we must check that we are not overflowing the SPI output buffer

        Args:
            lane(int): The lane to write SPI bytes to
            bytes(bytearray): The bytes to write to the SPI Buffer
            timeout(int,optional): Timeout in seconds until this method fails - this can be caused if the SPI Master is  deactivated (lane reset state) and the bytes are not exiting the output buffer
            waitForLastChunk(bool,optional): If set to true, when the last chunck is written, return immediately
        """

        logger.info(
            f"Writing {len(bytes)} bytes to SPI lane {lane}, current buffer size={await getattr(self.rfg, f'read_layer_{lane}_mosi_write_size')()}"
        )
        # Buffer size is the number of bytes we can write at once in the SPI output buffer
        outputBufferSize = 256
        steps = int(math.ceil(len(bytes) / outputBufferSize))
        for chunk in range(0, len(bytes), outputBufferSize):
            chunkBytes = bytes[chunk : chunk + outputBufferSize]

            # if len(chunkBytes) != 256:
            #    task = asyncio.create_task(asyncio.sleep(20))
            #    await task
            currentChunk = (chunk / outputBufferSize + 1)
            logger.info(
                "Writing Chunck %d/%d len=%d",
                currentChunk,
                steps,
                len(chunkBytes),
            )
            await getattr(self.rfg, f"write_layer_{lane}_mosi_bytes")(chunkBytes, True)

            # Wait for the current chunk to be written before sending the next one
            # If wait for Last Chunk is false and it is the last chunk, don't wait
            # This is not implemented using asyncio.timeout because it doesn't work in simulation
            if ((waitForLastChunk is True) and currentChunk == steps) or currentChunk < steps:
                
                startTime = time.time()
                currentTime = time.time()
                
                # Wait until bufer written out to astropix
                writeSize = await getattr(self.rfg, f"read_layer_{lane}_mosi_write_size")()
                while (
                    writeSize > 0
                    and (currentTime - startTime) <= timeout
                ):
                    currentTime = time.time()
                    writeSize = await getattr(self.rfg, f"read_layer_{lane}_mosi_write_size")()
                    pass

                # Test if timeout condition
                if (currentTime - startTime) > timeout:
                    raise RuntimeError(
                        f"Chunck {currentChunk}/{steps} len={len(chunkBytes)} timed out, write size is {writeSize}"
                    )
                    

    async def getLayerMOSIBytesCount(self, layer: int):
        return await getattr(self.rfg, f"read_layer_{layer}_mosi_write_size")()

    async def getLayerStatIDLECounter(self, layer: int):
        return await getattr(self.rfg, f"read_layer_{layer}_stat_idle_counter")()

    async def getLayerStatFRAMECounter(self, layer: int):
        return await getattr(self.rfg, f"read_layer_{layer}_stat_frame_counter")()

    async def getLayerStatus(self, layer: int):
        return await getattr(self.rfg, f"read_layer_{layer}_status")()

    async def getLayerControl(self, layer: int):
        return await getattr(self.rfg, f"read_layer_{layer}_cfg_ctrl")()

    async def getLayerWrongLength(self, layer: int):
        return await getattr(self.rfg, f"read_layer_{layer}_stat_wronglength_counter")()

    async def zeroLayerWrongLength(self, layer: int, flush: bool = True):
        await getattr(self.rfg, f"write_layer_{layer}_stat_wronglength_counter")(
            0, flush=flush
        )

    async def assertLayerNotInReset(self, layer: int):
        ctrlReg = await self.getLayerControl(layer)
        if ((ctrlReg >> 1) & 0x1) == 1:
            raise Exception(f"Layer {layer} is in reset, user requests it is not")

    async def resetLayerStatCounters(self, layer: int, flush: bool = True):
        await getattr(self.rfg, f"write_layer_{layer}_stat_frame_counter")(0, False)
        await getattr(self.rfg, f"write_layer_{layer}_stat_idle_counter")(0, False)
        await getattr(self.rfg, f"write_layer_{layer}_stat_wronglength_counter")(
            0, flush=flush
        )

    async def getLayerMISOBytesCount(self, layer: int):
        """Returns the number of bytes in the Slave Out Bytes Buffer"""
        return await getattr(self.rfg, f"read_layer_{layer}_mosi_write_size")()

    ## Readout
    ################
    
    async def readoutConfigure(self,packet_mode : bool,flush:bool=True):
        await self.rfg.write_layers_readout_ctrl(1 if packet_mode is True else 0,flush)
        
    async def readoutGetBufferSize(self):
        """Returns the actual size of buffer"""
        return await self.rfg.read_layers_readout_read_size()

    async def readoutReadBytes(self, count: int):
        ## Using the _raw version returns an array of bytes, while the normal method converts to int based on the number of bytes
        return await self.rfg.read_layers_readout_raw(count=count) if count > 0 else []

    ## FPGA Timestamp config
    ############
    #

    async def layersConfigFPGATimestamp(
        self,
        enable: bool,
        use_divider: bool,
        use_tlu: bool,
        tlu_busy_on_t0: bool = False,
        timestamp_size: int = 1,
        forced_value : bool = False,
        force_lsb_0 : bool = False,
        flush: bool = True,
    ):
        """
        Configure the FPGA Timestamp to count from the internal match counter, the external TS input or force at each clock cycle

        Args:
            enable (bool): Enable the FPGA Timestamp - If 0, the Timestamp will be 0 and not counting
            use_divider (bool): Enable the Timestamp divider - use #layersConfigFPGATimestampFrequency to configure frequency
            use_tlu (bool): Enable the TLU Logic
            tlu_busy_on_t0 (bool, optional): If set to True, the TLU will assert busy upon a trigger sync "t0" event
            timestamp_size (int, optional): Number of timestamp bits added to data frames.

                * 0 = 16bits
                * 1 = 32bits
                * 2 = 48bits
                * 3 = 64bits
                
            forced_value (bool,optional): Force the Timestamp to a value from layersConfigFPGATimestampForcedValue call
            force_lsb_0 (bool,optional): Force the Least Significant bit of the TS to 0

            flush (bool, optional): Write the register change to the firmware now

        """
        # assert not (source_match_counter is True and source_external is True), (
        #    "Don't configure FPGA TS to both count from internal match counter or the external clock"
        # )
        regVal = 0
        regVal |= 0x0 if enable is False else 0x1
        regVal |= 0x0 if use_divider is False else 0x2
        regVal |= 0x0 if use_tlu is False else 0x4
        regVal |= 0x0 if tlu_busy_on_t0 is False else 0x8
        regVal |= (timestamp_size & 0x3) << 4
        regVal |= (1 if forced_value else 0) << 6
        regVal |= (1 if force_lsb_0 else 0) << 7

        # Update class parameter saving the expected number of bytes for the FPGA timestamp after config
        # 0 = 16 bits, 1 = 32 bits, 2 = 48 bits, 3=64 bits
        self.fpgaTimeStampBytesCount = timestamp_size * 2 + 2

        await self.rfg.write_layers_fpga_timestamp_ctrl(regVal, flush)

    async def layersConfigFPGATimestampFrequency(
        self, targetFrequencyHz: int, flush: bool = True
    ):
        """
        Configure the FPGA Timestamp divider frequency.
        This method writes the divider register which is matched against the divider counter.
        If counter and divider match, a one cycle interrupt signal is asserted to increment the timestamp counter by 1, effectively dividing the counting speed.
        This method calculates the right divider value based on the desired freqency

        Args:
            frequency (int): The target freqency
            flush (bool, optional): Write the register change to the firmware now

        Raises:
            AssertError: If the selected frequency is too low or too high, outside of the divider counter range

        """
        
        divider = self.calculateMatchClockDivider(targetFrequencyHz)
        logger.info(f"Divider for frequency {targetFrequencyHz}={divider}")
        await self.rfg.write_layers_fpga_timestamp_divider_match(divider, flush)

    
    async def layersConfigFPGATimestampDivider(
        self, divider: int, flush: bool = True
    ):
        """Writes the Divider for the FPGA Timestamp - make sure to write a > 0 value"""
        assert divider > 0 , "Divider cannot be 0"
        await self.rfg.write_layers_fpga_timestamp_divider_match(divider, flush)
        
    
    async def layersConfigFPGATimestampForcedValue(
        self, forced: int, flush: bool = True
    ):
        """Writes the Forced Timestamp value"""
        await self.rfg.write_layers_fpga_timestamp_forced(forced, flush)
        
    async def layersConfigTLUBusyTime(self, clockCycles: int, flush: bool = True):
        """
        Configure the Number of clock cycles during which the TLU busy output is asserted to 1 after a trigger or sync event.
        The register is 16bits wide, maximum number of clock cycles is 65535
        """
        assert clockCycles > 0 and clockCycles <= 65535
        await self.rfg.write_layers_tlu_busy_duration(clockCycles, flush)
