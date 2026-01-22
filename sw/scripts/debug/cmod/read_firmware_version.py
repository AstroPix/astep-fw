
import asyncio 

## Load Board
##############
import drivers.boards
import drivers.astropix.asic


async def test_fpga():
    boardDriver = drivers.boards.getCMODUartDriver("COM6")
    await boardDriver.open()
    
    print('ID')
    id =      await boardDriver.readFirmwareID()
    print(f"Firmware ID: {hex(id)}")
    version = await boardDriver.readFirmwareVersion()
    print(f"Firmware Version: {str(version)}")

    await boardDriver.close()

if __name__ == "__main__":
    asyncio.run(test_fpga())

