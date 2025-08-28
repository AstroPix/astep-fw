import asyncio
import drivers.astep.serial
import drivers.boards





async def mainasync():
    port = drivers.astep.serial.getFirstCOMPort()
    if port is None:
        print("No COM Ports")
    else:
        print(f"Opening port: {port}")
        boardDriver = drivers.boards.getGeccoUARTDriver("/dev/ttyUSB0")
        await boardDriver.open()

        id =      await boardDriver.readFirmwareID()
        version = await boardDriver.readFirmwareVersion()

        print(f"Firmware ID: {hex(id)}")
        print(f"Firmware Version: {str(version)}")


asyncio.run(mainasync())
