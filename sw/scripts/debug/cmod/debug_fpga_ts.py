import asyncio 

## Load Board
##############
import drivers.boards
import drivers.astropix.asic

async def debug_test():

    driver = drivers.boards.getCMODUartDriver("COM6")
    await driver.open()
    await driver.layersConfigFPGATimestampFrequency(1000000, flush=True)
    await driver.layersConfigFPGATimestamp(
            enable=True,
            use_divider=True,
            use_tlu=False,
            flush=True,
    )
    #
    ts = await driver.rfg.read_layers_fpga_timestamp_counter(count=4)
    print(ts)
    await asyncio.sleep(.1)
    ts = await driver.rfg.read_layers_fpga_timestamp_counter(count=4)
    print(ts)
    print(await driver.rfg.read_layers_fpga_timestamp_divider_match())

if __name__ == "__main__":
    asyncio.run(debug_test())