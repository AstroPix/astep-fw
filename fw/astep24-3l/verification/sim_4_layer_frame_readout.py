import os
import os.path
import sys

## Import simulation target driver
import astep24_3l_sim
import cocotb
import vip.astropix3
import vip.cctb
from cocotb.clock import Clock
from cocotb.triggers import Combine, Join, RisingEdge, Timer, with_timeout


async def print_layers_stats(dut, driver):
    for i in range(3):
        dut._log.info(f"-- Layer {i} stats")
        idle = await driver.getLayerStatIDLECounter(i)
        frames = await driver.getLayerStatFRAMECounter(i)
        errors = await driver.getLayerWrongLength(i)
        dut._log.info(f"---> IDLE={idle} bytes")
        dut._log.info(f"---> Frames={frames}")
        dut._log.info(f"---> Errors={errors}")


async def totalBytesFromAstropix(driver, layer):
    return (await driver.getLayerStatIDLECounter(layer)) + (
        await driver.getLayerStatFRAMECounter(layer)
    ) * 5


async def impl_test_layer_0_single_frame_noautoread_tssize(
    dut, asic, driver, tssize: int = 1
):
    
    forcedTSValue = [0xAD,0xBC,0xDE,0xFF,0xAC,0xEC,0xB1,0x12]
    
    ## Enable FPGA Timestamp counting
    await driver.layersConfigFPGATimestamp(
        enable=True,
        use_divider=False,
        use_tlu=False,
        flush=True,
        timestamp_size=tssize,
    )
    
    await Timer(1,units="us")
    currentTS = await driver.rfg.read_layers_fpga_timestamp_counter()
    

    dut._log.info(
        f"Timestamp size {tssize}, expecting {driver.fpgaTimeStampBytesCount} TS bytes ({driver.fpgaTimeStampBytesCount * 8} bits), currentTS={hex(currentTS)}"
    )

    ## Drive a frame from the ASIC with autoread disabled, it should timeout
    try:
        await with_timeout(asic.generateTestFrame(length=5), 200, "us")
    except:
        pass

    dut._log.info(
        "Current Readout size after untapped frame: %d",
        await driver.readoutGetBufferSize(),
    )
    assert await driver.readoutGetBufferSize() == 0, "Before "

    ## Now Restart frame generator with a Readout in parallel
    ## Then Write 10 NULL Bytes, which will be enought to readout the whole frame
    generator = cocotb.start_soon(asic.generateTestFrame(length=5))
    await Timer(1, units="us")
    await driver.setLayerConfig(
        layer=0, reset=False, hold=False, autoread=False, chipSelect=True, flush=True
    )
    await driver.writeSPIBytesToLane(lane=0, bytes=[0xAB] * 10)
    await generator.join()

    ## Check That one Frame was seen with the correct size depending on the timestamp size
    await Timer(50, units="us")
    assert await driver.readoutGetBufferSize() == 7 + driver.fpgaTimeStampBytesCount

    assert (await totalBytesFromAstropix(driver, 0)) == asic.spiSlave.bytesOut, (
        "IDLE + Number of Frame bytes must be equal to number of bytes out of model"
    )

    ## Now Get readout buffer to be able to run that method a second time
    ## Also check that the dataframe second byte has the correct length
    bytes = await driver.readoutReadBytes(7 + driver.fpgaTimeStampBytesCount)

    dut._log.info(f"Frame Bytes: {bytes}")
    assert bytes[0] == 1 + 5 + driver.fpgaTimeStampBytesCount, (
        "Data Frame Length should equal 5 bytes of astropix and X bytes of timestamp depending on the configuration"
    )
    
    ## Check that the TS value is not the forced one
    assert bytes[-driver.fpgaTimeStampBytesCount:] != forcedTSValue[:driver.fpgaTimeStampBytesCount]
    
    ## Run the readout a second time with forced value
    await driver.layersConfigFPGATimestamp(
        enable=True,
        use_divider=False,
        use_tlu=False,
        timestamp_size=tssize,
        forced_value = True,
        flush=True,
    )
    await driver.layersConfigFPGATimestampForcedValue(int.from_bytes(bytes=forcedTSValue,byteorder="big"))
    
    generator = cocotb.start_soon(asic.generateTestFrame(length=5))
    await driver.writeSPIBytesToLane(lane=0, bytes=[0xAB] * 10)
    await generator.join()
    
    assert await driver.readoutGetBufferSize() == 7 + driver.fpgaTimeStampBytesCount
    bytes = await driver.readoutReadBytes(7 + driver.fpgaTimeStampBytesCount)
    
    assert bytes[0] == 1 + 5 + driver.fpgaTimeStampBytesCount, (
        "Data Frame Length should equal 5 bytes of astropix and X bytes of timestamp depending on the configuration"
    )
    
    ## Check that the TS value is the forced one 
    assert bytes[-driver.fpgaTimeStampBytesCount:] == forcedTSValue[-driver.fpgaTimeStampBytesCount:]
    
    await print_layers_stats(dut, driver)

    await Timer(50, units="us")


