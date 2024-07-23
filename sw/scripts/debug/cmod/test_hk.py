
import asyncio 

## Load Board
##############
import drivers.boards
import drivers.astropix.asic

## Open UART Driver for CMOD
driver = drivers.boards.getCMODUartDriver("COM4")
driver.open()

"""
## Read Firmware version
id =      asyncio.run(driver.readFirmwareID())
version = asyncio.run(driver.readFirmwareVersion())
print(f"Firmware Version: {str(version)}")
"""

## ADC test
print("TESTING ADC")
asyncio.run(driver.houseKeeping.selectADC())
asyncio.run(driver.houseKeeping.writeADCDACBytes([0x04,0x00]))
print("Writing ADC bytes [0xAB,0xCD]")
adcBytesCount = asyncio.run(driver.houseKeeping.getADCBytesCount())
print(f"Got ACD bytes count = {adcBytesCount}")
adcBytes = asyncio.run(driver.houseKeeping.readADCBytes(adcBytesCount) )
print(f"Got ADC bytes {adcBytes}")
    # After writting the bytes to the ADC, there should be 2 bytes in the ADC read buffer, since we wrote two bytes out.

"""
## DAC test
print("TESTING DAC")
asyncio.run(driver.houseKeeping.selectDAC())
asyncio.run(driver.houseKeeping.writeADCDACBytes([0x00,0x00]) )
print("Writing DAC bytes [0x07,0xFF]")

"""
