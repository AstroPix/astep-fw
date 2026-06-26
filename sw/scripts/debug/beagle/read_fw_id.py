
"""Read Firmware ID via SPI"""
import asyncio 
import drivers.boards
import struct

import rfg.io.spi 
rfg.io.spi.debug()
#rfg.io.spi.warning()

async def main():
    print("Hi")

    ## Open CMOD on Beagle
    boardDriver = drivers.boards.getCMODSPIDriver("/dev/spidev1.0","/dev/gpiochip2",19)
    await boardDriver.open()

    id      = await boardDriver.readFirmwareID()
    version = await boardDriver.readFirmwareVersion()

    print(f"Firmware ID: {hex(id)}")
    print(f"Firmware Version: {str(version)}")

    ofile = open("/home/debian/astep-fw/sw/data/readfwid.bin", "wb")
    ofile.write(struct.pack("i", id))
    ofile.write(struct.pack("i", version))
    ofile.close()

    await boardDriver.close()


asyncio.run(main())

