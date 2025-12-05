

import logging
from rfg.core import AbstractRFG
from rfg.core import RFGRegister
logger = logging.getLogger(__name__)


def load_rfg():
    return main_rfg()


HK_FIRMWARE_ID = 0x0
HK_FIRMWARE_VERSION = 0x4
CHIP_VERSION = 0x8
CLOCK_CTRL = 0x9
HK_XADC_TEMPERATURE = 0xa
HK_XADC_VCCINT = 0xc
HK_CONVERSION_TRIGGER = 0xe
HK_STAT_CONVERSIONS_COUNTER = 0x12
HK_CTRL = 0x16
HK_ADCDAC_MOSI_FIFO = 0x17
HK_ADC_MISO_FIFO = 0x18
HK_ADC_MISO_FIFO_READ_SIZE = 0x19
SPI_LAYERS_CKDIVIDER = 0x1d
SPI_HK_CKDIVIDER = 0x1e
LAYER_0_CFG_CTRL = 0x1f
LAYER_1_CFG_CTRL = 0x20
LAYER_2_CFG_CTRL = 0x21
LAYER_0_STATUS = 0x22
LAYER_1_STATUS = 0x23
LAYER_2_STATUS = 0x24
LAYER_0_STAT_FRAME_COUNTER = 0x25
LAYER_1_STAT_FRAME_COUNTER = 0x29
LAYER_2_STAT_FRAME_COUNTER = 0x2d
LAYER_0_STAT_IDLE_COUNTER = 0x31
LAYER_1_STAT_IDLE_COUNTER = 0x35
LAYER_2_STAT_IDLE_COUNTER = 0x39
LAYER_0_STAT_WRONGLENGTH_COUNTER = 0x3d
LAYER_1_STAT_WRONGLENGTH_COUNTER = 0x41
LAYER_2_STAT_WRONGLENGTH_COUNTER = 0x45
LAYER_0_MOSI = 0x49
LAYER_0_MOSI_WRITE_SIZE = 0x4a
LAYER_1_MOSI = 0x4e
LAYER_1_MOSI_WRITE_SIZE = 0x4f
LAYER_2_MOSI = 0x53
LAYER_2_MOSI_WRITE_SIZE = 0x54
LAYER_0_LOOPBACK_MISO = 0x58
LAYER_0_LOOPBACK_MISO_WRITE_SIZE = 0x59
LAYER_1_LOOPBACK_MISO = 0x5d
LAYER_1_LOOPBACK_MISO_WRITE_SIZE = 0x5e
LAYER_2_LOOPBACK_MISO = 0x62
LAYER_2_LOOPBACK_MISO_WRITE_SIZE = 0x63
LAYER_0_LOOPBACK_MOSI = 0x67
LAYER_0_LOOPBACK_MOSI_READ_SIZE = 0x68
LAYER_1_LOOPBACK_MOSI = 0x6c
LAYER_1_LOOPBACK_MOSI_READ_SIZE = 0x6d
LAYER_2_LOOPBACK_MOSI = 0x71
LAYER_2_LOOPBACK_MOSI_READ_SIZE = 0x72
LAYERS_FPGA_TIMESTAMP_CTRL = 0x76
LAYERS_FPGA_TIMESTAMP_DIVIDER = 0x78
LAYERS_FPGA_TIMESTAMP_COUNTER = 0x7c
LAYERS_FPGA_TIMESTAMP_FORCED = 0x84
LAYERS_TLU_TRIGGER_DELAY = 0x8c
LAYERS_TLU_BUSY_DURATION = 0x8e
LAYERS_CFG_NODATA_CONTINUE = 0x90
LAYERS_SR_OUT = 0x91
LAYERS_SR_IN = 0x92
LAYERS_SR_RB_CTRL = 0x93
LAYERS_SR_CRC = 0x94
LAYERS_SR_BYTES = 0x9a
LAYERS_SR_BYTES_READ_SIZE = 0x9b
LAYERS_INJ_CTRL = 0x9f
LAYERS_INJ_WADDR = 0xa0
LAYERS_INJ_WDATA = 0xa1
LAYERS_READOUT_CTRL = 0xa2
LAYERS_READOUT = 0xa3
LAYERS_READOUT_READ_SIZE = 0xa4
IO_CTRL = 0xa8
IO_LED = 0xa9
GECCO_SR_CTRL = 0xaa
HK_CONVERSION_TRIGGER_MATCH = 0xab
LAYERS_FPGA_TIMESTAMP_DIVIDER_MATCH = 0xaf




