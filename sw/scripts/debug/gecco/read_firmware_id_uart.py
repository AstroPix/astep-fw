import asyncio
import drivers.astep.serial
import drivers.boards





async def mainasync():
    port = "/dev/ttyUSB0"
    print(f"Opening port: {port}")
    boardDriver = drivers.boards.getGeccoUARTDriver(port)
    await boardDriver.open()

    id =      await boardDriver.readFirmwareID()
    version = await boardDriver.readFirmwareVersion()

    print(f"Firmware ID: {hex(id)}")
    print(f"Firmware Version: {str(version)}")
        


asyncio.run(mainasync())
