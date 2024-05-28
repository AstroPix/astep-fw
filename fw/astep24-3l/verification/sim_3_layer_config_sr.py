


import sys
import os
import os.path
import asyncio

#sys.path.append(os.path.dirname(__file__)+"/.generated/")

import cocotb
from cocotb.triggers    import Timer,RisingEdge,FallingEdge,Combine,Join
from cocotb.clock       import Clock

import vip.cctb
import vip.astropix3

import vip.spi
vip.spi.info()

import rfg.core

## Import simulation target driver
import astep24_3l_sim

@cocotb.test(timeout_time = 3 , timeout_unit = "ms")
async def test_layers_config_sr(dut):
    """Writs SR Config to each row/layer, check for Load signal for each"""
 
    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Create ASIC config
    driver.setupASICS(version = 2, rows = 3 , chipsPerRow = 1, configFile = "./files/config_c0_r0.yml")

    ## Send config
    async def wait_for_load(row):
        await FallingEdge(dut._id(f"layers_sr_out_ld{row}", extended=False))

    for row in range(3):
        asic = driver.getAsic(row = row)
        fallingEdgeTask = cocotb.start_soon( wait_for_load(row))
        await asic.writeConfigSR(ckdiv = 1 , limit = 4)
        ## After last bit to load = 4 written, we can wait for a falling edge of load 
        await Join(fallingEdgeTask)
    

    await Timer(150, units="us")


@cocotb.test(timeout_time = 3 , timeout_unit = "ms")
async def test_layer_0_config_sr_multichip(dut):
    """Configures using SR on layer 0 with a multichip chain"""

    rfg.core.debug()

    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Create ASIC config
    driver.setupASICS(version = 3, rows = 1 , chipsPerRow = 2, configFile = "./files/config_v3_mc.yml")

    asic = driver.getAsic(row = 0)

    ## Write Config and wait for edge
    async def wait_for_load():
        await FallingEdge(dut._id(f"layers_sr_out_ld0", extended=False))

    fallingEdgeTask = cocotb.start_soon( wait_for_load() )
    await asic.writeConfigSR(ckdiv = 2)
    await Join(fallingEdgeTask)
    #await asyncio.gather(asic.writeConfigSR(ckdiv = 2))
    #,FallingEdge(dut._id(f"layers_sr_out_ld0", extended=False))
    #await asic.writeConfigSR(ckdiv = 2)
    #await Combine(
    #    asic.writeConfigSR(ckdiv = 2),
    #    ## After last bit to load = 4 written, we can wait for a falling edge of load
    #    FallingEdge(dut._id(f"layers_sr_out_ld0", extended=False))
    #)
    
    await Timer(150, units="us")
