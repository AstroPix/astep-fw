import logging
import os
import os.path
import random
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


async def run_gen_read_test(
    dut,
    driver,
    asic,
    autoRead: bool,
    framesCount: int,
    frameLength: int,
    timestamp_size:int = 1,
    pause: bool = False,
):
    ##
    await driver.resetLayerStatCounters(0)
    await Timer(20, "us")

    ## Config Layer
    await driver.setLayerConfig(
        layer=0, reset=False, hold=False, autoread=autoRead, flush=True
    )
    # await driver.configureLayerSPIFrequency(targetFrequencyHz=400000,flush=True)

    try:
        if not autoRead:
            await driver.layersSelectSPI(flush=True)

        # framesCount = 150
        # frameLength=5
        finalBytesCount = framesCount * (frameLength + driver.fpgaTimeStampBytesCount + 2)

        dut._log.info(
            f"-- Start, expected {finalBytesCount} bytes, autoread={autoRead} (frames={framesCount},frame length={frameLength},single fw frame length={frameLength + 1 + driver.fpgaTimeStampBytesCount + 2} bytes)"
        )

        ## Now Restart frame generator with a Readout in parallel
        ## Then Write 10 NULL Bytes, which will be enought to readout the whole frame
        generator = cocotb.start_soon(
            asic.generateTestFrame(
                length=frameLength, framesCount=framesCount, isRandom=True, pause=pause
            )
        )
        await Timer(150, units="us")

        # await generator.join()
        # await RisingEdge(dut.layer_0_interruptn)

        ## Readout the frames a bit wild, until there are no bytes anymore
        finished = False
        readBytes = []
        mosiTimeout = 0
        while not finished:
            ## If not autoread, we need to send some bytes to trigger reading out random.randint(16,24)
            if not autoRead:
                await driver.writeSPIBytesToLane(lane=0, bytes=[0x00] * 32)
                await Timer(500, units="ns")
                mosiTimeout = 20
                while mosiTimeout > 0 and (
                    await driver.getLayerMOSIBytesCount(layer=0) > 0
                ):
                    await Timer(500, units="ns")
                    mosiTimeout -= 1
                # Get current available bytes
                # currentBytesAvailable = await driver.getLayerMOSIBytesCount(layer=0)
                # while mosiTimeout>0 and (currentBytesAvailable == 0):
                #    await Timer(500,units="ns")
                #    mosiTimeout -= 1
                #    if currentBytesAvailable == 0:
                #        mosiTimeout -= 1
                #    else:
                #        currentBytesAvailable = await driver.getLayerMOSIBytesCount(layer=0)

            # get readoutsize
            bufferSize = await driver.readoutGetBufferSize()

            ## If not autoread, read the buffer full, otherwise the next writeLayerBytes might write too much and hang if the buffers are full
            ## If the buffersize is 0 without autoread, it is finished
            if not autoRead:
                if bufferSize == 0:
                    finished = True
                    # Wait a bit here, since the SPI master might still be active
                    await Timer(100, units="us")
                else:
                    readBytes.extend(await driver.readoutReadBytes(bufferSize))

            else:
                # read a random number of bytes
                randReadCount = random.randint(int(bufferSize / 2), bufferSize)
                dut._log.info(
                    f"Reading {randReadCount} bytes from buffer ({bufferSize} bytes available)"
                )
                readBytes.extend(await driver.readoutReadBytes(randReadCount))

                # if nothing else to read, finish
                await Timer(random.randint(5, 50), units="us")
                if await driver.readoutGetBufferSize() == 0:
                    dut._log.info(f"No bytes left to read")
                    finished = True

            dut._log.info(
                f"--- (autoread={autoRead}) Read {len(readBytes)}/{finalBytesCount} bytes, {(int(len(readBytes) / finalBytesCount * 100)) / 100 * 100}%"
            )

        await generator.join()
        dut._log.info(f"Read {len(readBytes)} bytes, expected {finalBytesCount} bytes")
        # if (len(readBytes) != finalBytesCount):
        #    for b in readBytes:
        #        dut._log.info(f"{hex(b)}")
        assert len(readBytes) == finalBytesCount

        # Print stats after end to check for extra bytes
        await Timer(10, units="us")
        await print_layers_stats(dut, driver)

        # assert (await driver.getLayerStatFRAMECounter(0) == 0) , "After finishing getting frames, 0 frames should be left"

        assert await driver.readoutGetBufferSize() == 0, (
            "No Data in buffer after finishing"
        )

        ## Now Decode Check
        ##########
        asic.decodeCheckASTEPFramesStaticLength(readBytes, framesCount, frameLength,driver.fpgaTimeStampBytesCount)

        idleBytes = await driver.getLayerStatIDLECounter(0)
        dut._log.info(
            f"-- DONE Read {len(readBytes)} bytes, expected {finalBytesCount} bytes, IDLE Bytes={idleBytes} --"
        )

    finally:
        if not autoRead:
            await driver.layersDeselectSPI(flush=True)