@cocotb.test(timeout_time=2, timeout_unit="ms")
async def test_layer_0_single_frame_noautoread(dut):
    ## Driver, asic, clock+reset
    asic = vip.astropix3.Astropix3Model(dut=dut, lane = 0 ,  chipID=1)
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    await impl_test_layer_0_single_frame_noautoread_tssize(dut, asic, driver, 1)


@cocotb.test(timeout_time=5, timeout_unit="ms")
async def test_layer_0_single_frame_noautoread_alltssizes(dut):
    """Gets a single frame on layer 0 with all possible timestamp sizes"""

    ## Driver, asic, clock+reset
    asic = vip.astropix3.Astropix3Model(dut=dut, lane = 0 ,  chipID=1)
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    for i in range(4):
        await impl_test_layer_0_single_frame_noautoread_tssize(dut, asic, driver, i)


@cocotb.test(timeout_time=2, timeout_unit="ms")
async def test_layer_0_double_frame_noautoread(dut):
    """"""
    ## Driver, asic, clock+reset
    asic = vip.astropix3.Astropix3Model(dut=dut,lane = 0 ,  chipID=1)
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Enable FPGA Timestamp counting
    await driver.layersConfigFPGATimestamp(
        enable=True,
        use_divider=False,
        use_tlu=False,
        flush=True,
    )

    dut._log.info(
        "Current Readout size after untapped frame: %d",
        await driver.readoutGetBufferSize(),
    )
    assert await driver.readoutGetBufferSize() == 0

    ## Now Restart frame generator with a Readout in parallel
    ## Then Write 10 NULL Bytes, which will be enought to readout the whole frame
    generator = cocotb.start_soon(asic.generateTestFrame(length=5, framesCount=2))
    await Timer(1, units="us")
    await driver.setLayerConfig(
        layer=0, reset=False, hold=False, autoread=False, chipSelect=True, flush=True
    )
    await driver.writeSPIBytesToLane(lane=0, bytes=[0x00] * 16)
    await generator.join()

    ## Check That two Frames were seen
    await Timer(50, units="us")
    assert (
        await driver.readoutGetBufferSize() == (7 + driver.fpgaTimeStampBytesCount) * 2
    )

    ## Readout and print
    bytes = await driver.readoutReadBytes((7 + driver.fpgaTimeStampBytesCount) * 2)
    for b in bytes:
        print(f"B={hex(b)}")

    await print_layers_stats(dut, driver)

    assert (await totalBytesFromAstropix(driver, 0)) == asic.spiSlave.bytesOut, (
        "IDLE + Number of Frame bytes must be equal to number of bytes out of model"
    )

    await Timer(50, units="us")


