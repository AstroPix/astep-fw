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


async def diff_clock(dut):
    # pre-construct triggers for performance
    high_time = Timer(50, units="ns")
    low_time = Timer(50, units="ns")
    await Timer(43, units="ns")
    while True:
        dut.ext_timestamp_clk_p.value = 1
        dut.ext_timestamp_clk_n.value = 0
        await high_time
        dut.ext_timestamp_clk_p.value = 0
        dut.ext_timestamp_clk_n.value = 1
        await low_time

@cocotb.test(timeout_time = 10 , timeout_unit = "ms")
async def test_count_ext_clock(dut):

    ## Clock/Reset
    driver = astep24_3l_sim.getUARTDriver(dut)
    await vip.cctb.common_clock_reset_nexys(dut)
    await Timer(10, units="us")

    ## Start external clock
    await Timer(43,units="ns")
    #cocotb.start_soon(Clock(dut.ext_timestamp_clk, 100, units='ns').start())
    cocotb.start_soon(diff_clock(dut))

    ## Enable Timestamp clock
    await Timer(10, units="us")
    await driver.ioSetTimestampClock(enable = True, flush = True)

    ## Disable
    await Timer(10, units="us")
    await driver.ioSetTimestampClock(enable = False, flush = True)
    await driver.rfg.write_layers_cfg_frame_tag_counter(0,flush=True)

    ## Reenable
    await Timer(10, units="us")
    await driver.ioSetTimestampClock(enable = True, flush = True)

    await Timer(50, units="us")