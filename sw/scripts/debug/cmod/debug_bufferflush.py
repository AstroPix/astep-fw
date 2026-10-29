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
    await driver.layersConfigFPGATimestamp(enable=True, use_divider=True, use_tlu=False, force_lsb_0=False, forced_value=False, flush=True)
    await driver.enableLayersReadout(layerlst=[0, 1, 2], autoread=True, flush=True)
    lbmodel = driver.getLoopbackModelForLayer(1)
    await lbmodel.enableLoopback()
    print("Writing valid hit")
    time.sleep(1)
    #await lbmodel.writeMISOBytes(bytes.fromhex("bcbcbcbc040a56019e048a550192bcbcbcbc"), flush=True)
    print(f"Reading: {await lbmodel.readMISOBytesSize()}")
    bufferSize = await driver.readoutGetBufferSize()
    print(f"Buffer size: {bufferSize}")
    buffer = await driver.readoutReadBytes(bufferSize)
    print(type(buffer))
    await lbmodel.disableLoopback()

if __name__ == "__main__":
    asyncio.run(debug_test())