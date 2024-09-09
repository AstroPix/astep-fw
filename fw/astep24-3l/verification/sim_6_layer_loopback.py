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



@cocotb.test(timeout_time = 500 , timeout_unit = "ms")
async def test_loopback_layer0(dut):

    ## Reset and driver
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Stop frame tag counter, read it's valud to be able to check data frames
    await driver.configureLayersFrameTagFrequency(500000,True)
    await Timer(1,units="us")
    await driver.configureLayersFrameTag(enable = False,flush = True)
    tagCounterBytes = await driver.rfg.read_layers_cfg_frame_tag_counter_raw()

    ## Get LP Driver for Layer 0
    lpModel = driver.getLoopbackModelForLayer(0)

    ## Enable and prepare some bytes in MISO
    ## The bytes should minimally conform to astropix frame, otherwise the frame decoder might kick in wrong
    await lpModel.enableLoopback()
    await lpModel.writeMISOBytes([0x02,0xAB,0xCD])

    ## Trigger Layer 0 Master, read bytes should be  the prepared ones
    await driver.setLayerConfig(layer = 0 , reset = False , autoread =False, hold = False , chipSelect = True,disableMISO = False, flush = True)
    #await driver.layerSelectSPI(layer=0,cs = True, flush = True)
    await driver.writeLayerBytes(layer = 0, bytes = [0x00] * 2 , flush=True)
    await Timer(10, units="us")
    await driver.layerSelectSPI(layer=0,cs = False, flush = True)
    
    ## Check Size in readout buffer
    assert  await driver.readoutGetBufferSize() == 9
    readoutBytes = await driver.readoutReadBytes(9)

    assert readoutBytes == [0x08,0x01,0x02,0xAB,0xCD] + tagCounterBytes
    await Timer(100, units="us")


@cocotb.test(timeout_time = 500 , timeout_unit = "ms")
async def test_loopback_all_layers(dut):

    ## Reset and driver
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Stop frame tag counter, read it's valud to be able to check data frames
    await driver.configureLayersFrameTagFrequency(500000,True)
    await Timer(1,units="us")
    await driver.configureLayersFrameTag(enable = False,flush = True)
    tagCounterBytes = await driver.rfg.read_layers_cfg_frame_tag_counter_raw()

    for layer in range(3):
        ## Get LP Driver for Layer 0
        lpModel = driver.getLoopbackModelForLayer(layer)

        ## Enable and prepare some bytes in MISO
        ## The bytes should minimally conform to astropix frame, otherwise the frame decoder might kick in wrong
        await lpModel.enableLoopback()
        await lpModel.writeMISOBytes([0x02,0xAB + layer ,0xCD])

        ## Trigger Layer 0 Master, read bytes should be  the prepared ones
        await driver.setLayerConfig(layer = layer , reset = False , autoread =False, hold = False , chipSelect = True,disableMISO = False, flush = True)
        #await driver.layerSelectSPI(layer=0,cs = True, flush = True)
        await driver.writeLayerBytes(layer = layer, bytes = [0x00] * 2 , flush=True)
        await Timer(10, units="us")
        await driver.layerSelectSPI(layer=layer ,cs = False, flush = True)
        
        ## Check Size in readout buffer
        assert  await driver.readoutGetBufferSize() == 9
        readoutBytes = await driver.readoutReadBytes(9)

        ## Check bytes
        assert readoutBytes == [0x08,layer+1,0x02,0xAB + layer ,0xCD] + tagCounterBytes

    await Timer(100, units="us")