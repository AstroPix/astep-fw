import asyncio
import drivers.astep.serial
import drivers.boards

port = drivers.astep.serial.getFirstCOMPort()
if port is None: 
    print("No COM Ports")
else:
    boardDriver = drivers.boards.getGeccoUARTDriver(port)
    boardDriver.open()

    id =      asyncio.run(boardDriver.readFirmwareID())
    version = asyncio.run(boardDriver.readFirmwareVersion())

    print(f"Firmware ID: {hex(id)}")
    print(f"Firmware Version: {str(version)}")
    