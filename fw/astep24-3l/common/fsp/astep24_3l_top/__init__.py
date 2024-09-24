

import logging
from rfg.core import AbstractRFG
from rfg.core import RFGRegister
logger = logging.getLogger(__name__)


def load_rfg():
    return main_rfg()


HK_FIRMWARE_ID = 0x0
HK_FIRMWARE_VERSION = 0x4
HK_XADC_TEMPERATURE = 0x8
HK_XADC_VCCINT = 0xa
HK_CONVERSION_TRIGGER = 0xc
HK_STAT_CONVERSIONS_COUNTER = 0x10
HK_CTRL = 0x14
HK_ADCDAC_MOSI_FIFO = 0x15
HK_ADC_MISO_FIFO = 0x16
HK_ADC_MISO_FIFO_READ_SIZE = 0x17
SPI_LAYERS_CKDIVIDER = 0x1b
SPI_HK_CKDIVIDER = 0x1c
LAYER_0_CFG_CTRL = 0x1d
LAYER_1_CFG_CTRL = 0x1e
LAYER_2_CFG_CTRL = 0x1f
LAYER_0_STATUS = 0x20
LAYER_1_STATUS = 0x21
LAYER_2_STATUS = 0x22
LAYER_0_STAT_FRAME_COUNTER = 0x23
LAYER_1_STAT_FRAME_COUNTER = 0x27
LAYER_2_STAT_FRAME_COUNTER = 0x2b
LAYER_0_STAT_IDLE_COUNTER = 0x2f
LAYER_1_STAT_IDLE_COUNTER = 0x33
LAYER_2_STAT_IDLE_COUNTER = 0x37
LAYER_0_MOSI = 0x3b
LAYER_0_MOSI_WRITE_SIZE = 0x3c
LAYER_1_MOSI = 0x40
LAYER_1_MOSI_WRITE_SIZE = 0x41
LAYER_2_MOSI = 0x45
LAYER_2_MOSI_WRITE_SIZE = 0x46
LAYER_0_LOOPBACK_MISO = 0x4a
LAYER_0_LOOPBACK_MISO_WRITE_SIZE = 0x4b
LAYER_1_LOOPBACK_MISO = 0x4f
LAYER_1_LOOPBACK_MISO_WRITE_SIZE = 0x50
LAYER_2_LOOPBACK_MISO = 0x54
LAYER_2_LOOPBACK_MISO_WRITE_SIZE = 0x55
LAYER_0_LOOPBACK_MOSI = 0x59
LAYER_0_LOOPBACK_MOSI_READ_SIZE = 0x5a
LAYER_1_LOOPBACK_MOSI = 0x5e
LAYER_1_LOOPBACK_MOSI_READ_SIZE = 0x5f
LAYER_2_LOOPBACK_MOSI = 0x63
LAYER_2_LOOPBACK_MOSI_READ_SIZE = 0x64
LAYERS_CFG_FRAME_TAG_COUNTER_CTRL = 0x68
LAYERS_CFG_FRAME_TAG_COUNTER_TRIGGER = 0x69
LAYERS_CFG_FRAME_TAG_COUNTER = 0x6d
LAYERS_CFG_NODATA_CONTINUE = 0x71
LAYERS_SR_OUT = 0x72
LAYERS_SR_IN = 0x73
LAYERS_INJ_CTRL = 0x74
LAYERS_INJ_WADDR = 0x75
LAYERS_INJ_WDATA = 0x76
LAYERS_READOUT = 0x77
LAYERS_READOUT_READ_SIZE = 0x78
IO_CTRL = 0x7c
IO_LED = 0x7d
GECCO_SR_CTRL = 0x7e
HK_CONVERSION_TRIGGER_MATCH = 0x7f
LAYERS_CFG_FRAME_TAG_COUNTER_TRIGGER_MATCH = 0x83