async def run_gen_read_test_multi(
    dut,
    driver,
    asics,
    autoRead: bool,
    framesCount: int,
    frameLength: int,
    pause: bool = False,
    minBuffSize=0,
):
    ## Config Layer
    for i in range(len(asics)):
        await driver.setLayerConfig(
            layer=i,
            reset=False,
            hold=False,
            autoread=autoRead,
            chipSelect=(not autoRead),
            flush=True,
        )
        await driver.resetLayerStatCounters(i)
        await Timer(20, "us")
    # await driver.configureLayerSPIFrequency(targetFrequencyHz=400000,flush=True)

    try:
        # if not autoRead:
        #    await driver.layersSelectSPI(flush=True)

        # framesCount = 150
        # frameLength=5
        finalBytesCount = framesCount * (frameLength + 4 + 2) * len(asics)

        dut._log.info(
            f"-- Start, expected {finalBytesCount} bytes, autoread={autoRead} (frames={framesCount},frame length={frameLength},single fw frame length={frameLength + 4 + 2} bytes)"
        )

        ## Now Restart frame generator with a Readout in parallel
        ## Then Write 10 NULL Bytes, which will be enought to readout the whole frame
        generators = []
        for i in range(len(asics)):
            generators.append(
                cocotb.start_soon(
                    asics[i].generateTestFrame(
                        length=frameLength,
                        framesCount=framesCount,
                        isRandom=True,
                        pause=pause,
                    )
                )
            )
        await Timer(150, units="us")

        # await generator.join()
        # await RisingEdge(dut.layer_0_interruptn)

        ## Readout the frames a bit wild, until there are no bytes anymore
        finished = False
        
        readBytes = []
        mosiTimeout = 0
        while not finished:
            
            timeoutInWriteSPI = False 
            
            ## If not autoread, we need to send some bytes to trigger reading out random.randint(16,24)
            ## This method might timeout because of buffers filling, just keep going if that's the case
            if not autoRead:
                for i in range(len(asics)):
                    try:
                        await driver.writeSPIBytesToLane(lane=i, bytes=[0x00] * 16,waitForLastChunk=False)
                    except RuntimeError:
                        dut._log.warn("Timeout in write SPI")
                        timeoutInWriteSPI = True
                        pass

                #await Timer(500, units="ns")
                #for i in range(len(asics)):
                #    mosiTimeout = 20
                #    while mosiTimeout > 0 and (
                #        await driver.getLayerMOSIBytesCount(layer=i) > 0
                #    ):
                #        await Timer(500, units="ns")
                #        mosiTimeout -= 1

            # get readoutsize
            bufferSize = await driver.readoutGetBufferSize()
            dut._log.info(
                f"Buffer size available: {bufferSize}"
            )

            ## If not autoread, read the buffer full, otherwise the next writeLayerBytes might write too much and hang if the buffers are full
            ## If the buffersize is 0 without autoread, it is finished
            if not autoRead:
                if bufferSize == 0:
                    finished = True
                    # Wait a bit here, since the SPI master might still be active
                    await Timer(100, units="us")
                else:
                    # Read Bytes, if a timeout happened, wait a bit and read again to help avoid too much timeout 
                    readBytes.extend(await driver.readoutReadBytes(bufferSize))
                    if timeoutInWriteSPI is True: 
                        await Timer(100, units="us")
                        bufferSize2 = await driver.readoutGetBufferSize()
                        while (bufferSize2>0):
                            dut._log.warn(f"Second buffer read of {bufferSize2} bytes in no autoread to avoid timeouts")
                            readBytes.extend(await driver.readoutReadBytes(bufferSize2))
                            bufferSize += bufferSize2
                        

            else:
                # Read only if number of bytes reached
                # If not reached, wait and request size again, if nothing moves, it's probably end of test so read everything
                # If minBuffSize is 0 just read a random number of bytes from the actual buffer size
                randReadCount = random.randint(int(bufferSize / 2), bufferSize)
                if minBuffSize > 0:
                    if (bufferSize) < minBuffSize:
                        await Timer(5, units="us")
                        if (await driver.readoutGetBufferSize()) == bufferSize:
                            dut._log.info(
                                f"Buffer size not changing, probably the end of test"
                            )
                            randReadCount = bufferSize
                            # readBytes.extend(await driver.readoutReadBytes(bufferSize))
                    else:
                        # Enough data in buffer, can read
                        randReadCount = minBuffSize

                # read a random number of bytes
                # randReadCount = random.randint(int(bufferSize/2),bufferSize)
                dut._log.info(
                    f"Reading {randReadCount} bytes from buffer ({bufferSize} bytes available)"
                )
                readBytes.extend(await driver.readoutReadBytes(randReadCount))

                # if nothing else to read, finish
                await Timer(2, units="us")
                if await driver.readoutGetBufferSize() == 0:
                    dut._log.info(f"No bytes left to read")
                    finished = True

            percentRead = (int(len(readBytes) / finalBytesCount * 100)) / 100 * 100
            dut._log.info(
                f"--- (autoread={autoRead}) Read {len(readBytes)}/{finalBytesCount} bytes, {percentRead}%"
            )

            ## If more than 100%, fail
            assert percentRead <= 100, "Error in Read, more than 100% data read"

        # await generator.join()
        await Combine(*generators)
        dut._log.info(f"Read {len(readBytes)} bytes, expected {finalBytesCount} bytes")
        # if (len(readBytes) != finalBytesCount):
        #    for b in readBytes:
        #        dut._log.info(f"{hex(b)}")
        assert len(readBytes) == finalBytesCount

        await print_layers_stats(dut, driver)

        # Check no daata is available in buffer after test finishes
        assert await driver.readoutGetBufferSize() == 0, (
            "No Data in buffer after finishing"
        )

        ## Now Decode Check
        ##########
        # asic.decodeCheckASTEPFramesStaticLength(readBytes,framesCount,frameLength)
        for i in range(len(asics)):
            idleBytes = await driver.getLayerStatIDLECounter(i)
            dut._log.info(
                f"-- DONE Read {len(readBytes)} bytes, expected {finalBytesCount} bytes, IDLE Bytes={idleBytes} --"
            )

    finally:
        if not autoRead:
            await driver.layersDeselectSPI(flush=True)
        await print_layers_stats(dut, driver)


