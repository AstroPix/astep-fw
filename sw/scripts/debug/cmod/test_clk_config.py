
import asyncio 

## Load Board
##############
import drivers.boards
import drivers.astropix.asic


async def test_fpga():

    boardDriver = drivers.boards.getCMODUartDriver("COM26")
    await boardDriver.open()

    #configuring ToA Divider. Clock Divider of 0 yields a 40 MHz Clock

    #True clock Divider is 40 MHz/(1+DIV). 1 MHz TS with a clock divider of 39
    #Clock Divider can be modified either before or after setTimestampClock without any issues (but we will prefer before)
    await boardDriver.configureLayersToADivider(15, flush=True)
    await boardDriver.setTimestampClock(enable=True, flush=True)

    await asyncio.sleep(10)

    await boardDriver.setTimestampClock(enable=False, flush=True)
    await boardDriver.close()

if __name__ == "__main__":
    asyncio.run(test_fpga())