class main_rfg(AbstractRFG):
    """Register File Entry Point Class"""
    
    
    class Registers(RFGRegister):
        HK_FIRMWARE_ID = 0x0
        HK_FIRMWARE_VERSION = 0x4
        HK_XADC_TEMPERATURE = 0x8
        HK_XADC_VCCINT = 0xa
        HK_CONVERSION_TRIGGER = 0xc
        HK_STAT_CONVERSIONS_COUNTER = 0x10
        HK_CTRL = 0x14
        HK_ADCDAC_MOSI_FIFO = 0x15
        HK_ADC_MISO_FIFO = 0x16
        HK_ADC_MISO_FIFO_READ_SIZE = 0x17
        SPI_LAYERS_CKDIVIDER = 0x1b
        SPI_HK_CKDIVIDER = 0x1c
        LAYER_0_CFG_CTRL = 0x1d
        LAYER_1_CFG_CTRL = 0x1e
        LAYER_2_CFG_CTRL = 0x1f
        LAYER_0_STATUS = 0x20
        LAYER_1_STATUS = 0x21
        LAYER_2_STATUS = 0x22
        LAYER_0_STAT_FRAME_COUNTER = 0x23
        LAYER_1_STAT_FRAME_COUNTER = 0x27
        LAYER_2_STAT_FRAME_COUNTER = 0x2b
        LAYER_0_STAT_IDLE_COUNTER = 0x2f
        LAYER_1_STAT_IDLE_COUNTER = 0x33
        LAYER_2_STAT_IDLE_COUNTER = 0x37
        LAYER_0_MOSI = 0x3b
        LAYER_0_MOSI_WRITE_SIZE = 0x3c
        LAYER_1_MOSI = 0x40
        LAYER_1_MOSI_WRITE_SIZE = 0x41
        LAYER_2_MOSI = 0x45
        LAYER_2_MOSI_WRITE_SIZE = 0x46
        LAYER_0_LOOPBACK_MISO = 0x4a
        LAYER_0_LOOPBACK_MISO_WRITE_SIZE = 0x4b
        LAYER_1_LOOPBACK_MISO = 0x4f
        LAYER_1_LOOPBACK_MISO_WRITE_SIZE = 0x50
        LAYER_2_LOOPBACK_MISO = 0x54
        LAYER_2_LOOPBACK_MISO_WRITE_SIZE = 0x55
        LAYER_0_LOOPBACK_MOSI = 0x59
        LAYER_0_LOOPBACK_MOSI_READ_SIZE = 0x5a
        LAYER_1_LOOPBACK_MOSI = 0x5e
        LAYER_1_LOOPBACK_MOSI_READ_SIZE = 0x5f
        LAYER_2_LOOPBACK_MOSI = 0x63
        LAYER_2_LOOPBACK_MOSI_READ_SIZE = 0x64
        LAYERS_CFG_FRAME_TAG_COUNTER_CTRL = 0x68
        LAYERS_CFG_FRAME_TAG_COUNTER_TRIGGER = 0x69
        LAYERS_CFG_FRAME_TAG_COUNTER = 0x6d
        LAYERS_CFG_NODATA_CONTINUE = 0x71
        LAYERS_SR_OUT = 0x72
        LAYERS_SR_IN = 0x73
        LAYERS_INJ_CTRL = 0x74
        LAYERS_INJ_WADDR = 0x75
        LAYERS_INJ_WDATA = 0x76
        LAYERS_READOUT = 0x77
        LAYERS_READOUT_READ_SIZE = 0x78
        IO_CTRL = 0x7c
        IO_LED = 0x7d
        GECCO_SR_CTRL = 0x7e
        HK_CONVERSION_TRIGGER_MATCH = 0x7f
        LAYERS_CFG_FRAME_TAG_COUNTER_TRIGGER_MATCH = 0x83
    
    
    
    def __init__(self):
        super().__init__()
    
    
    def hello(self):
        logger.info("Hello World")
    
    
    
    async def read_hk_firmware_id(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['HK_FIRMWARE_ID'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_hk_firmware_id_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['HK_FIRMWARE_ID'],count = count, increment = True)
        
    
    
    
    async def read_hk_firmware_version(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['HK_FIRMWARE_VERSION'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_hk_firmware_version_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['HK_FIRMWARE_VERSION'],count = count, increment = True)
        
    
    
    
    async def read_hk_xadc_temperature(self, count : int = 2 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['HK_XADC_TEMPERATURE'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_hk_xadc_temperature_raw(self, count : int = 2 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['HK_XADC_TEMPERATURE'],count = count, increment = True)
        
    
    
    
    async def read_hk_xadc_vccint(self, count : int = 2 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['HK_XADC_VCCINT'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_hk_xadc_vccint_raw(self, count : int = 2 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['HK_XADC_VCCINT'],count = count, increment = True)
        
    
    
    
    async def write_hk_conversion_trigger(self,value : int,flush = False):
        self.addWrite(register = self.Registers['HK_CONVERSION_TRIGGER'],value = value,increment = True,valueLength=4)
        if flush == True:
            await self.flush()
        
    
    async def read_hk_conversion_trigger(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['HK_CONVERSION_TRIGGER'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_hk_conversion_trigger_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['HK_CONVERSION_TRIGGER'],count = count, increment = True)
        
    
    
    
    async def read_hk_stat_conversions_counter(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['HK_STAT_CONVERSIONS_COUNTER'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_hk_stat_conversions_counter_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['HK_STAT_CONVERSIONS_COUNTER'],count = count, increment = True)
        
    
    
    
    async def write_hk_ctrl(self,value : int,flush = False):
        self.addWrite(register = self.Registers['HK_CTRL'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def read_hk_ctrl(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['HK_CTRL'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_hk_ctrl_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['HK_CTRL'],count = count, increment = False)
        
    
    
    
    async def write_hk_adcdac_mosi_fifo(self,value : int,flush = False):
        self.addWrite(register = self.Registers['HK_ADCDAC_MOSI_FIFO'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def write_hk_adcdac_mosi_fifo_bytes(self,values : bytearray,flush = False):
        for b in values:
            self.addWrite(register = self.Registers['HK_ADCDAC_MOSI_FIFO'],value = b,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    
    
    async def read_hk_adc_miso_fifo(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['HK_ADC_MISO_FIFO'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_hk_adc_miso_fifo_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['HK_ADC_MISO_FIFO'],count = count, increment = False)
        
    
    
    
    async def read_hk_adc_miso_fifo_read_size(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['HK_ADC_MISO_FIFO_READ_SIZE'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_hk_adc_miso_fifo_read_size_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['HK_ADC_MISO_FIFO_READ_SIZE'],count = count, increment = True)
        
    
    
    
    async def write_spi_layers_ckdivider(self,value : int,flush = False):
        self.addWrite(register = self.Registers['SPI_LAYERS_CKDIVIDER'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def read_spi_layers_ckdivider(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['SPI_LAYERS_CKDIVIDER'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_spi_layers_ckdivider_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['SPI_LAYERS_CKDIVIDER'],count = count, increment = False)
        
    
    
    
    async def write_spi_hk_ckdivider(self,value : int,flush = False):
        self.addWrite(register = self.Registers['SPI_HK_CKDIVIDER'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def read_spi_hk_ckdivider(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['SPI_HK_CKDIVIDER'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_spi_hk_ckdivider_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['SPI_HK_CKDIVIDER'],count = count, increment = False)
        
    
    
    
    async def write_layer_0_cfg_ctrl(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYER_0_CFG_CTRL'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def read_layer_0_cfg_ctrl(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_0_CFG_CTRL'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_0_cfg_ctrl_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_0_CFG_CTRL'],count = count, increment = False)
        
    
    
    
    async def write_layer_1_cfg_ctrl(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYER_1_CFG_CTRL'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def read_layer_1_cfg_ctrl(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_1_CFG_CTRL'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_1_cfg_ctrl_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_1_CFG_CTRL'],count = count, increment = False)
        
    
    
    
    async def write_layer_2_cfg_ctrl(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYER_2_CFG_CTRL'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def read_layer_2_cfg_ctrl(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_2_CFG_CTRL'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_2_cfg_ctrl_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_2_CFG_CTRL'],count = count, increment = False)
        
    
    
    
    async def read_layer_0_status(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_0_STATUS'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_0_status_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_0_STATUS'],count = count, increment = False)
        
    
    
    
    async def read_layer_1_status(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_1_STATUS'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_1_status_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_1_STATUS'],count = count, increment = False)
        
    
    
    
    async def read_layer_2_status(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_2_STATUS'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_2_status_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_2_STATUS'],count = count, increment = False)
        
    
    
    
    async def write_layer_0_stat_frame_counter(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYER_0_STAT_FRAME_COUNTER'],value = value,increment = True,valueLength=4)
        if flush == True:
            await self.flush()
        
    
    async def read_layer_0_stat_frame_counter(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_0_STAT_FRAME_COUNTER'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_0_stat_frame_counter_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_0_STAT_FRAME_COUNTER'],count = count, increment = True)
        
    
    
    
    async def write_layer_1_stat_frame_counter(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYER_1_STAT_FRAME_COUNTER'],value = value,increment = True,valueLength=4)
        if flush == True:
            await self.flush()
        
    
    async def read_layer_1_stat_frame_counter(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_1_STAT_FRAME_COUNTER'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_1_stat_frame_counter_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_1_STAT_FRAME_COUNTER'],count = count, increment = True)
        
    
    
    
    async def write_layer_2_stat_frame_counter(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYER_2_STAT_FRAME_COUNTER'],value = value,increment = True,valueLength=4)
        if flush == True:
            await self.flush()
        
    
    async def read_layer_2_stat_frame_counter(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_2_STAT_FRAME_COUNTER'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_2_stat_frame_counter_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_2_STAT_FRAME_COUNTER'],count = count, increment = True)
        
    
    
    
    async def write_layer_0_stat_idle_counter(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYER_0_STAT_IDLE_COUNTER'],value = value,increment = True,valueLength=4)
        if flush == True:
            await self.flush()
        
    
    async def read_layer_0_stat_idle_counter(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_0_STAT_IDLE_COUNTER'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_0_stat_idle_counter_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_0_STAT_IDLE_COUNTER'],count = count, increment = True)
        
    
    
    
    async def write_layer_1_stat_idle_counter(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYER_1_STAT_IDLE_COUNTER'],value = value,increment = True,valueLength=4)
        if flush == True:
            await self.flush()
        
    
    async def read_layer_1_stat_idle_counter(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_1_STAT_IDLE_COUNTER'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_1_stat_idle_counter_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_1_STAT_IDLE_COUNTER'],count = count, increment = True)
        
    
    
    
    async def write_layer_2_stat_idle_counter(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYER_2_STAT_IDLE_COUNTER'],value = value,increment = True,valueLength=4)
        if flush == True:
            await self.flush()
        
    
    async def read_layer_2_stat_idle_counter(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_2_STAT_IDLE_COUNTER'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_2_stat_idle_counter_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_2_STAT_IDLE_COUNTER'],count = count, increment = True)
        
    
    
    
    async def write_layer_0_mosi(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYER_0_MOSI'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def write_layer_0_mosi_bytes(self,values : bytearray,flush = False):
        for b in values:
            self.addWrite(register = self.Registers['LAYER_0_MOSI'],value = b,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    
    
    async def read_layer_0_mosi_write_size(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_0_MOSI_WRITE_SIZE'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_0_mosi_write_size_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_0_MOSI_WRITE_SIZE'],count = count, increment = True)
        
    
    
    
    async def write_layer_1_mosi(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYER_1_MOSI'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def write_layer_1_mosi_bytes(self,values : bytearray,flush = False):
        for b in values:
            self.addWrite(register = self.Registers['LAYER_1_MOSI'],value = b,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    
    
    async def read_layer_1_mosi_write_size(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_1_MOSI_WRITE_SIZE'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_1_mosi_write_size_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_1_MOSI_WRITE_SIZE'],count = count, increment = True)
        
    
    
    
    async def write_layer_2_mosi(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYER_2_MOSI'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def write_layer_2_mosi_bytes(self,values : bytearray,flush = False):
        for b in values:
            self.addWrite(register = self.Registers['LAYER_2_MOSI'],value = b,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    
    
    async def read_layer_2_mosi_write_size(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_2_MOSI_WRITE_SIZE'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_2_mosi_write_size_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_2_MOSI_WRITE_SIZE'],count = count, increment = True)
        
    
    
    
    async def write_layer_0_loopback_miso(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYER_0_LOOPBACK_MISO'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def write_layer_0_loopback_miso_bytes(self,values : bytearray,flush = False):
        for b in values:
            self.addWrite(register = self.Registers['LAYER_0_LOOPBACK_MISO'],value = b,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    
    
    async def read_layer_0_loopback_miso_write_size(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_0_LOOPBACK_MISO_WRITE_SIZE'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_0_loopback_miso_write_size_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_0_LOOPBACK_MISO_WRITE_SIZE'],count = count, increment = True)
        
    
    
    
    async def write_layer_1_loopback_miso(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYER_1_LOOPBACK_MISO'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def write_layer_1_loopback_miso_bytes(self,values : bytearray,flush = False):
        for b in values:
            self.addWrite(register = self.Registers['LAYER_1_LOOPBACK_MISO'],value = b,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    
    
    async def read_layer_1_loopback_miso_write_size(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_1_LOOPBACK_MISO_WRITE_SIZE'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_1_loopback_miso_write_size_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_1_LOOPBACK_MISO_WRITE_SIZE'],count = count, increment = True)
        
    
    
    
    async def write_layer_2_loopback_miso(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYER_2_LOOPBACK_MISO'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def write_layer_2_loopback_miso_bytes(self,values : bytearray,flush = False):
        for b in values:
            self.addWrite(register = self.Registers['LAYER_2_LOOPBACK_MISO'],value = b,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    
    
    async def read_layer_2_loopback_miso_write_size(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_2_LOOPBACK_MISO_WRITE_SIZE'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_2_loopback_miso_write_size_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_2_LOOPBACK_MISO_WRITE_SIZE'],count = count, increment = True)
        
    
    
    
    async def read_layer_0_loopback_mosi(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_0_LOOPBACK_MOSI'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_0_loopback_mosi_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_0_LOOPBACK_MOSI'],count = count, increment = False)
        
    
    
    
    async def read_layer_0_loopback_mosi_read_size(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_0_LOOPBACK_MOSI_READ_SIZE'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_0_loopback_mosi_read_size_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_0_LOOPBACK_MOSI_READ_SIZE'],count = count, increment = True)
        
    
    
    
    async def read_layer_1_loopback_mosi(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_1_LOOPBACK_MOSI'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_1_loopback_mosi_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_1_LOOPBACK_MOSI'],count = count, increment = False)
        
    
    
    
    async def read_layer_1_loopback_mosi_read_size(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_1_LOOPBACK_MOSI_READ_SIZE'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_1_loopback_mosi_read_size_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_1_LOOPBACK_MOSI_READ_SIZE'],count = count, increment = True)
        
    
    
    
    async def read_layer_2_loopback_mosi(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_2_LOOPBACK_MOSI'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_2_loopback_mosi_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_2_LOOPBACK_MOSI'],count = count, increment = False)
        
    
    
    
    async def read_layer_2_loopback_mosi_read_size(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_2_LOOPBACK_MOSI_READ_SIZE'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_2_loopback_mosi_read_size_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_2_LOOPBACK_MOSI_READ_SIZE'],count = count, increment = True)
        
    
    
    
    async def write_layers_cfg_frame_tag_counter_ctrl(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYERS_CFG_FRAME_TAG_COUNTER_CTRL'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def read_layers_cfg_frame_tag_counter_ctrl(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYERS_CFG_FRAME_TAG_COUNTER_CTRL'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_layers_cfg_frame_tag_counter_ctrl_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYERS_CFG_FRAME_TAG_COUNTER_CTRL'],count = count, increment = False)
        
    
    
    
    async def write_layers_cfg_frame_tag_counter_trigger(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYERS_CFG_FRAME_TAG_COUNTER_TRIGGER'],value = value,increment = True,valueLength=4)
        if flush == True:
            await self.flush()
        
    
    async def read_layers_cfg_frame_tag_counter_trigger(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYERS_CFG_FRAME_TAG_COUNTER_TRIGGER'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layers_cfg_frame_tag_counter_trigger_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYERS_CFG_FRAME_TAG_COUNTER_TRIGGER'],count = count, increment = True)
        
    
    
    
    async def write_layers_cfg_frame_tag_counter(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYERS_CFG_FRAME_TAG_COUNTER'],value = value,increment = True,valueLength=4)
        if flush == True:
            await self.flush()
        
    
    async def read_layers_cfg_frame_tag_counter(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYERS_CFG_FRAME_TAG_COUNTER'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layers_cfg_frame_tag_counter_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYERS_CFG_FRAME_TAG_COUNTER'],count = count, increment = True)
        
    
    
    
    async def write_layers_cfg_nodata_continue(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYERS_CFG_NODATA_CONTINUE'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def read_layers_cfg_nodata_continue(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYERS_CFG_NODATA_CONTINUE'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_layers_cfg_nodata_continue_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYERS_CFG_NODATA_CONTINUE'],count = count, increment = False)
        
    
    
    
    async def write_layers_sr_out(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYERS_SR_OUT'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def read_layers_sr_out(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYERS_SR_OUT'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_layers_sr_out_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYERS_SR_OUT'],count = count, increment = False)
        
    
    
    
    async def write_layers_sr_in(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYERS_SR_IN'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def read_layers_sr_in(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYERS_SR_IN'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_layers_sr_in_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYERS_SR_IN'],count = count, increment = False)
        
    
    
    
    async def write_layers_inj_ctrl(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYERS_INJ_CTRL'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def read_layers_inj_ctrl(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYERS_INJ_CTRL'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_layers_inj_ctrl_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYERS_INJ_CTRL'],count = count, increment = False)
        
    
    
    
    async def write_layers_inj_waddr(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYERS_INJ_WADDR'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def read_layers_inj_waddr(self, count : int = 0 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYERS_INJ_WADDR'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_layers_inj_waddr_raw(self, count : int = 0 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYERS_INJ_WADDR'],count = count, increment = False)
        
    
    
    
    async def write_layers_inj_wdata(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYERS_INJ_WDATA'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def read_layers_inj_wdata(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYERS_INJ_WDATA'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_layers_inj_wdata_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYERS_INJ_WDATA'],count = count, increment = False)
        
    
    
    
    async def read_layers_readout(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYERS_READOUT'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_layers_readout_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYERS_READOUT'],count = count, increment = False)
        
    
    
    
    async def read_layers_readout_read_size(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYERS_READOUT_READ_SIZE'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layers_readout_read_size_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYERS_READOUT_READ_SIZE'],count = count, increment = True)
        
    
    
    
    async def write_io_ctrl(self,value : int,flush = False):
        self.addWrite(register = self.Registers['IO_CTRL'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def read_io_ctrl(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['IO_CTRL'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_io_ctrl_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['IO_CTRL'],count = count, increment = False)
        
    
    
    
    async def write_io_led(self,value : int,flush = False):
        self.addWrite(register = self.Registers['IO_LED'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def read_io_led(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['IO_LED'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_io_led_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['IO_LED'],count = count, increment = False)
        
    
    
    
    async def write_gecco_sr_ctrl(self,value : int,flush = False):
        self.addWrite(register = self.Registers['GECCO_SR_CTRL'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def read_gecco_sr_ctrl(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['GECCO_SR_CTRL'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_gecco_sr_ctrl_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['GECCO_SR_CTRL'],count = count, increment = False)
        
    
    
    
    async def write_hk_conversion_trigger_match(self,value : int,flush = False):
        self.addWrite(register = self.Registers['HK_CONVERSION_TRIGGER_MATCH'],value = value,increment = True,valueLength=4)
        if flush == True:
            await self.flush()
        
    
    async def read_hk_conversion_trigger_match(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['HK_CONVERSION_TRIGGER_MATCH'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_hk_conversion_trigger_match_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['HK_CONVERSION_TRIGGER_MATCH'],count = count, increment = True)
        
    
    
    
    async def write_layers_cfg_frame_tag_counter_trigger_match(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYERS_CFG_FRAME_TAG_COUNTER_TRIGGER_MATCH'],value = value,increment = True,valueLength=4)
        if flush == True:
            await self.flush()
        
    
    async def read_layers_cfg_frame_tag_counter_trigger_match(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYERS_CFG_FRAME_TAG_COUNTER_TRIGGER_MATCH'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layers_cfg_frame_tag_counter_trigger_match_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYERS_CFG_FRAME_TAG_COUNTER_TRIGGER_MATCH'],count = count, increment = True)
        
    