@cocotb.test(timeout_time=500, timeout_unit="ms")
async def test_layer_0_longframe_with_pause_no_autoread(dut):
    """"""

    ## Reset and driver
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

    asic = vip.astropix3.Astropix3Model(dut=dut,  lane = 0 ,  chipID=1)
    logging.getLogger("cocotb.astep24_3l_top.uart_tx").setLevel(logging.WARN)
    logging.getLogger("cocotb.astep24_3l_top.uart_rx").setLevel(logging.WARN)
    logging.getLogger("vip.spi").setLevel(logging.WARN)

    await run_gen_read_test(
        dut, driver, asic, autoRead=False, framesCount=5, frameLength=5, pause=True
    )
    await Timer(250, units="us")


@cocotb.test(timeout_time=500, timeout_unit="ms")
async def test_layer_0_longframe_with_pause_autoread(dut):
    """"""

    ## Reset and driver
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

    asic = vip.astropix3.Astropix3Model(dut=dut,  lane = 0 ,  chipID=1)
    logging.getLogger("cocotb.astep24_3l_top.uart_tx").setLevel(logging.WARN)
    logging.getLogger("cocotb.astep24_3l_top.uart_rx").setLevel(logging.WARN)
    logging.getLogger("vip.spi").setLevel(logging.WARN)

    await Timer(250, units="us")
    await run_gen_read_test(
        dut, driver, asic, autoRead=True, framesCount=2, frameLength=5, pause=True
    )
    await Timer(250, units="us")

    for x in range(5):
        await Timer(250, units="us")
        await run_gen_read_test(
            dut, driver, asic, autoRead=True, framesCount=10, frameLength=5, pause=True
        )
        await Timer(250, units="us")

    await Timer(250, units="us")
    await run_gen_read_test(
        dut, driver, asic, autoRead=True, framesCount=25, frameLength=5, pause=True
    )
    await Timer(250, units="us")

    await Timer(250, units="us")
    await run_gen_read_test(
        dut, driver, asic, autoRead=True, framesCount=750, frameLength=5, pause=True
    )
    await Timer(250, units="us")


