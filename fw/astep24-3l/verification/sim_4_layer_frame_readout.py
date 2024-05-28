


import sys
import os
import os.path

import cocotb
from cocotb.triggers    import Timer,RisingEdge,Join,Combine,with_timeout
from cocotb.clock       import Clock

import vip.cctb
import vip.astropix3


## Import simulation target driver
import astep24_3l_sim


@cocotb.test(timeout_time = 0.8 , timeout_unit = "ms")
async def test_layer_0_single_frame_noautoread(dut):

    ## Driver, asic, clock+reset
    asic = vip.astropix3.Astropix3Model(dut = dut, prefix = "layer_0" , chipID = 1)
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Drive a frame from the ASIC with autoread disabled, it should timeout
    try:
        await with_timeout( asic.generateTestFrame(length = 5),200, 'us')
        assert True == False
    except:
        pass

   
    dut._log.info("Current Readout size after untapped frame: %d",await driver.readoutGetBufferSize())
    assert  await driver.readoutGetBufferSize() == 0

    ## Now Restart frame generator with a Readout in parallel
    ## Then Write 10 NULL Bytes, which will be enought to readout the whole frame
    generator = cocotb.start_soon(asic.generateTestFrame(length = 5))
    await Timer(1,units="us")  
    await driver.setLayerConfig(layer = 0, reset = False,hold=False,autoread=False,chipSelect=True,flush=True)
    await driver.writeLayerBytes( layer = 0 , bytes = [0x00]*10 , flush = True)
    await generator.join()

    ## Check That one Frame was seen
    await Timer(50, units="us")
    assert  await driver.readoutGetBufferSize() == 12
    await Timer(50, units="us")

@cocotb.test(timeout_time = 2 , timeout_unit = "ms")
async def test_layer_0_double_frame_noautoread(dut):

    ## Driver, asic, clock+reset
    asic = vip.astropix3.Astropix3Model(dut = dut, prefix = "layer_0" , chipID = 1)
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Drive a frame from the ASIC with autoread disabled, it should timeout
    try:
        await with_timeout( asic.generateTestFrame(length = 5,framesCount=2),50, 'us')
        assert True == False
    except:
        pass

   
    dut._log.info("Current Readout size after untapped frame: %d",await driver.readoutGetBufferSize())
    assert  await driver.readoutGetBufferSize() == 0

    ## Now Restart frame generator with a Readout in parallel
    ## Then Write 10 NULL Bytes, which will be enought to readout the whole frame
    generator = cocotb.start_soon(asic.generateTestFrame(length = 5,framesCount=2))
    await Timer(1,units="us")  
    await driver.setLayerConfig(layer = 0, reset = False,hold=False,autoread=False,chipSelect=True,flush=True)
    await driver.writeLayerBytes( layer = 0 , bytes = [0x00]*16 , flush = True)
    await generator.join()

    ## Check That two Frames were seen
    await Timer(50, units="us")
    assert  await driver.readoutGetBufferSize() == 24

    ## Readout and print
    bytes = await driver.readoutReadBytes(24)
    for b in bytes:
        print(f"B={hex(b)}")
    await Timer(50, units="us")

@cocotb.test(timeout_time = 2 , timeout_unit = "ms")
async def test_layer_0_single_frame_autoread(dut):

    ## Driver, asic, clock+reset
    asic = vip.astropix3.Astropix3Model(dut = dut, prefix = "layer_0" , chipID = 1)
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    assert await driver.readoutGetBufferSize() == 0

    ##########

    ## Start the layer, with autoread enabled
    await driver.setLayerConfig(layer = 0, reset = False, hold = False, autoread = True , flush = True )

    ## Drive a frame from the ASIC
    ## This method returns when the frame was outputed from the chip spi slave
    await asic.generateTestFrame(length = 5)

    ## Wait a bit and get the bytes from the readout
    await Timer(50, units="us")
    readoutLength = await driver.readoutGetBufferSize()
    
    ## Length should be 6 Frame bytes (header + 5 payload), +2 Readout Frame Header + 4 Timestamp bytes = 12
    assert readoutLength == 12

    await Timer(50, units="us")


@cocotb.test(timeout_time = 2, timeout_unit = "ms")
async def test_3_layers_single_frame(dut):
    """Send A single frame to all layers after each other"""


    ## Create ASIC Models
    asics = []
    asics.append(vip.astropix3.Astropix3Model(dut = dut, prefix = "layer_0" , chipID = 1))
    asics.append(vip.astropix3.Astropix3Model(dut = dut, prefix = "layer_1" , chipID = 2))
    asics.append(vip.astropix3.Astropix3Model(dut = dut, prefix = "layer_2" , chipID = 3))
    
    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    #########

    ## Start the layers, with autoread enabled
    await driver.setLayerConfig(layer = 0, reset = False, hold = False, autoread = True , flush = False )
    await driver.setLayerConfig(layer = 1, reset = False, hold = False, autoread = True , flush = False )
    await driver.setLayerConfig(layer = 2, reset = False, hold = False, autoread = True , flush = True )

    ## Generate Frame to all after each other
    for i in range(3):
        await asics[i].generateTestFrame(length = 5)

    ## Wait a bit and get the bytes size
    await Timer(100, units="us")
    readoutLength = await driver.readoutGetBufferSize()

    ## Each frame length is 12 (see previous test) -> We should have 3*12
    assert readoutLength == 3*12

    await Timer(10, units="us")

    dut._log.info("Done Frames in sequence")

    ###########

    ## Same test but generate the frames in parallel
    ## First warm reset
    await vip.cctb.warm_reset(dut)
    await Timer(50, units="us")

    ## Start the layers, with autoread enabled
    await driver.setLayerConfig(layer = 0, reset = False, hold = False, autoread = True , flush = False )
    await driver.setLayerConfig(layer = 1, reset = False, hold = False, autoread = True , flush = False )
    await driver.setLayerConfig(layer = 2, reset = False, hold = False, autoread = True , flush = True )

    ## Generate Frames
    tasks = []
    for i in range(3):
        tasks.append(cocotb.start_soon(asics[i].generateTestFrame(length = 5)))

    Combine(*tasks)
    dut._log.info("Sequencing tasks done")

    ## Wait a bit and check the readout size
    await Timer(50, units="us")
    readoutLength = await driver.readoutGetBufferSize()
    assert readoutLength == 3*12

    await Timer(50, units="us")