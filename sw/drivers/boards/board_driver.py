
from deprecated import deprecated

import drivers.astep.housekeeping
import rfg.io
import rfg.core
import asyncio

from drivers.astropix.asic import Asic

from drivers.astropix.loopback_model import Astropix3LBModel

class BoardDriver():

    def __init__(self,rfg):
        self.rfg = rfg
        self.houseKeeping = drivers.astep.housekeeping.Housekeeping(self,rfg)
        self.asics = []
        
        # Synchronisation Utils
        ########

        ## Opened Event -> Set/unset by close/open
        ## Useful to start or stop tasks dependent on open/close state of the driver
        self.openedEvent = asyncio.Event()

    def selectUARTIO(self,portPath : str | None = None ):
        """This method is common to all targets now, because all targets have a USB-UART Converter available"""
        if (portPath == None):
            import drivers.astep.serial
            port = drivers.astep.serial.selectFirstLinuxFTDIPort()
            if port:
                self.rfg.withUARTIO(port.device)
                return self
            else:
                raise RuntimeError("No Serial Port could be listed")
        else:
            self.rfg.withUARTIO(portPath)
            return self
        

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
        return (await (self.rfg.read_hk_firmware_version()))

    async def readFirmwareID(self):
        """Returns the raw integer with the firmware id"""
        return await (self.rfg.read_hk_firmware_id())

    async def readFirmwareIDName(self):
        """"""
        boards  =  {0xab02: 'Nexys GECCO Astropix v2',0xab03: 'Nexys GECCO Astropix v3',0xac03:"CMOD Astropix v3"}
        boardID =  await (self.readFirmwareID())
        return boards.get(boardID,"Firmware ID unknown: {0}".format(hex(boardID)))

    async def checkFirmwareVersionAfter(self,v):
        return await (self.readFirmwareVersion()) >= v

    def getFPGACoreFrequency(self):
        """Returns the Core Clock frequency to help clock divider configuration - this method is overriden by implementation class (Gecco or Cmod)"""
        pass

    ## Gecco
    ###############
    def geccoGetVoltageBoard(self):
        return self.getVoltageBoard(slot = 4 )
    def geccoGetInjectionBoard(self):
        return self.getInjectionBoard(slot = 3 )

    ## Loopback Model
    ################
    def getLoopbackModelForLayer(self,layer):
        return Astropix3LBModel(self,layer)

    ## Chips
    ################
    async def setupASICSAuto(self, configFile : str ):

        #assert version >=2 and version < 4 , "Only Astropix 2 and 3 Supported"
        self.asics.clear()
        asic = Asic(rfg = self.rfg, row = 0)
        asic.chipversion = (await self.readFirmwareID()) & 0x0F
        print(configFile)
        self.asics.append(asic)

        return asic

    def setupASICS(self, version: int , rows: int = 1 , chipsPerRow:int = 1 , configFile : str | None = None):
        """Configure one or multiple rows with a single config file

        Args:
            version: int, AstroPix chip version
            rows: int, number of rows, default=1
            chipsPerRow: int, number of chips per row (aka daisy chain), default=1
            configFile: srt, path to yaml config file, defaults to None (no configuration applied?)
        """
        assert version >=2 and version < 4 , "Only Astropix 2 and 3 Supported"
        if version == 2: 
            self.geccoGetVoltageBoard().dacvalues =  (8, [0, 0, 1.1, 1, 0, 0, 1, 1.100])

        for i in range(rows):
            self.setupASIC(version, row=i, chipsPerRow=chipsPerRow, configFile=configFile)

    def setupASIC(self, version: int, row: int = 0, chipsPerRow: int=1, configFile: str|None = None):
        """Configures one row (aka daisy chain) with a single config file

        Args:
            version: int, AstroPix chip version
            row: int, number of the current row, default=0
            chipsPerRow: int, number of chips per row (aka daisy chain), default=1
            configFile: srt, path to yaml config file, defaults to None (no configuration applied?)
        """
        asic = Asic(rfg = self.rfg, row = row)
        asic.chipversion = version
        self.asics.append(asic)
        asic.num_chips = chipsPerRow

        if configFile is not None: 
            asic.load_conf_from_yaml(configFile)

    def getAsic(self,row = 0 ): 
        """Returns the Asic Model for the Given Row - Other chips in the Daisy Chain are handeled by the returned 'front' model"""
        return self.asics[row]

    async def enableSensorClocks(self,flush:bool = False):
        """Writes the I/O Control register to enable both Timestamp and Sample clock outputs"""
        await self.ioSetSampleClock(enable=True, flush=flush)
        await self.ioSetTimestampClock( enable=True, flush=flush)

    async def getIOControlRegister(self):
        return await self.rfg.read_io_ctrl()

    async def ioSetSampleClock(self,enable:bool,flush:bool = False):
        v = await self.rfg.read_io_ctrl()
        if enable: v|=0x1 
        else: v &= ~(0x1)
        await self.rfg.write_io_ctrl(v,flush) 
    
    async def ioSetTimestampClock(self,enable:bool,flush:bool = False):
        v = await self.rfg.read_io_ctrl()
        if enable: v|=0x2 
        else: v &= ~(0x2)
        await self.rfg.write_io_ctrl(v,flush) 
    
    async def ioSetSampleClockSingleEnded(self,enable:bool,flush:bool = False):
        v = await self.rfg.read_io_ctrl()
        if enable: v|=0x4 
        else: v &= ~(0x4)
        await self.rfg.write_io_ctrl(v,flush) 

    async def ioSetInjectionToGeccoInjBoard(self,enable:bool,flush:bool = False):
        v = await self.rfg.read_io_ctrl()
        if enable: v|=0x8 
        else: v &= ~(0x8)
        await self.rfg.write_io_ctrl(v,flush) 


    async def ioSetFPGAExternalTSClockDifferential(self,enable:bool,flush:bool = False):
        """If an external clock input is used for the FPGA TS counter, it is differential or not"""
        v = await self.rfg.read_io_ctrl()
        if enable: v|=0x10 
        else: v &= ~(0x10)
        await self.rfg.write_io_ctrl(v,flush)

    async def ioSetAstropixTSToFPGATS(self,enable:bool,flush:bool = False):
        """The Astropix TS clock can be sourced from the external FPGA TS clock (it true) or from the internal TS clock (if false)"""
        v = await self.rfg.read_io_ctrl()
        if enable: v|=0x20 
        else: v &= ~(0x20)
        await self.rfg.write_io_ctrl(v,flush) 

    ## Layers
    ##################
    async def configureLayersFrameTag(self,enable, flush = False):
        await self.rfg.write_layers_cfg_frame_tag_counter_ctrl(1 if enable is True else 0,flush)

    async def configureLayersFrameTagFrequency(self, targetFrequencyHz : int , flush = False):
        """Calculated required divider to reach the provided target SPI clock frequency"""
        coreFrequency = self.getFPGACoreFrequency()
        divider = int( coreFrequency / ( targetFrequencyHz))
        assert divider >=1 and divider <=255 , (f"Divider {divider} is too high, min. clock frequency: {int(coreFrequency/255)}")
        await self.configureLayersFrameTagDivider(divider,flush)

    async def configureLayersFrameTagDivider(self, divider , flush = False):
        await self.rfg.write_layers_cfg_frame_tag_counter_trigger_match(divider,False)
        await self.rfg.write_layers_cfg_frame_tag_counter_trigger(0,flush)
        
    async def configureLayerSPIFrequency(self, targetFrequencyHz : int , flush = False):
        """Calculated required divider to reach the provided target SPI clock frequency"""
        coreFrequency = self.getFPGACoreFrequency()
        divider = int( coreFrequency / (2 * targetFrequencyHz))
        assert divider >=1 and divider <=255 , (f"Divider {divider} is too high, min. clock frequency: {int(coreFrequency/2/255)}")
        await self.configureLayerSPIDivider(divider,flush)

    async def configureLayerSPIDivider(self, divider:int , flush = False):
        await self.rfg.write_spi_layers_ckdivider(divider,flush)


    async def layerSelectSPI(self, layer , cs : bool, flush = False):
        """This helper method asserts the shared CSN to 0 by selecting CS on layer 0
        it's a helper to be used only if the hardware uses a shared Chip Select!!
        If any Layer is in autoread mode, chip select will be already asserted
        """
        layerCfg = await getattr(self.rfg, f"read_layer_{layer}_cfg_ctrl")()
        layerCfg = (layerCfg | (1 << 3)) if cs else (layerCfg & ~(1 << 3))
        await getattr(self.rfg, f"write_layer_{layer}_cfg_ctrl")(layerCfg,flush)


    async def layersSetSPICSN(self, cs = False, flush = False):
        """This helper method asserts the shared CSN to 0 by selecting CS on layer 0
        it's a helper to be used only if the hardware uses a shared Chip Select!!
        If any Layer is in autoread mode, chip select will be already asserted
        """
        layer0Cfg = await self.rfg.read_layer_0_cfg_ctrl()
        if cs:
            layer0Cfg = layer0Cfg | (1 << 3)
        else:
            layer0Cfg = layer0Cfg & ~(1 << 3)
            
        await self.rfg.write_layer_0_cfg_ctrl(layer0Cfg,flush)

    async def layersSelectSPI(self, flush = False):
        """This helper method asserts the shared CSN to 0 by selecting CS on layer 0
        it's a helper to be used only if the hardware uses a shared Chip Select!!
        If any Layer is in autoread mode, chip select will be already asserted
        """
        layer0Cfg = await self.rfg.read_layer_0_cfg_ctrl()
        layer0Cfg = layer0Cfg | (1 << 3)
        await self.rfg.write_layer_0_cfg_ctrl(layer0Cfg,flush)

    async def layersDeselectSPI(self, flush = False):
        """This helper method deasserts the shared CSN to 1 by deselecting CS on layer 0
        it's a helper to be used only if the hardware uses a shared Chip Select!!
        If any Layer is in autoread mode, chip select will stay asserted
        """
        layer0Cfg = await self.rfg.read_layer_0_cfg_ctrl()
        layer0Cfg = layer0Cfg & ~(1 << 3)
        await self.rfg.write_layer_0_cfg_ctrl(layer0Cfg,flush)


    async def resetLayer(self, layer : int , waitTime : float = 0.5 ):
        """Sets Layer in Reset then Remove reset after a wait time. The registers are written right now.

        Args:
            layer (int): layer to reset
            waitTime (float):  Reset duration - Default 0.5s
        """
        #await self.setLayerReset(layer = layer, reset = True , flush = True )
        await self.setLayerConfig(layer=layer, reset=True, autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)
        await asyncio.sleep(waitTime)
        #await self.setLayerReset(layer = layer, reset = False , flush = True )
        await self.setLayerConfig(layer=layer, reset=False, autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)

    @deprecated("Please use clearer setLayerConfig method")
    async def setLayerReset(self,layer:int, reset : bool, disable_autoread : bool  = True, modify : bool = False, flush = False):
        """Asserts/Deasserts the Reset output for the given layer

        Args:
            disable_autoread (int): By default 1, disables the automatic layer readout upon interruptn=0 condition
            modify (bool): Reads the Control register first and only change the required bits
            flush (bool): Write the register right away
        
        """
        regval = 0xff if reset is True else 0x00
        if modify is True:
            regval =  await getattr(self.rfg, f"read_layer_{layer}_cfg_ctrl")()
        
        if reset is True:
            regval |= (1<<1)
        else:
            regval &= ~(1<<1)

        if disable_autoread is True:
            regval |= (1<<2)
        else:
            regval &= ~(1<<2)

        #if not reset: 
        #    regval = regval | ( disable_autoread << 2 )
        await getattr(self.rfg, f"write_layer_{layer}_cfg_ctrl")(regval,flush)
    
    async def setLayerConfig(self,layer:int, reset : bool, autoread : bool, hold:bool , chipSelect:bool = False,disableMISO:bool = False, flush = False):
        """Modified the layer config with provided bools

        Args:
            layer (int): layer to reset
            reset (bool): Assert/deassert reset I/O to ASIC
            autoread (bool): Enables or Disables interrupt-based automatic reading
            hold (bool): Assert/deassert hold I/O to ASIC
            chipSelect (bool): Assert/deassert Chip Select for this layer (I/O is inverted in firmware to produce low-active signal)
            disableMISO (bool): Disable SPI MISO bytes reading. Setting this bit to 1 prevents the Firmware from reading bytes
            flush (bool): Write the register right away
        
        """
        regval =  await getattr(self.rfg, f"read_layer_{layer}_cfg_ctrl")()

        if reset is True:
            regval |= (1<<1)
        else:
            regval &= ~(1<<1)

        if hold is True:
            regval |= 1 
        else: 
            regval &= 0XFE
        
        # Autoread is "disable" in config, so True here means False in the register
        if autoread is False:
            regval |= (1<<2)
        else:
            regval &= ~(1<<2)

        if chipSelect is True:
            regval |= (1<<3)
        else:
            regval &= ~(1<<3)

        if disableMISO is True:
            regval |= (1<<4)
        else:
            regval &= ~(1<<4)

        await getattr(self.rfg, f"write_layer_{layer}_cfg_ctrl")(regval,flush)

    async def holdLayer(self,layer:int,hold:bool = True,flush:bool = False):
        """Asserts/Deasserts the hold signal for the given layer - This method reads the ctrl register and modifies it"""
        ctrl = await getattr(self.rfg, f"read_layer_{layer}_cfg_ctrl")()
        if hold:
            ctrl |= 1 
        else: 
            ctrl &= 0XFE
        await getattr(self.rfg, f"write_layer_{layer}_cfg_ctrl")(ctrl,flush=flush) 


    async def writeLayerBytes(self,layer : int , bytes: bytearray,flush:bool = False):
        await getattr(self.rfg, f"write_layer_{layer}_mosi_bytes")(bytes,flush)
    
    async def writeBytesToLayer(self,layer : int , bytes: bytearray,waitBytesSend : bool = False, flush:bool = False):
        await getattr(self.rfg, f"write_layer_{layer}_mosi_bytes")(bytes,flush)
        if waitBytesSend is True:
            await self.assertLayerNotInReset(layer)
            while (await getattr(self.rfg, f"read_layer_{layer}_mosi_write_size")() > 0):
                pass

    async def getLayerMOSIBytesCount(self,layer:int):
        return await getattr(self.rfg,f"read_layer_{layer}_mosi_write_size")()

    async def getLayerStatIDLECounter(self,layer:int):
        return await getattr(self.rfg, f"read_layer_{layer}_stat_idle_counter")()

    async def getLayerStatFRAMECounter(self,layer:int):
        return await getattr(self.rfg, f"read_layer_{layer}_stat_frame_counter")()

    async def getLayerStatus(self,layer:int):
        return await getattr(self.rfg, f"read_layer_{layer}_status")()

    async def getLayerControl(self,layer:int):
        return await getattr(self.rfg, f"read_layer_{layer}_cfg_ctrl")()
    
    async def assertLayerNotInReset(self,layer:int):
        ctrlReg = await self.getLayerControl(layer)
        if ((ctrlReg >> 1) & 0x1) == 1:
            raise Exception(f"Layer {layer} is in reset, user requests it is not")

    async def resetLayerStatCounters(self,layer:int,flush:bool = True):
        await getattr(self.rfg, f"write_layer_{layer}_stat_frame_counter")(0,False)
        await getattr(self.rfg, f"write_layer_{layer}_stat_idle_counter")(0,flush)

    async def getLayerMISOBytesCount(self,layer:int):
        """Returns the number of bytes in the Slave Out Bytes Buffer"""
        return await getattr(self.rfg, f"read_layer_{layer}_mosi_write_size")()


    ## Readout
    ################
    async def readoutGetBufferSize(self):
        """Returns the actual size of buffer"""
        return await self.rfg.read_layers_readout_read_size()
    
    async def readoutReadBytes(self,count : int):
        ## Using the _raw version returns an array of bytes, while the normal method converts to int based on the number of bytes
        return  await self.rfg.read_layers_readout_raw(count = count) if count > 0 else  []
    

    ## FPGA Timestamp config
    ############

    async def layersConfigFPGATimestamp(self,enable:bool,force : bool,source_match_counter:bool,source_external:bool,flush:bool = False):
        """Configure the FPGA Timestamp to count from the internal match counter, the external TS input or force at each clock cycle"""
        assert not (source_match_counter is True and source_external is True) , "Don't configure FPGA TS to both count from internal match counter or the external clock"
        regVal = 0
        regVal |= 0x0 if enable is False else 0x1
        regVal |= 0x0 if source_match_counter is False else 0x2
        regVal |= 0x0 if source_external is False else 0x4
        regVal |= 0x0 if force is False else 0x8
        await self.rfg.write_layers_cfg_frame_tag_counter_ctrl(regVal,flush)

    async def layersConfigFPGATimestampFrequency(self,targetFrequencyHz:int,flush:bool = False):
        """Configure the internal matching counter to trigger an FPGA Timestmap count with a certain frequency"""
        coreFrequency = self.getFPGACoreFrequency()
        divider = int( coreFrequency / (targetFrequencyHz))
        assert divider >=1 and divider < pow(2,32) , (f"Target Freq is too slow, Divider {divider} is too high, min. clock frequency: {int(coreFrequency/pow(2,32))}")
        await self.rfg.write_layers_cfg_frame_tag_counter_trigger_match(divider,flush)
