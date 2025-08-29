
from deprecated import deprecated

import rfg.io
import rfg.core
import asyncio

from drivers.astropix.asic import Asic

from drivers.astropix.loopback_model import Astropix3LBModel

## Constants
##############

# SR
SPI_SR_BROADCAST    = 0x7E
SPI_SR_BIT0         = 0x00
SPI_SR_BIT1         = 0x01
SPI_SR_LOAD         = 0x03
SPI_EMPTY_BYTE      = 0x00

srRegisterName="LAYERS_SR_OUT"

# Daisychain 3bit Header + 5bit ID
SPI_HEADER_EMPTY    = 0b001 << 5
SPI_HEADER_ROUTING  = 0b010 << 5
SPI_HEADER_SR       = 0b011 << 5


class BoardDriver():

    def __init__(self, rfg):
        self.rfg = rfg
        self.asics = {}
        
        # Synchronisation Utils
        ########

        ## Opened Event -> Set/unset by close/open
        ## Useful to start or stop tasks dependent on open/close state of the driver
        self.openedEvent = asyncio.Event()

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

    async def checkFirmwareVersionAfter(self, v):
        return await (self.readFirmwareVersion()) >= v

    def getFPGACoreFrequency(self):
        """Returns the Core Clock frequency to help clock divider configuration - this method is overriden by implementation class (Gecco or Cmod)"""
        pass

    ## Loopback Model
    ################
    def getLoopbackModelForLayer(self,layer):
        return Astropix3LBModel(self,layer)

    ## Chips config
    ################
    def setupASIC(self, version:int, lane:int=0, chipsPerLane:int=1, configFile:str|None=None):
        """Configures one row (aka daisy chain) with a single config file

        Args:
            version: int, AstroPix chip version
            row: int, number of the current row, default=0
            chipsPerLane: int, number of chips per row (aka daisy chain), default=1
            configFile: srt, path to yaml config file, defaults to None (no configuration applied?)
        """
        asic = Asic(chipversion=version)
        if configFile is not None: 
            asic.load_conf_from_yaml(configFile)
        self.asics.update({lane:asic})

    def getAsic(self, layer:int=0):
        """Returns the Asic Model for the Given Row - Other chips in the Daisy Chain are handeled by the returned 'front' model"""
        return self.asics[layer]

    def getRoutingFrame(self, layer:int=0, firstChipID:int=0):
        return [SPI_HEADER_ROUTING | firstChipID] + [0x00]*(self.asics[layer].num_chips-1)*2#+1?

    def getConfigFrame(self, load:bool=True, n_load:int=10, broadcast:bool=False, layer:int=0, targetChip:int=0, config:BitArray|None=None)  -> bytearray:
        """
        Converts the ASIC Config bits to the corresponding bytes to send via SPI
        :param load: bool, includes load signal, default=True
        :param n_load: int, length of load signal, default=10
        :param broadcast: bool, Enable Broadcast - in that case the config of targetChip will be broadcasted, default=False
        :param layer: int, daisy chain to target, default=0
        :param targetChip: int, ChipID of source config, set in header if !broadcast, default=0
        :param config: BitArray, vector of config bits, default=None (generated from targetchip and layer)
        :returns: SPI ASIC config pattern
        """
        ## Generate Bit vector for config
        if value is None:
            value = self.gen_config_vector_SPI(msbfirst = False,targetChip = targetChip)
        # Write SPI SR Command to set MUX
        if broadcast:
            data = bytearray([SPI_SR_BROADCAST])
        else:
            data = bytearray([SPI_HEADER_SR | targetChip])
        # data
        for bit in value:
            sin = SPI_SR_BIT1 if bit else SPI_SR_BIT0
            data.append(sin)
        # Append Load signal and empty bytes
        if load:
            data.extend([SPI_SR_LOAD] * n_load)
        # Append 2 Empty bytes per chip in the chip, to ensure the config frame is pushed completely through the chain
        data.extend([SPI_EMPTY_BYTE] * ((self._num_chips-1) *2))
        logger.debug("Length: %d\n Data (%db): %s\n", len(data), len(value), value)
        return data

    ## IO control and clocks
    ########################
    async def getIOControlRegister(self):
        return await self.rfg.read_io_ctrl()

    async def ioSetSampleClock(self ,enable:bool, flush:bool=False):
        v = await self.rfg.read_io_ctrl()
        if enable: v |= 0x1 
        else: v &= ~(0x1)
        await self.rfg.write_io_ctrl(v,flush) 
    
    async def ioSetTimestampClock(self, enable:bool, flush:bool=False):
        v = await self.rfg.read_io_ctrl()
        if enable: v |= 0x2 
        else: v &= ~(0x2)
        await self.rfg.write_io_ctrl(v,flush) 
    
    async def ioSetSampleClockSingleEnded(self, enable:bool, flush:bool=False):
        v = await self.rfg.read_io_ctrl()
        if enable: v |= 0x4 
        else: v &= ~(0x4)
        await self.rfg.write_io_ctrl(v,flush) 

    async def ioSetInjectionToChip(self, enable:bool=True, flush:bool=False):
        v = await self.rfg.read_io_ctrl()
        if enable: v &= ~(0x8)
        else: v |= 0x8
        await self.rfg.write_io_ctrl(v,flush) 

    async def ioSetFPGAExternalTSClockDifferential(self, enable:bool, flush:bool=False):
        """If an external clock input is used for the FPGA TS counter, it is differential or not"""
        v = await self.rfg.read_io_ctrl()
        if enable: v |= 0x10 
        else: v &= ~(0x10)
        await self.rfg.write_io_ctrl(v,flush)

    async def ioSetAstropixTSToFPGATS(self, enable:bool, flush:bool=False):
        """The Astropix TS clock can be sourced from the external FPGA TS clock (if true) or from the internal TS clock (if false)"""
        v = await self.rfg.read_io_ctrl()
        if enable: v |= 0x20 
        else: v &= ~(0x20)
        await self.rfg.write_io_ctrl(v,flush) 

    async def enableSensorClocks(self, flush:bool=False):
        """Writes the I/O Control register to enable both Timestamp and Sample clock outputs"""
        await self.ioSetSampleClock(enable=True, flush=flush)
        await self.ioSetTimestampClock(enable=True, flush=flush)

    # FPGA Timestamp config
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

    # SPI configuration
    async def configureLayerSPIFrequency(self, targetFrequencyHz:int, flush:bool=False):
        """Calculated required divider to reach the provided target SPI clock frequency"""
        coreFrequency = self.getFPGACoreFrequency()
        divider = int( coreFrequency / (2 * targetFrequencyHz))
        assert divider >=1 and divider <=255 , (f"Divider {divider} is too high, min. clock frequency: {int(coreFrequency/2/255)}")
        await self.configureLayerSPIDivider(divider, flush)

    async def configureLayerSPIDivider(self, divider:int, flush:bool=False):
        await self.rfg.write_spi_layers_ckdivider(divider, flush)


    ## Layers control
    ##################
    async def setLayerConfig(self, layer:int, reset:bool, autoread:bool, hold:bool, chipSelect:bool=False, disableMISO:bool=False, flush:bool=False):
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
        regval =  await getattr(self.rfg, f"read_layer_{layer}_cfg_ctrl")()
        if hold: regval |= 1
        else: regval &= ~1
        if reset: regval |= (1<<1)
        else: regval &= ~(1<<1)
        # Autoread is "disable" in config, so True here means False in the register
        if autoread is False: regval |= (1<<2)
        else: regval &= ~(1<<2)
        if chipSelect: regval |= (1<<3)
        else: regval &= ~(1<<3)
        if disableMISO: regval |= (1<<4)
        else: regval &= ~(1<<4)
        await getattr(self.rfg, f"write_layer_{layer}_cfg_ctrl")(regval, flush)

    async def holdLayers(self, hold:bool, flush:bool=False):
        """
        """
        ctrl = await self.rfg.read_layer_0_cfg_ctrl()
        if hold: ctrl |= 1
        else: ctrl &= ~1
        await getattr(self.rfg.write_layer_0_cfg_ctrl(ctrl, flush=flush)

    async def resetLayers(self, waitTime:float=0.5, flush:bool=True):
        """Reset all layers because the reset line is shared.

        Args:
            waitTime (float):  Reset duration - Default 0.5s
        """
        layer0Cfg = await self.rfg.read_layer_0_cfg_ctrl()
        layer0Cfg |= (1<<1)
        await self.rfg.write_layer_0_cfg_ctrl(layer0Cfg, flush)
        await asyncio.sleep(waitTime)
        layer0Cfg &= ~(1<<1)
        await self.rfg.write_layer_0_cfg_ctrl(layer0Cfg, flush)

    async def layersSetSPICSN(self, cs:bool=False, flush:bool=False):
        """This helper method asserts the shared CSN to 0 by selecting CS on layer 0
        it's a helper to be used only if the hardware uses a shared Chip Select!!
        If any Layer is in autoread mode, chip select will be already asserted
        """
        layer0Cfg = await self.rfg.read_layer_0_cfg_ctrl()
        if cs: layer0Cfg |= (1 << 3)
        else: layer0Cfg &= ~(1 << 3)
        await self.rfg.write_layer_0_cfg_ctrl(layer0Cfg, flush)

    async def layersSelectSPI(self, flush:bool=False):
        """This helper method asserts the shared CSN to 0 by selecting CS on layer 0
        it's a helper to be used only if the hardware uses a shared Chip Select!!
        If any Layer is in autoread mode, chip select will be already asserted
        """
        layer0Cfg = await self.rfg.read_layer_0_cfg_ctrl()
        layer0Cfg |= (1 << 3)
        await self.rfg.write_layer_0_cfg_ctrl(layer0Cfg, flush)

    async def layersDeselectSPI(self, flush:bool=False):
        """This helper method deasserts the shared CSN to 1 by deselecting CS on layer 0
        it's a helper to be used only if the hardware uses a shared Chip Select!!
        If any Layer is in autoread mode, chip select will stay asserted
        """
        layer0Cfg = await self.rfg.read_layer_0_cfg_ctrl()
        layer0Cfg &= ~(1 << 3)
        await self.rfg.write_layer_0_cfg_ctrl(layer0Cfg, flush)


    # async def layerSelectSPI(self, layer , cs : bool, flush = False):
    #     """This helper method asserts the shared CSN to 0 by selecting CS on layer 0
    #     it's a helper to be used only if the hardware uses a shared Chip Select!!
    #     If any Layer is in autoread mode, chip select will be already asserted
    #     """
    #     layerCfg = await getattr(self.rfg, f"read_layer_{layer}_cfg_ctrl")()
    #     layerCfg = (layerCfg | (1 << 3)) if cs else (layerCfg & ~(1 << 3))
    #     await getattr(self.rfg, f"write_layer_{layer}_cfg_ctrl")(layerCfg,flush)


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


    #async def resetLayersFull(self, waitTime:float=0.5, flush=True):
    #    """Reset all layers because the reset line is shared.

    #    Args:
    #        waitTime (float):  Reset duration - Default 0.5s
    #    """
    #    layersCfg = [await getattr(self.rfg, f"read_layer_{layer}_cfg_ctrl")() for layer in range(3)]
    #    for layer in range(3):
    #        layersCfg[layer] |= (1<<1)
    #        await getattr(self.rfg, f"write_layer_{layer}_cfg_ctrl")(layersCfg[layer], flush)
    #    await asyncio.sleep(waitTime)
    #    for layer in range(3):
    #        layersCfg[layer] &= ~(1<<1)
    #        await getattr(self.rfg, f"write_layer_{layer}_cfg_ctrl")(layersCfg[layer], flush)


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

    async def enableLayersReadout(self, layerlst:list, autoread:bool, flush:bool = False):
        """
        Enables readout - Implemented in daughter classes
        """
        pass

    async def disableLayersReadout(self, flush:bool = True):
        """
        Disable readout for all layers
        """
        pass

    async def getLayerMOSIBytesCount(self, layer:int=0):
        return await getattr(self.rfg,f"read_layer_{layer}_mosi_write_size")()

    async def getLayerStatIDLECounter(self, layer:int=0):
        return await getattr(self.rfg, f"read_layer_{layer}_stat_idle_counter")()

    async def getLayerStatFRAMECounter(self, layer:int=0):
        return await getattr(self.rfg, f"read_layer_{layer}_stat_frame_counter")()

    async def getLayerStatus(self, layer:int=0):
        return await getattr(self.rfg, f"read_layer_{layer}_status")()

    async def getLayerControl(self, layer:int=0):
        return await getattr(self.rfg, f"read_layer_{layer}_cfg_ctrl")()
    
    async def getLayerWrongLength(self, layer:int=0):
        return await getattr(self.rfg, f"read_layer_{layer}_stat_wronglength_counter")()

    async def zeroLayerWrongLength(self, layer:int=0, flush:bool=True):
        await getattr(self.rfg, f"write_layer_{layer}_stat_wronglength_counter")(0, flush=flush)

    async def assertLayerNotInReset(self, layer:int=0):
        ctrlReg = await self.getLayerControl(layer)
        if ((ctrlReg >> 1) & 0x1) == 1:
            raise Exception(f"Layer {layer} is in reset, user requests it is not")

    async def resetLayerStatCounters(self, layer:int=0, flush:bool=True):
        await getattr(self.rfg, f"write_layer_{layer}_stat_frame_counter")(0,False)
        await getattr(self.rfg, f"write_layer_{layer}_stat_idle_counter")(0,flush)


    ## Layers data IO
    ##################

    # Writing
    async def writeSRConfig(self, config:BitArray, layer:int=0, ckdiv:int=8, limit:int|None=None):
        """This method writes the Config bits through the register file bits (SIN,CK1,CK2, LOAD)
        Args:
            config(BitArray): configuration bit vector to be written
            layer(int) : Layer to write config to, default=0
            ckdiv(int) : Repeats the write for ck1/ck2/load ckdiv times to strech the signal. Set this value higher for faster software interface, default=8
            limit(int) : Only write limit bits to SR - Mostly useful in simulation to limit runtime which checking the I/O are correctly driven, default=None
        """
        if limit is not None: 
            config = config[:limit]
        logger.info("Writing SR Config for row=%d,len=%d",layer,len(config))
        ## Find target register to write to for IO
        targetRegister = self.rfg.Registers[self.rfgSRRegisterName]
        ## Write to SR using register
        for bit in config:
            # SIN (bit 3 in register)
            sinValue = 0x4 if bit else 0
            self.rfg.addWrite(register = targetRegister, value = sinValue, repeat = ckdiv) #ensure SIN has higher delay than CLK1 to avoid setup violation / incorrect sampling
            # CK1
            self.rfg.addWrite(register = targetRegister, value = sinValue | 0x1 , repeat = ckdiv)
            self.rfg.addWrite(register = targetRegister, value = sinValue , repeat = ckdiv)
            # CK2
            self.rfg.addWrite(register = targetRegister, value = sinValue | 0x2 , repeat = ckdiv)
            self.rfg.addWrite(register = targetRegister, value = sinValue , repeat = ckdiv)
        ## Set Load (loads start bit 4)
        self.rfg.addWrite(register = targetRegister, value = sinValue | (0x1 << (layer +3)) , repeat = ckdiv)
        self.rfg.addWrite(register = targetRegister, value = 0 , repeat = ckdiv)
        await self.rfg.flush()

    async def writeSPI(self, payload:bytearray, layer:int=0, timeout:float=1.):
        """Writes the payload over SPI
        :param payload: bytearray to be written (by chunks of 256 bytes)
        :param layer: int, layer number (default 0, only 0 is connected on the Gecco board)
        :param timeout: maximum duration allowed for a single chunk
        :raises: RuntimeError if a chunks times out
        """
        step  = 256
        steps = int(math.ceil(len(payload)/step))
        for chunk in range(0, len(payload), step):
            chunkBytes = payload[chunk:chunk+step]
            logger.info("Writing Chunck %d/%d len=%d",(chunk/step+1),steps,len(chunkBytes))
            if self.getLayerControl(layer) & 0x2 == 0x2:
                logger.warning("Reset is asserted! Data will be written after reset is de-asserted.")
            await getattr(self.rfg, f"write_layer_{layer}_mosi_bytes")(chunkBytes,True)
            # Wait for the current chunk to be written before sending the next one
            maxtime = time.time()+timeout
            while (await getattr(self.rfg, f"read_layer_{layer}_mosi_write_size")() > 0 and time.time() <= maxtime):
                time.sleep(0.05)
            if time.time() > maxtime:
                raise RuntimeError("Chunck {}/{} len={} timed out".format(int(chunk/step+1),steps,len(chunkBytes)))

    async def writeSPIRoutingFrame(self, layer:int=0, firstChipID:int=0):
        await self.writeSPI(self.getRoutingFrame(layer, firstChipID), layer)

    async def writeSPIConfig(self, layer:int=0, targetChip:int=0, broadcast:bool=False):
        await self.writeSPI(self.getConfigFrame(layer=layer, targetChip=targetChip, broadcast=broadcast, config=None), layer)

    #async def writeLayerBytes(self, payload:bytearray, layer:int=0, flush:bool=False):
    #    await getattr(self.rfg, f"write_layer_{layer}_mosi_bytes")(bytes,flush)

    #async def writeBytesToLayer(self, payload:bytearray, layer:int=0, waitBytesSend:bool=True, flush:bool=False):
    #    await getattr(self.rfg, f"write_layer_{layer}_mosi_bytes")(bytes,flush)
    #    if waitBytesSend is True:
    #        await self.assertLayerNotInReset(layer)
    #        while (await getattr(self.rfg, f"read_layer_{layer}_mosi_write_size")() > 0):
    #            pass

    # Readout
    async def readoutGetBufferSize(self):
        """Returns the actual size of buffer"""
        return await self.rfg.read_layers_readout_read_size()

    async def readoutReadBytes(self, count:int):
        ## Using the _raw version returns an array of bytes, while the normal method converts to int based on the number of bytes
        return  await self.rfg.read_layers_readout_raw(count = count) if count > 0 else  []

