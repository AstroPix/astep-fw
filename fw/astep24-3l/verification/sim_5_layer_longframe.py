


import sys
import os
import os.path
import logging
import random 
import cocotb
from cocotb.triggers    import Timer,RisingEdge,Join,Combine,with_timeout
from cocotb.clock       import Clock

import vip.cctb
import vip.astropix3


## Import simulation target driver
import astep24_3l_sim


async def run_gen_read_test(dut,driver,asic,autoRead:bool,framesCount:int,frameLength:int,pause:bool=False):

    ## Config Layer 
    await driver.setLayerConfig(layer = 0, reset = False, hold = False, autoread = autoRead , flush = True )
    #await driver.configureLayerSPIFrequency(targetFrequencyHz=400000,flush=True)

    if not autoRead:
        await driver.layersSelectSPI(flush=True)

    #framesCount = 150 
    #frameLength=5
    finalBytesCount = framesCount * (frameLength+1+4+2)

    dut._log.info(f"-- Start, expected {finalBytesCount} bytes")

    ## Now Restart frame generator with a Readout in parallel
    ## Then Write 10 NULL Bytes, which will be enought to readout the whole frame
    generator = cocotb.start_soon(asic.generateTestFrame(length = frameLength,framesCount=framesCount,isRandom=True,pause=pause))
    await Timer(150,units="us")  
    
    #await generator.join()
    #await RisingEdge(dut.layer_0_interruptn)

    ## Readout the frames a bit wild, until there are no bytes anymore
    finished = False
    readBytes = []
    mosiTimeout = 0
    while not finished:

        ## If not autoread, we need to send some bytes to trigger reading out random.randint(16,24)
        if not autoRead:
            await driver.writeLayerBytes(layer=0,bytes=[0x00]*32,flush=True)
            await Timer(5,units="us")
            mosiTimeout = 150
            while mosiTimeout>0 and (await driver.getLayerMOSIBytesCount(layer=0) > 0):
                await Timer(1,units="us") 
                mosiTimeout -= 1


        # get readoutsize 
        bufferSize = await driver.readoutGetBufferSize()

        ## If not autoread, read the buffer full, otherwise the next writeLayerBytes might write too much and hang if the buffers are full
        ## If the buffersize is 0 without autoread, it is finished
        if not autoRead:
            if bufferSize == 0:
                finished = True 
            else:
                readBytes.extend(await driver.readoutReadBytes(bufferSize))
        else:
            # read a random number of bytes
            randReadCount = random.randint(int(bufferSize/2),bufferSize)
            dut._log.info(f"Reading {randReadCount} bytes from buffer ({bufferSize} bytes available)")
            readBytes.extend(await driver.readoutReadBytes(randReadCount))

            # if nothing else to read, finish
            await Timer(random.randint(5,50),units="us")
            if await driver.readoutGetBufferSize() == 0:
                dut._log.info(f"No bytes left to read")
                finished = True

    dut._log.info(f"Read {len(readBytes)} bytes, expected {finalBytesCount} bytes")
    if (len(readBytes) != finalBytesCount):
        for b in readBytes:
            dut._log.info(f"{hex(b)}")
    assert(len(readBytes) == finalBytesCount)

    ## Now Decode Check
    ##########
    asic.decodeCheckASTEPFramesStaticLength(readBytes,framesCount,frameLength)

    idleBytes = await driver.getLayerStatIDLECounter(0)
    dut._log.info(f"-- DONE Read {len(readBytes)} bytes, expected {finalBytesCount} bytes, IDLE Bytes={idleBytes} --")

    if not autoRead:
        await driver.layersDeselectSPI(flush=True)


@cocotb.test(timeout_time = 500 , timeout_unit = "ms")
async def test_layer_0_longframe_with_pause_no_autoread(dut):

    ## Reset and driver
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    asic = vip.astropix3.Astropix3Model(dut = dut, prefix = "layer_0" , chipID = 1)
    logging.getLogger("cocotb.astep24_3l_top.uart_tx").setLevel(logging.WARN)
    logging.getLogger("cocotb.astep24_3l_top.uart_rx").setLevel(logging.WARN)
    logging.getLogger("vip.spi").setLevel(logging.WARN)

    await run_gen_read_test(dut,driver,asic,autoRead=False,framesCount=5,frameLength=4,pause=True)
    await Timer(250,units="us")

@cocotb.test(timeout_time = 500 , timeout_unit = "ms")
async def test_layer_0_longframe_with_pause_autoread(dut):

    ## Reset and driver
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    asic = vip.astropix3.Astropix3Model(dut = dut, prefix = "layer_0" , chipID = 1)
    logging.getLogger("cocotb.astep24_3l_top.uart_tx").setLevel(logging.WARN)
    logging.getLogger("cocotb.astep24_3l_top.uart_rx").setLevel(logging.WARN)
    logging.getLogger("vip.spi").setLevel(logging.WARN)

    await Timer(250,units="us")
    await run_gen_read_test(dut,driver,asic,autoRead=True,framesCount=2,frameLength=4,pause=True)
    await Timer(250,units="us")

@cocotb.test(timeout_time = 500 , timeout_unit = "ms")
async def test_layer_0_longframe_with_pause_dualmode(dut):

    ## Reset and driver
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    asic = vip.astropix3.Astropix3Model(dut = dut, prefix = "layer_0" , chipID = 1)
    logging.getLogger("cocotb.astep24_3l_top.uart_tx").setLevel(logging.WARN)
    logging.getLogger("cocotb.astep24_3l_top.uart_rx").setLevel(logging.WARN)
    logging.getLogger("vip.spi").setLevel(logging.WARN)

    await Timer(250,units="us")
    await run_gen_read_test(dut,driver,asic,autoRead=False,framesCount=200,frameLength=4,pause=True)
    await Timer(250,units="us")
    await run_gen_read_test(dut,driver,asic,autoRead=True,framesCount=2,frameLength=4,pause=True)
    await Timer(250,units="us")

@cocotb.test(timeout_time = 500 , timeout_unit = "ms")
async def test_layer_0_longframe_longtest(dut):

    asic = vip.astropix3.Astropix3Model(dut = dut, prefix = "layer_0" , chipID = 1)
    logging.getLogger("cocotb.astep24_3l_top.uart_tx").setLevel(logging.WARN)
    logging.getLogger("cocotb.astep24_3l_top.uart_rx").setLevel(logging.WARN)
    logging.getLogger("vip.spi").setLevel(logging.WARN)

    ## Reset and driver
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    await run_gen_read_test(dut,driver,asic,autoRead=False,framesCount=2,frameLength=4,pause=True)
    await Timer(250,units="us")
    await run_gen_read_test(dut,driver,asic,autoRead=False,framesCount=30,frameLength=4,pause=True)
    await Timer(250,units="us")
    await run_gen_read_test(dut,driver,asic,autoRead=False,framesCount=150,frameLength=4,pause=True)
    await Timer(250,units="us")
    await run_gen_read_test(dut,driver,asic,autoRead=False,framesCount=250,frameLength=4,pause=True)
    await Timer(250,units="us")

    await run_gen_read_test(dut,driver,asic,autoRead=True,framesCount=2,frameLength=4,pause=True)
    await Timer(250,units="us")
    await run_gen_read_test(dut,driver,asic,autoRead=True,framesCount=80,frameLength=4,pause=True)
    await Timer(250,units="us")
    await run_gen_read_test(dut,driver,asic,autoRead=True,framesCount=250,frameLength=4,pause=True)
    await Timer(250,units="us")

    return