@cocotb.test(timeout_time=500, timeout_unit="ms")
async def test_layer_0_longframe_with_pause_dualmode(dut):
    """"""

    ## Reset and driver
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

    asic = vip.astropix3.Astropix3Model(dut=dut,  lane = 0 ,  chipID=1)
    logging.getLogger("cocotb.astep24_3l_top.uart_tx").setLevel(logging.WARN)
    logging.getLogger("cocotb.astep24_3l_top.uart_rx").setLevel(logging.WARN)
    logging.getLogger("vip.spi").setLevel(logging.WARN)

    await Timer(250, units="us")
    await run_gen_read_test(
        dut, driver, asic, autoRead=False, framesCount=200, frameLength=5, pause=True
    )
    await Timer(250, units="us")
    await run_gen_read_test(
        dut, driver, asic, autoRead=True, framesCount=10, frameLength=5, pause=True
    )
    await Timer(250, units="us")


@cocotb.test(timeout_time=500, timeout_unit="ms")
async def test_layer_0_longframe_longtest(dut):
    """"""

    asic = vip.astropix3.Astropix3Model(dut=dut, lane = 0 ,  chipID=1)
    logging.getLogger("cocotb.astep24_3l_top.uart_tx").setLevel(logging.WARN)
    logging.getLogger("cocotb.astep24_3l_top.uart_rx").setLevel(logging.WARN)
    logging.getLogger("vip.spi").setLevel(logging.WARN)

    ## Reset and driver
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Enable FPGA Timestamp counting
    tsSize = 3
    await driver.layersConfigFPGATimestamp(
        enable=True,
        use_divider=False,
        use_tlu=False,
        timestamp_size = tsSize,
        flush=True,
    )

    #await run_gen_read_test_multi(
    #    dut, driver, [asic], autoRead=False, framesCount=65, frameLength=5, pause=True
    #)
    #return 
    # 
    await run_gen_read_test(
        dut, driver, asic, autoRead=True, framesCount=4096, frameLength=5,timestamp_size=tsSize, pause=True
    )
    await run_gen_read_test(
        dut, driver, asic, autoRead=True, framesCount=4096, frameLength=5,timestamp_size=tsSize, pause=False
    )
    
    
    
    await Timer(10, units="us")
    return 
    await run_gen_read_test(
        dut, driver, asic, autoRead=False, framesCount=2, frameLength=5, pause=True
    )
    await Timer(250, units="us")

    await run_gen_read_test(
        dut, driver, asic, autoRead=True, framesCount=80, frameLength=5, pause=True
    )
    await Timer(250, units="us")

    await run_gen_read_test(
        dut, driver, asic, autoRead=False, framesCount=250, frameLength=5, pause=True
    )
    await Timer(250, units="us")

    await run_gen_read_test(
        dut, driver, asic, autoRead=False, framesCount=150, frameLength=5, pause=True
    )
    await Timer(250, units="us")

    await run_gen_read_test(
        dut, driver, asic, autoRead=True, framesCount=2, frameLength=5, pause=True
    )
    await Timer(250, units="us")

    await run_gen_read_test(
        dut, driver, asic, autoRead=False, framesCount=30, frameLength=5, pause=True
    )
    await Timer(250, units="us")

    await run_gen_read_test(
        dut, driver, asic, autoRead=True, framesCount=250, frameLength=5, pause=True
    )
    await Timer(250, units="us")

    return


