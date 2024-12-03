import sys
import os
import os.path

import rfg.core
import cocotb
from cocotb.triggers    import Timer,RisingEdge,Join,Combine
from cocotb.clock       import Clock

import vip.cctb
import vip.astropix3

## Import simulation target driver
import astep24_3l_sim

@cocotb.test(timeout_time = 10 , timeout_unit = "ms")
async def test_count_ext_clock(dut):

    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Start external clock
    await Timer(43,units="ns")
    cocotb.start_soon(Clock(dut.ext_timestamp_clk, 100, units='ns').start())

    ## Enable FPGA TS and set external source
    await Timer(10, units="us")
    await driver.layersConfigFPGATimestamp(enable = True,force = False ,source_match_counter = False, source_external = True ,flush = True)


    ## Disable
    await Timer(10, units="us")
    await driver.layersConfigFPGATimestamp(enable = False,force = False ,source_match_counter = False, source_external = True ,flush = True)
    await driver.rfg.write_layers_cfg_frame_tag_counter(0,flush=True)

    ## Reenable
    await Timer(10, units="us")
    await driver.layersConfigFPGATimestamp(enable = True,force = False ,source_match_counter = False, source_external = True ,flush = True)


    await Timer(50, units="us")



@cocotb.test(timeout_time = 10 , timeout_unit = "ms")
async def test_count_match_trigger(dut):

    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    dut.ext_timestamp_clk.value = 0

    await Timer(50, units="us")

    ## Configure
    await driver.layersConfigFPGATimestampFrequency(targetFrequencyHz = 1000000 ,flush = True)
    await driver.layersConfigFPGATimestamp(enable = True,force = False ,source_match_counter = True, source_external = False ,flush = True)

    await Timer(50, units="us")

    ## Change match value
    await driver.layersConfigFPGATimestampFrequency(targetFrequencyHz = 1500000 ,flush = True)

    await Timer(50, units="us")