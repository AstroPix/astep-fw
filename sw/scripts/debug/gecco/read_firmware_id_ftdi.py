import asyncio
import drivers.astep.serial
import drivers.boards
import rfg.io.ftdi

rfg.io.ftdi.debug()

async def mainasync():
    boardDriver =  drivers.boards.getGeccoFTDIDriver()
    await boardDriver.open()

    id =      await boardDriver.readFirmwareID()
    version = await boardDriver.readFirmwareVersion()

    print(f"Firmware ID: {hex(id)}")
    print(f"Firmware Version: {str(version)}")


asyncio.run(mainasync())