@cocotb.test(timeout_time=2, timeout_unit="ms",skip=True)
async def test_layer_0_spi_stall(dut):
    """Generate more than 66 bytes + 16 spi buffer frames to make the buffers stall"""

    ## Driver, asic, clock+reset
    asic = vip.astropix3.Astropix3Model(dut=dut,lane = 0 ,  chipID=1)
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)
    await Timer(50, units="us")

    ## Enable FPGA Timestamp counting
    await driver.layersConfigFPGATimestamp(
        enable=True,
        use_divider=False,
        use_tlu=False,
        flush=True,
    )

    await driver.setLayerConfig(
        layer=0, reset=False, hold=False, autoread=False, chipSelect=True, flush=True
    )

    ## Drive enough bytes to output buffer to trigger readout
    #
    # readoutLength = await driver.readoutGetBufferSize()
    framesCount = 25
    bytesToSendToSPI = int(framesCount * 5) + 10
    generator = cocotb.start_soon(
        asic.generateTestFrame(length=5, framesCount=framesCount)
    )
    totalBytes = 0
    for i in range(int(bytesToSendToSPI / 12) + 1):
        await driver.writeSPIBytesToLane(lane=0, bytes=[0xAB] * (12))
        await Timer(25, units="us")
        readoutLength = await driver.readoutGetBufferSize()
        if readoutLength == 66:
            await driver.readoutReadBytes(32)
            totalBytes += 32

    await generator.join()

    totalBytes += await driver.readoutGetBufferSize()

    dut._log.info(f"Number of total bytes={totalBytes},expected={framesCount * 11}")
    assert totalBytes == framesCount * 11, (
        "Number of total bytes={totalBytes},expected={framesCount*11}"
    )
    assert (await totalBytesFromAstropix(driver, 0)) == asic.spiSlave.bytesOut, (
        "IDLE + Number of Frame bytes must be equal to number of bytes out of model"
    )

    await Timer(50, units="us")


@cocotb.test(timeout_time=2, timeout_unit="ms")
async def test_layer_0_single_frame_autoread(dut):
    """"""

    ## Driver, asic, clock+reset
    asic = vip.astropix3.Astropix3Model(dut=dut, lane = 0 ,  chipID=1)
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Enable FPGA Timestamp counting
    await driver.layersConfigFPGATimestamp(
        enable=True,
        use_divider=False,
        use_tlu=False,
        flush=True,
    )

    assert await driver.readoutGetBufferSize() == 0

    ##########

    ## Start the layer, with autoread enabled
    await driver.setLayerConfig(
        layer=0, reset=False, hold=False, autoread=True, flush=True
    )

    ## Drive a frame from the ASIC
    ## This method returns when the frame was outputed from the chip spi slave
    await asic.generateTestFrame(length=5)

    ## Wait a bit for autoread to be finished and get the bytes from the readout
    await Timer(250, units="us")
    readoutLength = await driver.readoutGetBufferSize()

    ## Length should be 6 Frame bytes (header + 5 payload), +2 Readout Frame Header + 4 Timestamp bytes = 12
    assert readoutLength == 11

    await print_layers_stats(dut, driver)
    dut._log.info(f"Number of bytes out of Astropix model: {asic.spiSlave.bytesOut}")

    assert (await totalBytesFromAstropix(driver, 0)) == asic.spiSlave.bytesOut, (
        "IDLE + Number of Frame bytes must be equal to number of bytes out of model"
    )
    await Timer(50, units="us")


@cocotb.test(timeout_time=2, timeout_unit="ms")
async def test_layer_0_two_differentframes_autoread(dut):
    """"""

    ## Driver, asic, clock+reset
    asic = vip.astropix3.Astropix3Model(dut=dut, lane = 0 ,  chipID=1)
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Enable FPGA Timestamp counting
    await driver.layersConfigFPGATimestamp(
        enable=True,
        use_divider=False,
        use_tlu=False,
        flush=True,
    )

    assert await driver.readoutGetBufferSize() == 0

    ##########

    ## Start the layer, with autoread enabled
    await driver.setLayerConfig(
        layer=0, reset=False, hold=False, autoread=True, flush=True
    )

    ## Drive a frame from the ASIC
    ## This method returns when the frame was outputed from the chip spi slave
    await asic.generateTestFrame(length=5)
    await Timer(1, units="us")
    await asic.generateTestFrame(
        length=5
    )  # This should run during the extra runtime of autoread

    ## Wait a bit and get the bytes from the readout
    await Timer(200, units="us")
    readoutLength = await driver.readoutGetBufferSize()

    ## Length should be 6 Frame bytes (header + 5 payload), +2 Readout Frame Header + 4 Timestamp bytes = 12
    assert readoutLength == 2 * 11

    await print_layers_stats(dut, driver)
    assert (await totalBytesFromAstropix(driver, 0)) == asic.spiSlave.bytesOut, (
        "IDLE + Number of Frame bytes must be equal to number of bytes out of model"
    )

    await Timer(50, units="us")