@cocotb.test(timeout_time=500, timeout_unit="ms")
async def test_layers_parallel_autoread_noautoread(dut):
    """"""

    asics = []
    for i in range(3):
        asics.append(
            vip.astropix3.Astropix3Model(dut=dut,  lane = i ,  chipID=i+1)
        )

    logging.getLogger("cocotb.astep24_3l_top.uart_tx").setLevel(logging.WARN)
    logging.getLogger("cocotb.astep24_3l_top.uart_rx").setLevel(logging.WARN)
    logging.getLogger("vip.spi").setLevel(logging.WARN)

    ## Reset and driver
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)
    await driver.configureLayerSPIFrequency(10000000)

    ## Enable FPGA Timestamp counting
    await driver.layersConfigFPGATimestamp(
        enable=True,
        use_divider=False,
        use_tlu=False,
        flush=True,
    )
    await Timer(250, units="us")
    
     
    
    
    await run_gen_read_test_multi(
        dut, driver, asics, autoRead=True, framesCount=20, frameLength=5, pause=True
    )
    await Timer(250, units="us")

    await run_gen_read_test_multi(
        dut, driver, asics, autoRead=True, framesCount=250, frameLength=5, pause=True
    )
    await Timer(250, units="us")
    
    await run_gen_read_test_multi(
        dut, driver, asics, autoRead=False, framesCount=150, frameLength=5, pause=True
    )
    await Timer(250, units="us")

    await run_gen_read_test_multi(
        dut, driver, asics, autoRead=True, framesCount=800, frameLength=5, pause=True
    )
    await Timer(250, units="us")

    

    await run_gen_read_test_multi(
        dut, driver, asics, autoRead=False, framesCount=2, frameLength=5, pause=True
    )
    await Timer(250, units="us")

    await run_gen_read_test_multi(
        dut, driver, asics, autoRead=False, framesCount=30, frameLength=5, pause=True
    )
    await Timer(250, units="us")
    
    await run_gen_read_test_multi(
        dut, driver, asics, autoRead=False, framesCount=250, frameLength=5, pause=True
    )
    await Timer(250, units="us")


    return

    await run_gen_read_test_multi(
        dut, driver, asics, autoRead=True, framesCount=20, frameLength=5, pause=True
    )
    await Timer(250, units="us")

    await run_gen_read_test_multi(
        dut, driver, asics, autoRead=True, framesCount=250, frameLength=5, pause=True
    )
    await Timer(250, units="us")

    await run_gen_read_test_multi(
        dut, driver, asics, autoRead=True, framesCount=800, frameLength=5, pause=True
    )
    await Timer(250, units="us")

    return
    await run_gen_read_test(
        dut, driver, asic, autoRead=False, framesCount=2, frameLength=4, pause=True
    )
    await Timer(250, units="us")
    await run_gen_read_test(
        dut, driver, asic, autoRead=False, framesCount=30, frameLength=4, pause=True
    )
    await Timer(250, units="us")
    await run_gen_read_test(
        dut, driver, asic, autoRead=False, framesCount=150, frameLength=4, pause=True
    )
    await Timer(250, units="us")
    await run_gen_read_test(
        dut, driver, asic, autoRead=False, framesCount=250, frameLength=4, pause=True
    )
    await Timer(250, units="us")

    await run_gen_read_test(
        dut, driver, asic, autoRead=True, framesCount=2, frameLength=4, pause=True
    )
    await Timer(250, units="us")
    await run_gen_read_test(
        dut, driver, asic, autoRead=True, framesCount=80, frameLength=4, pause=True
    )
    await Timer(250, units="us")
    await run_gen_read_test(
        dut, driver, asic, autoRead=True, framesCount=250, frameLength=4, pause=True
    )
    await Timer(250, units="us")

    return
