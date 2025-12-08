from decimal import Decimal, ROUND_HALF_EVEN

import asyncio
from deprecated import deprecated

## These aren't explicitly used... does importing do something???
from ... import rfg.io
from ... import rfg.core


class Housekeeping():

    def __init__(self,driver,rfg):
        self.rfg = rfg
        self.driver = driver

    async def readFirmwareVersion(self, queue : int = 0):
        return (await self.rfg.read_hk_firmware_version())
    async def readFirmwareID(self, queue : int = 0):
        """"""
        return (await self.rfg.read_hk_firmware_id())

    async def checkFirmwareVersionAfter(self,v):
        return (await self.readFirmwareVersion()) >= v


    def convertBytesToFPGATemperature(self, rawTemperature) -> float:
        rawTemperature = (int.from_bytes(rawTemperature,'little')) >> 4
        floatTemperature =  rawTemperature * 503.975 / 4096 - 273.15
        return Decimal(floatTemperature).quantize(Decimal('.01'), rounding=ROUND_HALF_EVEN)

    def convertBytesToVCCInt(self,rawVccit) -> float :
        rawVccit = (int.from_bytes(rawVccit,'little')) >> 4
        return Decimal(rawVccit  / 4096 * 3 ).quantize(Decimal('.01'), rounding=ROUND_HALF_EVEN)


    async def setXADCSampleFrequence(self,targetClock,refClock  : int = 60000000):
        await self.rfg.write_hk_conversion_trigger_match(int(refClock/targetClock),flush = True)

    async def getXADCSampleFrequence(self,refClock : int = 60000000):
        matchRegister = await self.rfg.read_hk_conversion_trigger_match()
        dividedClock = float(refClock) / float(matchRegister)
        return Decimal(dividedClock).quantize(Decimal('.01'), rounding=ROUND_HALF_EVEN)

    async def readFPGATemperature(self, targetQueue: str | None = None ) ->  float:
        """Returns FPGA Temperature as Float -> Doc: https://docs.xilinx.com/r/en-US/ug480_7Series_XADC/Analog-Inputs "Temperature Sensor" """

        rawTemperature = await self.rfg.read_hk_xadc_temperature(targetQueue = targetQueue) >> 4
        floatTemperature =  rawTemperature * 503.975 / 4096 - 273.15
        return Decimal(floatTemperature).quantize(Decimal('.01'), rounding=ROUND_HALF_EVEN)

    async def readFPGATemperatureRaw(self, targetQueue: str | None = None ) ->  float:
        """Doc: https://docs.xilinx.com/r/en-US/ug480_7Series_XADC/Analog-Inputs "Temperature Sensor" """
        return await self.rfg.read_hk_xadc_temperature(targetQueue = targetQueue) >> 4


    async def readVCCInt(self, targetQueue: str | None = None) ->  float:
        """ https://docs.xilinx.com/r/en-US/ug480_7Series_XADC/Analog-Inputs "Power Supply Sensor" """

        vccint = ( (await self.rfg.read_hk_xadc_vccint(targetQueue = targetQueue)) >> 4 ) / 4096 * 3
        return Decimal(vccint).quantize(Decimal('.01'), rounding=ROUND_HALF_EVEN)

    @deprecated("Use Method in Board Driver")
    async def configureHKSPIFrequency(self, targetFrequencyHz : int , flush = False):
        """Calculated required divider to reach the provided target SPI clock frequency"""
        coreFrequency = self.driver.getFPGACoreFrequency()
        divider = int( coreFrequency / (2 * targetFrequencyHz))
        assert divider >=1 and divider <=255 , (f"Divider {divider} is too high, min. clock frequency: {int(coreFrequency/2/255)}")
        await self.configureHKSPIDivider(divider,flush)

    @deprecated("Use Method in Board Driver")
    async def configureHKSPIDivider(self, divider:int , flush = False):
        await self.rfg.spi_hk_ckdivider(divider,flush)

    async def writeADCDACBytes(self,values : bytearray) :
        return await self.rfg.write_hk_adcdac_mosi_fifo_bytes(values,flush=True)

    async def getADCBytesCount(self):
        """Returns the number of bytes in the ADC MISO buffer"""
        return await self.rfg.read_hk_adc_miso_fifo_read_size()

    async def readADCBytes(self,count:int=1) :
        return await self.rfg.read_hk_adc_miso_fifo_raw(count)



    async def configureSPI(self,adc:bool,dac:bool):
        """Selects ADC/DAC and configures CPOL/CPHA of SPI master accordingly"""
        assert not(adc and dac),"ADC and DAC cannot be selected at the same time"

        # First Change the CPOL/CPHA configuration, then after a little wait select the Chip
        # Reason is that if all bits change at once, the clock polarity will change after chip select is low, creating an edge that will be wrongly interpreted

        # Change CPOL/CPHA
        # For ADC: CPOL=1, CPHA=0 - Output on falling edge, capture on rising edge
        # For DAC: CPOL=0, CPHA=1  - Output on rising edge, capture on Falling edge
        regval = 0
        if adc is True:
            regval |= (1 << 2) | (0 << 3)
        else:
            regval |= (0 << 2) | (1 << 3)

        await self.rfg.write_hk_ctrl(regval,True)

    async def selectSPI(self,adc:bool,dac:bool):
        """Selects ADC/DAC and configures CPOL/CPHA of SPI master accordingly"""
        assert not(adc and dac),"ADC and DAC cannot be selected at the same time"

        # First Change the CPOL/CPHA configuration, then after a little wait select the Chip
        # Reason is that if all bits change at once, the clock polarity will change after chip select is low, creating an edge that will be wrongly interpreted

        # Change CPOL/CPHA
        regval = await self.rfg.read_hk_ctrl()
        regval |= adc | (dac << 1)

        await self.rfg.write_hk_ctrl(regval,True)