@cocotb.test(timeout_time=2, timeout_unit="ms", skip=True)
async def test_layer_0_single_frame_autoread_stopduringread(dut):
    """"""

    ## Driver, asic, clock+reset
    asic = vip.astropix3.Astropix3Model(dut=dut, lane = 0 ,  chipID=1)
    await vip.cctb.common_clock_reset(dut)
    await Timer(5, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Enable FPGA Timestamp counting
    await driver.layersConfigFPGATimestamp(
        enable=True,
        use_divider=False,
        use_tlu=False,
        flush=True,
    )

    assert await driver.readoutGetBufferSize() == 0

    ##########

    ## Start the layer, with autoread enabled
    await driver.setLayerConfig(
        layer=0, reset=False, hold=False, autoread=True, flush=True
    )
    await driver.setLayerConfig(
        layer=1, reset=False, hold=False, autoread=True, flush=True
    )
    await Timer(10, units="us")

    ## Drive a frame from the ASIC
    ## This method returns when the frame was outputed from the chip spi slave
    await asic.generateTestFrame(length=5)

    ## Wait for interrupt to be 1 to generate new frames directly
    await RisingEdge(dut.layer_0_interruptn)
    await Timer(2, units="us")
    await asic.generateTestFrame(length=5)

    ## Wait a bit and generate another frame
    await Timer(20, units="us")
    await asic.generateTestFrame(length=5)

    ## Generate a wrong length frame
    await Timer(20, units="us")
    await asic.generateTestFrame(length=5)

    await Timer(20, units="us")
    await driver.setLayerConfig(
        layer=0, reset=False, hold=True, autoread=True, flush=True
    )
    await driver.setLayerConfig(
        layer=0, reset=False, hold=True, autoread=False, flush=True
    )
    # await Timer(50, units="us")
    # readoutLength = await driver.readoutGetBufferSize()

    ## Length should be 6 Frame bytes (header + 5 payload), +2 Readout Frame Header + 4 Timestamp bytes = 12
    # assert readoutLength == 12

    await Timer(50, units="us")


@cocotb.test(timeout_time=2, timeout_unit="ms")
async def test_layer_0_readout_large_buffer(dut):
    """Generate some data frames and make a large read in parallel to check if the data comes in full frames or with empty between"""
    
    ## Driver, asic, clock+reset
    asic = vip.astropix3.Astropix3Model(dut=dut,lane = 0 ,  chipID=1)
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Enable FPGA Timestamp counting
    forcedTSValue = [0xAD,0xBC,0xDE,0xFF,0xAC,0xEC,0xB1,0x12]
    await driver.layersConfigFPGATimestamp(
        enable=True,
        use_divider=False,
        use_tlu=False,
        forced_value = True,
        flush=True,
    )
    await driver.layersConfigFPGATimestampForcedValue(int.from_bytes(bytes=forcedTSValue,byteorder="big"))
    
    await driver.readoutConfigure(packet_mode = False)

    dut._log.info(
        "Current Readout size after untapped frame: %d",
        await driver.readoutGetBufferSize(),
    )
    assert await driver.readoutGetBufferSize() == 0

    ## Now Restart frame generator with a Readout in parallel
    ## Ise autoread to make FW produce frames while we are reading out
    generator = cocotb.start_soon(asic.generateTestFrame(length=5, framesCount=4))
    await Timer(1, units="us")
    await driver.setLayerConfig(
        layer=0, reset=False, hold=False, autoread=True, chipSelect=True, flush=True
    )
    
    ## Readout and print
    bytes = await driver.readoutReadBytes(256)
    for b in bytes:
        print(f"B={hex(b)}")

    await print_layers_stats(dut, driver)
    
    await generator.join()

    
    await Timer(50, units="us")

@cocotb.test(timeout_time=2, timeout_unit="ms")
async def test_3_layers_single_frame(dut):
    """Send A single frame to all layers after each other"""

    ## Create ASIC Models
    asics = []
    asics.append(vip.astropix3.Astropix3Model(dut=dut, lane = 0 ,  chipID=1))
    asics.append(vip.astropix3.Astropix3Model(dut=dut, lane =1 ,  chipID=2))
    asics.append(vip.astropix3.Astropix3Model(dut=dut, lane = 2 ,  chipID=3))

    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Enable FPGA Timestamp counting
    await driver.layersConfigFPGATimestamp(
        enable=True,
        use_divider=False,
        use_tlu=False,
        flush=True,
    )

    #########

    ## Start the layers, with autoread enabled
    await driver.setLayerConfig(
        layer=0, reset=False, hold=False, autoread=True, flush=False
    )
    await driver.setLayerConfig(
        layer=1, reset=False, hold=False, autoread=True, flush=False
    )
    await driver.setLayerConfig(
        layer=2, reset=False, hold=False, autoread=True, flush=True
    )

    ## Generate Frame to all after each other
    for i in range(3):
        await asics[i].generateTestFrame(length=5)

    ## Wait a bit and get the bytes size
    await Timer(100, units="us")
    readoutLength = await driver.readoutGetBufferSize()

    ## Each frame length is 11 (see previous test) -> We should have 3*11
    assert readoutLength == 3 * 11

    await Timer(10, units="us")

    dut._log.info("Done Frames in sequence")

    ## Flush readout buffer
    await driver.readoutReadBytes(3 * 11)

    ###########

    ## Same test but generate the frames in parallel
    await Timer(50, units="us")

    ## Generate Frames
    tasks = []
    for i in range(3):
        tasks.append(cocotb.start_soon(asics[i].generateTestFrame(length=5)))

    Combine(*tasks)
    dut._log.info("Sequencing tasks done")

    ## Wait a bit and check the readout size
    await Timer(100, units="us")
    readoutLength = await driver.readoutGetBufferSize()
    assert readoutLength == 3 * 11

    await print_layers_stats(dut, driver)

    await Timer(50, units="us")


@cocotb.test(timeout_time=2, timeout_unit="ms")
async def test_3_layers_multiple_frames_parallel(dut):
    """Send A single frame to all layers after each other"""

    ## Create ASIC Models
    asics = []
    asics.append(vip.astropix3.Astropix3Model(dut=dut, lane = 0 ,  chipID=1))
    asics.append(vip.astropix3.Astropix3Model(dut=dut,  lane = 1 ,  chipID=2))
    asics.append(vip.astropix3.Astropix3Model(dut=dut,  lane = 2 ,  chipID=3))

    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Enable FPGA Timestamp counting
    await driver.layersConfigFPGATimestamp(
        enable=True,
        use_divider=False,
        use_tlu=False,
        flush=True,
    )

    await print_layers_stats(dut, driver)

    await Timer(50, units="us")

    ## Start the layers, with autoread enabled
    await driver.setLayerConfig(
        layer=0, reset=False, hold=False, autoread=True, flush=False
    )
    await driver.setLayerConfig(
        layer=1, reset=False, hold=False, autoread=True, flush=False
    )
    await driver.setLayerConfig(
        layer=2, reset=False, hold=False, autoread=True, flush=True
    )
    # await Timer(100, units="us") # Wait after enabling for resets to be done, makes waveform easier

    ## Generate Frames
    counts = 10
    tasks = []
    for i in range(3):
        tasks.append(
            cocotb.start_soon(asics[i].generateTestFrame(length=5, framesCount=counts))
        )

    Combine(*tasks)
    dut._log.info("Sequencing tasks done")

    ## Wait a bit and check the readout size - also read the bytes to avoid buffer getting full, since simulation buffer size is small (16)
    totalBytes = 0
    for i in range(6):
        await Timer(20, units="us")
        readoutLength = await driver.readoutGetBufferSize()
        if readoutLength == 0:
            break
        totalBytes += readoutLength
        await driver.readoutReadBytes(readoutLength)

    await print_layers_stats(dut, driver)

    # assert readoutLength == 3*11*counts , f"Expected {3*11*counts} bytes"
    assert totalBytes == 3 * 11 * counts, (
        f"Expected {3 * 11 * counts} bytes, got {totalBytes} bytes"
    )

    await Timer(50, units="us")