class main_rfg(AbstractRFG):
    """Register File Entry Point Class"""
    
    
    class Registers(RFGRegister):
        HK_FIRMWARE_ID = 0x0
        HK_FIRMWARE_VERSION = 0x4
        CHIP_VERSION = 0x8
        CLOCK_CTRL = 0x9
        HK_XADC_TEMPERATURE = 0xa
        HK_XADC_VCCINT = 0xc
        HK_CONVERSION_TRIGGER = 0xe
        HK_STAT_CONVERSIONS_COUNTER = 0x12
        HK_CTRL = 0x16
        HK_ADCDAC_MOSI_FIFO = 0x17
        HK_ADC_MISO_FIFO = 0x18
        HK_ADC_MISO_FIFO_READ_SIZE = 0x19
        SPI_LAYERS_CKDIVIDER = 0x1d
        SPI_HK_CKDIVIDER = 0x1e
        LAYER_0_CFG_CTRL = 0x1f
        LAYER_1_CFG_CTRL = 0x20
        LAYER_2_CFG_CTRL = 0x21
        LAYER_0_STATUS = 0x22
        LAYER_1_STATUS = 0x23
        LAYER_2_STATUS = 0x24
        LAYER_0_STAT_FRAME_COUNTER = 0x25
        LAYER_1_STAT_FRAME_COUNTER = 0x29
        LAYER_2_STAT_FRAME_COUNTER = 0x2d
        LAYER_0_STAT_IDLE_COUNTER = 0x31
        LAYER_1_STAT_IDLE_COUNTER = 0x35
        LAYER_2_STAT_IDLE_COUNTER = 0x39
        LAYER_0_STAT_WRONGLENGTH_COUNTER = 0x3d
        LAYER_1_STAT_WRONGLENGTH_COUNTER = 0x41
        LAYER_2_STAT_WRONGLENGTH_COUNTER = 0x45
        LAYER_0_MOSI = 0x49
        LAYER_0_MOSI_WRITE_SIZE = 0x4a
        LAYER_1_MOSI = 0x4e
        LAYER_1_MOSI_WRITE_SIZE = 0x4f
        LAYER_2_MOSI = 0x53
        LAYER_2_MOSI_WRITE_SIZE = 0x54
        LAYER_0_LOOPBACK_MISO = 0x58
        LAYER_0_LOOPBACK_MISO_WRITE_SIZE = 0x59
        LAYER_1_LOOPBACK_MISO = 0x5d
        LAYER_1_LOOPBACK_MISO_WRITE_SIZE = 0x5e
        LAYER_2_LOOPBACK_MISO = 0x62
        LAYER_2_LOOPBACK_MISO_WRITE_SIZE = 0x63
        LAYER_0_LOOPBACK_MOSI = 0x67
        LAYER_0_LOOPBACK_MOSI_READ_SIZE = 0x68
        LAYER_1_LOOPBACK_MOSI = 0x6c
        LAYER_1_LOOPBACK_MOSI_READ_SIZE = 0x6d
        LAYER_2_LOOPBACK_MOSI = 0x71
        LAYER_2_LOOPBACK_MOSI_READ_SIZE = 0x72
        LAYERS_FPGA_TIMESTAMP_CTRL = 0x76
        LAYERS_FPGA_TIMESTAMP_DIVIDER = 0x78
        LAYERS_FPGA_TIMESTAMP_COUNTER = 0x7c
        LAYERS_FPGA_TIMESTAMP_FORCED = 0x84
        LAYERS_TLU_TRIGGER_DELAY = 0x8c
        LAYERS_TLU_BUSY_DURATION = 0x8e
        LAYERS_CFG_NODATA_CONTINUE = 0x90
        LAYERS_SR_OUT = 0x91
        LAYERS_SR_IN = 0x92
        LAYERS_SR_RB_CTRL = 0x93
        LAYERS_SR_CRC = 0x94
        LAYERS_SR_BYTES = 0x9a
        LAYERS_SR_BYTES_READ_SIZE = 0x9b
        LAYERS_INJ_CTRL = 0x9f
        LAYERS_INJ_WADDR = 0xa0
        LAYERS_INJ_WDATA = 0xa1
        LAYERS_READOUT_CTRL = 0xa2
        LAYERS_READOUT = 0xa3
        LAYERS_READOUT_READ_SIZE = 0xa4
        IO_CTRL = 0xa8
        IO_LED = 0xa9
        GECCO_SR_CTRL = 0xaa
        HK_CONVERSION_TRIGGER_MATCH = 0xab
        LAYERS_FPGA_TIMESTAMP_DIVIDER_MATCH = 0xaf
    
    
    
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
        
    
    
    
    async def write_chip_version(self,value : int,flush = False):
        self.addWrite(register = self.Registers['CHIP_VERSION'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def read_chip_version(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['CHIP_VERSION'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_chip_version_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['CHIP_VERSION'],count = count, increment = False)
        
    
    
    
    async def write_clock_ctrl(self,value : int,flush = False):
        self.addWrite(register = self.Registers['CLOCK_CTRL'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def read_clock_ctrl(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['CLOCK_CTRL'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_clock_ctrl_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['CLOCK_CTRL'],count = count, increment = False)
        
    
    
    
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
        
    
    
    
    async def write_layer_0_stat_wronglength_counter(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYER_0_STAT_WRONGLENGTH_COUNTER'],value = value,increment = True,valueLength=4)
        if flush == True:
            await self.flush()
        
    
    async def read_layer_0_stat_wronglength_counter(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_0_STAT_WRONGLENGTH_COUNTER'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_0_stat_wronglength_counter_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_0_STAT_WRONGLENGTH_COUNTER'],count = count, increment = True)
        
    
    
    
    async def write_layer_1_stat_wronglength_counter(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYER_1_STAT_WRONGLENGTH_COUNTER'],value = value,increment = True,valueLength=4)
        if flush == True:
            await self.flush()
        
    
    async def read_layer_1_stat_wronglength_counter(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_1_STAT_WRONGLENGTH_COUNTER'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_1_stat_wronglength_counter_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_1_STAT_WRONGLENGTH_COUNTER'],count = count, increment = True)
        
    
    
    
    async def write_layer_2_stat_wronglength_counter(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYER_2_STAT_WRONGLENGTH_COUNTER'],value = value,increment = True,valueLength=4)
        if flush == True:
            await self.flush()
        
    
    async def read_layer_2_stat_wronglength_counter(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYER_2_STAT_WRONGLENGTH_COUNTER'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layer_2_stat_wronglength_counter_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYER_2_STAT_WRONGLENGTH_COUNTER'],count = count, increment = True)
        
    
    
    
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
        
    
    
    
    async def write_layers_fpga_timestamp_ctrl(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYERS_FPGA_TIMESTAMP_CTRL'],value = value,increment = True,valueLength=2)
        if flush == True:
            await self.flush()
        
    
    async def read_layers_fpga_timestamp_ctrl(self, count : int = 2 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYERS_FPGA_TIMESTAMP_CTRL'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layers_fpga_timestamp_ctrl_raw(self, count : int = 2 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYERS_FPGA_TIMESTAMP_CTRL'],count = count, increment = True)
        
    
    
    
    async def write_layers_fpga_timestamp_divider(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYERS_FPGA_TIMESTAMP_DIVIDER'],value = value,increment = True,valueLength=4)
        if flush == True:
            await self.flush()
        
    
    async def read_layers_fpga_timestamp_divider(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYERS_FPGA_TIMESTAMP_DIVIDER'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layers_fpga_timestamp_divider_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYERS_FPGA_TIMESTAMP_DIVIDER'],count = count, increment = True)
        
    
    
    
    async def read_layers_fpga_timestamp_counter(self, count : int = 8 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYERS_FPGA_TIMESTAMP_COUNTER'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layers_fpga_timestamp_counter_raw(self, count : int = 8 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYERS_FPGA_TIMESTAMP_COUNTER'],count = count, increment = True)
        
    
    
    
    async def write_layers_fpga_timestamp_forced(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYERS_FPGA_TIMESTAMP_FORCED'],value = value,increment = True,valueLength=8)
        if flush == True:
            await self.flush()
        
    
    async def read_layers_fpga_timestamp_forced(self, count : int = 8 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYERS_FPGA_TIMESTAMP_FORCED'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layers_fpga_timestamp_forced_raw(self, count : int = 8 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYERS_FPGA_TIMESTAMP_FORCED'],count = count, increment = True)
        
    
    
    
    async def write_layers_tlu_trigger_delay(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYERS_TLU_TRIGGER_DELAY'],value = value,increment = True,valueLength=2)
        if flush == True:
            await self.flush()
        
    
    async def read_layers_tlu_trigger_delay(self, count : int = 2 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYERS_TLU_TRIGGER_DELAY'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layers_tlu_trigger_delay_raw(self, count : int = 2 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYERS_TLU_TRIGGER_DELAY'],count = count, increment = True)
        
    
    
    
    async def write_layers_tlu_busy_duration(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYERS_TLU_BUSY_DURATION'],value = value,increment = True,valueLength=2)
        if flush == True:
            await self.flush()
        
    
    async def read_layers_tlu_busy_duration(self, count : int = 2 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYERS_TLU_BUSY_DURATION'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layers_tlu_busy_duration_raw(self, count : int = 2 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYERS_TLU_BUSY_DURATION'],count = count, increment = True)
        
    
    
    
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
        
    
    
    
    async def write_layers_sr_rb_ctrl(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYERS_SR_RB_CTRL'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def read_layers_sr_rb_ctrl(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYERS_SR_RB_CTRL'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_layers_sr_rb_ctrl_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYERS_SR_RB_CTRL'],count = count, increment = False)
        
    
    
    
    async def read_layers_sr_crc(self, count : int = 6 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYERS_SR_CRC'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layers_sr_crc_raw(self, count : int = 6 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYERS_SR_CRC'],count = count, increment = True)
        
    
    
    
    async def read_layers_sr_bytes(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYERS_SR_BYTES'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_layers_sr_bytes_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYERS_SR_BYTES'],count = count, increment = False)
        
    
    
    
    async def read_layers_sr_bytes_read_size(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYERS_SR_BYTES_READ_SIZE'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layers_sr_bytes_read_size_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYERS_SR_BYTES_READ_SIZE'],count = count, increment = True)
        
    
    
    
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
        
    
    
    
    async def write_layers_readout_ctrl(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYERS_READOUT_CTRL'],value = value,increment = False,valueLength=1)
        if flush == True:
            await self.flush()
        
    
    async def read_layers_readout_ctrl(self, count : int = 1 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYERS_READOUT_CTRL'],count = count, increment = False , targetQueue = targetQueue), 'little') 
        
    
    async def read_layers_readout_ctrl_raw(self, count : int = 1 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYERS_READOUT_CTRL'],count = count, increment = False)
        
    
    
    
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
        
    
    
    
    async def write_layers_fpga_timestamp_divider_match(self,value : int,flush = False):
        self.addWrite(register = self.Registers['LAYERS_FPGA_TIMESTAMP_DIVIDER_MATCH'],value = value,increment = True,valueLength=4)
        if flush == True:
            await self.flush()
        
    
    async def read_layers_fpga_timestamp_divider_match(self, count : int = 4 , targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register = self.Registers['LAYERS_FPGA_TIMESTAMP_DIVIDER_MATCH'],count = count, increment = True , targetQueue = targetQueue), 'little') 
        
    
    async def read_layers_fpga_timestamp_divider_match_raw(self, count : int = 4 ) -> bytes: 
        return  await self.syncRead(register = self.Registers['LAYERS_FPGA_TIMESTAMP_DIVIDER_MATCH'],count = count, increment = True)
        
    
