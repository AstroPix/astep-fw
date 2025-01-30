
import asyncio 

## Load Board
##############
import drivers.boards
import drivers.astropix.asic

## Open UART Driver for Gecco:
##  - Change this to the correct COM Port for the system
##  - On Linux, leave empty to filter FTDI Com ports and use the first available
##  - For CMOD -> change to drivers.boards.getCMODUartDriver("COM4")
#boardDriver = drivers.boards.getGeccoFTDIDriver()
boardDriver = drivers.boards.getCMODUartDriver("COM4")
boardDriver.open()

## Read Firmware version
## This call should run in asyncio
id =      asyncio.run(boardDriver.readFirmwareID())
version = asyncio.run(boardDriver.readFirmwareVersion())

#print(f"Firmware ID: 0x{hex(id)}")
print(f"Firmware Version: {str(version)}")