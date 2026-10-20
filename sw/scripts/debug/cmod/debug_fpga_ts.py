import asyncio 
import time
## Load Board
##############
import drivers.boards
import drivers.astropix.asic

async def debug_test():

    driver = drivers.boards.getCMODUartDriver("COM6")
    await driver.open()
    await driver.layersConfigFPGATimestampFrequency(1000000, flush=True)
    await driver.layersConfigFPGATimestamp(enable=True, use_divider=True, use_tlu=False, force_lsb_0=False, forced_value=True, flush=False)
    await driver.layersConfigFPGATimestamp(enable=True, use_divider=True, use_tlu=False, force_lsb_0=False, forced_value=False, flush=True)
    for i in range(1):
        ts = await driver.rfg.read_layers_fpga_timestamp_counter_raw(count=4)
        print(ts, int.from_bytes(ts, byteorder="little"))
        #await asyncio.sleep(.1)
        time.sleep(.1)
        ts = await driver.rfg.read_layers_fpga_timestamp_counter_raw(count=4)
        print(ts, int.from_bytes(ts, byteorder="little"))
    print(await driver.rfg.read_layers_fpga_timestamp_divider_match())

if __name__ == "__main__":
    asyncio.run(debug_test())