import asyncio 
import time
import binascii
## Load Board
##############
import drivers.boards
import drivers.astropix.asic

async def debug_loopback():
    driver = drivers.boards.getCMODUartDriver("COM6")
    await driver.open()
    await driver.layersConfigFPGATimestampFrequency(1000000, flush=True)
    await driver.layersConfigFPGATimestamp(enable=True, use_divider=True, use_tlu=False, force_lsb_0=False, forced_value=False, flush=True)
    await driver.enableLayersReadout(layerlst=[0, 1, 2], autoread=True, flush=True)
    lbmodel = driver.getLoopbackModelForLayer(0)
    await lbmodel.enableLoopback()
    for lane in range(3):
        await driver.writeSPIBytesToLane(lane=lane, bytes=[0x00]*5)
    bufferSize = await driver.readoutGetBufferSize()
    print(f"Buffer size: {bufferSize}, status={await driver.getLayerStatus(0)}")
    buffer = await driver.readoutReadBytes(bufferSize)
    print(binascii.hexlify(buffer))
    print("Writing valid hit")
    time.sleep(1)
    for _ in range(20): await lbmodel.writeMISOBytes(bytes.fromhex("3d3d3d3d040a56019e048a5501923d3d3d3d"), flush=True)
    print(f"Reading: {await lbmodel.readMISOBytesSize()}")
    # await driver.writeSPIBytesToLane(lane=0, bytes=[0x00]*50)
    # while(nbytes := await driver.getLayerMOSIBytesCount(0)) > 0:
    #     print(f"{nbytes} B still to be written.")
    bufferSize = await driver.readoutGetBufferSize()
    print(f"Buffer size: {bufferSize}, status={await driver.getLayerStatus(0)}")
    buffer = await driver.readoutReadBytes(bufferSize)
    print(binascii.hexlify(buffer))
    await lbmodel.disableLoopback()

async def debug_loopback_test():
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

async def debug_test():
    row, col = 10, 10
    driver = drivers.boards.getCMODUartDriver("COM6")
    await driver.open()
    #await driver.setSampleClock(True)
    await driver.setTimestampClock(enable=True)
    await driver.layersConfigFPGATimestampFrequency(targetFrequencyHz=1000000)
    await driver.layersConfigFPGATimestamp(enable=True,use_divider=True,use_tlu=False)
    await driver.configureLayerSPIFrequency(1000000)
    driver.setupASIC(version=3,lane=0,chipsPerLane=4,configFile="scripts/config/quadchip_allOff.yml")
    await driver.rfg.write_layers_cfg_nodata_continue(8)
    driver.asics[0].enable_pixel(3, row, col)
    driver.asics[0].enable_inj_col(3, col)
    driver.asics[0].enable_inj_row(3, row)
    injector = driver.getInjector()
    injector.period = 100
    injector.clkdiv = 300
    injector.initdelay = 100
    injector.cycle = 2 # 2 injections total (?) ...
    injector.pulsesperset = 1
    await driver.ioSetInjectionToChip(enable=True, flush=True)
    await driver.resetLayers()
    await driver.disableLayersReadout(True)
    await driver.layersSelectSPI(flush=True)
    await driver.writeRoutingFrame(lane=0, firstChipID=0)
    await driver.layersDeselectSPI(flush=True)
    for chip in range(4):
        await driver.layersSelectSPI(flush=True)  # Set CS
        await driver.writeSPIAsicConfig(lane=0, targetChip=chip)
        await driver.layersDeselectSPI(flush=True)  # Unset CS
    # Test 1
    bufferSize = await driver.readoutGetBufferSize()
    print(f"Buffer size after config: {bufferSize}, status={await driver.getLayerStatus(0)}")
    readout = await driver.readoutReadBytes(bufferSize)
    if len(readout)>0: print(binascii.hexlify(readout))
    # Test 2
    await driver.enableLayersReadout([0], False, True)
    await driver.writeSPIBytesToLane(lane=0, bytes=[0x00] * 6)
    bufferSize = await driver.readoutGetBufferSize()
    print(f"Buffer size after first read: {bufferSize}, status={await driver.getLayerStatus(0)}")
    readout = await driver.readoutReadBytes(bufferSize)
    if len(readout)>0: print(binascii.hexlify(readout))
    # Test 3
    for _ in range(5):
        await injector.start()
        time.sleep(.5)
        await injector.stop()
        await driver.writeSPIBytesToLane(lane=0, bytes=[0x00] * 9)
        bufferSize = await driver.readoutGetBufferSize()
        print(f"Buffer size after injection: {bufferSize}, status={await driver.getLayerStatus(0)}")
        readout = await driver.readoutReadBytes(bufferSize)
        if len(readout)>0: print(binascii.hexlify(readout))
    # Closeout
    await driver.disableLayersReadout(True)
    await driver.close()




if __name__ == "__main__":
    asyncio.run(debug_loopback())