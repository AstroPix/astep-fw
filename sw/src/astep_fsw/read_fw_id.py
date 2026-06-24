
"""Read Firmware ID via SPI"""
import asyncio 
#import drivers.boards

#from ....vendor.icflow_hdl_240807.hdl_rfg_v1.python.rfg import io
from rfg import io
io.spi.debug()

from drivers import boards

async def main():
    print("Hi")

    ## Open CMOD on Beagle
    boardDriver = boards.getCMODSPIDriver("/dev/spidev1.0","/dev/gpiochip2",19)
    await boardDriver.open()

    id      = await boardDriver.readFirmwareID()
    version = await boardDriver.readFirmwareVersion()

    print(f"Firmware ID: 0x{hex(id)}")
    print(f"Firmware Version: {str(version)}")


asyncio.run(main())

