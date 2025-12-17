
"""Read Firmware ID via SPI"""
import asyncio 
import drivers.boards


import rfg.io.spi 
rfg.io.spi.debug()

async def main():
    print("Hi")

    ## Open CMOD on Beagle
    boardDriver = drivers.boards.getCMODSPIDriver("/dev/spidev1.0","/dev/gpiochip2",19)
    await boardDriver.open()

    id      = await  boardDriver.readFirmwareID()
    version = await boardDriver.readFirmwareVersion()

    print(f"Firmware ID: 0x{hex(id)}")
    print(f"Firmware Version: {str(version)}")


asyncio.run(main())

