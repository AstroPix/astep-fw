import sys
import os
import os.path

import rfg.core
import cocotb
from cocotb.triggers import Timer, RisingEdge, FallingEdge, Join, Combine
from cocotb.clock import Clock

import vip.cctb
import vip.astropix3

## Import simulation target driver
import astep24_3l_sim


@cocotb.test(timeout_time=1, timeout_unit="ms")
async def test_tlu_disabled_count_enable(dut):
    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    job = cocotb.start_soon(
        driver.layersConfigFPGATimestamp(
            enable=True,
            use_divider=False,
            use_tlu=False,
            flush=True,
        )
    )

    ## Wait for counter count and two clock cycles to cover delay of TLU starting to update
    await RisingEdge(dut.layers_fpga_timestamp_ctrl_count)
    await FallingEdge(dut.tlu.tlu_clk_in)

    ## Check it counts
    await FallingEdge(dut.tlu.tlu_clk_in)
    assert dut.tlu_ts_out.value & 0xFF == 0
    await FallingEdge(dut.tlu.tlu_clk_in)
    assert dut.tlu_ts_out.value & 0xFF == 1
    await FallingEdge(dut.tlu.tlu_clk_in)
    assert dut.tlu_ts_out.value & 0xFF == 2

    ## Disable Counter and TLU, should reset
    await job
    job = cocotb.start_soon(
        driver.layersConfigFPGATimestamp(
            enable=False,
            use_divider=False,
            use_tlu=False,
            flush=True,
        )
    )

    await FallingEdge(dut.layers_fpga_timestamp_ctrl_count)
    await FallingEdge(dut.tlu.tlu_clk_in)
    await FallingEdge(dut.tlu.tlu_clk_in)
    assert dut.tlu_ts_out.value & 0xFF == 0

    await job

    await Timer(50, units="us")
    pass


@cocotb.test(timeout_time=1, timeout_unit="ms")
async def test_tlu_disabled_count_divided(dut):
    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    job = cocotb.start_soon(
        driver.layersConfigFPGATimestamp(
            enable=True,
            use_divider=True,
            use_tlu=False,
            flush=True,
        )
    )

    ## Wait for counter counting, and then wait for an increment
    await RisingEdge(dut.layers_fpga_timestamp_ctrl_count)
    await RisingEdge(dut.tlu.tlu_clk_in)
    await FallingEdge(dut.tlu.tlu_clk_in)
    assert dut.tlu_ts_out.value & 0xFF == 0

    ## Check it counts
    await RisingEdge(dut.layers_fpga_timestamp_ctrl_count)
    await RisingEdge(dut.tlu.tlu_clk_in)
    await FallingEdge(dut.tlu.tlu_clk_in)
    assert dut.tlu_ts_out.value & 0xFF == 1

    ## Disable Counter and TLU, should reset
    await job
    job = cocotb.start_soon(
        driver.layersConfigFPGATimestamp(
            enable=False,
            use_divider=False,
            use_tlu=False,
            flush=True,
        )
    )

    await FallingEdge(dut.layers_fpga_timestamp_ctrl_enable)
    await FallingEdge(dut.tlu.tlu_clk_in)
    await FallingEdge(dut.tlu.tlu_clk_in)
    assert dut.tlu_ts_out.value & 0xFF == 0

    await job
    await Timer(50, units="us")
    pass


@cocotb.test(timeout_time=1, timeout_unit="ms")
async def test_tlu_enabled_always_count(dut):
    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    job = cocotb.start_soon(
        driver.layersConfigFPGATimestamp(
            enable=True,
            use_divider=False,
            use_tlu=True,
            flush=True,
        )
    )

    ## Wait for counter counting, then for some clock cycles - TS output should stay stable until a trigger comes
    await RisingEdge(dut.layers_fpga_timestamp_ctrl_count)
    for i in range(10):
        await FallingEdge(dut.tlu.tlu_clk_in)

    await job

    ## Make a trigger, check the TS changed after the trigger, but not when no trigger is present
    for i in range(5):
        tsval1 = dut.tlu_ts_out.value & 0xFFFFFF
        await RisingEdge(dut.tlu.tlu_clk_in)
        dut.tlu_trigger.value = 1
        await RisingEdge(dut.tlu.tlu_clk_in)
        dut.tlu_trigger.value = 0
        await RisingEdge(dut.tlu.tlu_clk_in)
        await RisingEdge(dut.tlu.tlu_clk_in)
        await RisingEdge(dut.tlu.tlu_clk_in)

        ## Check TS didn't change
        tsval = dut.tlu_ts_out.value & 0xFFFFFF
        await RisingEdge(dut.tlu.tlu_clk_in)
        await RisingEdge(dut.tlu.tlu_clk_in)
        await RisingEdge(dut.tlu.tlu_clk_in)
        assert tsval == dut.tlu_ts_out.value & 0xFFFFFF
        assert tsval != 0
        assert tsval > tsval1 + 1

        await Timer(1, units="us")

    ## Now Reset with t0
    await Timer(50, units="us")

    dut.tlu_t0.value = 1
    await Timer(10, units="us")
    dut.tlu_t0.value = 0
    await FallingEdge(dut.tlu.tlu_clk_in)
    assert dut.tlu_ts_out.value & 0xFF == 0
    await RisingEdge(dut.tlu.tlu_clk_in)
    await RisingEdge(dut.tlu.tlu_clk_in)

    ## Make another couple trigger to make sure it updates again
    for i in range(5):
        tsval1 = dut.tlu_ts_out.value & 0xFFFFFF
        await RisingEdge(dut.tlu.tlu_clk_in)
        dut.tlu_trigger.value = 1
        await RisingEdge(dut.tlu.tlu_clk_in)
        dut.tlu_trigger.value = 0
        await RisingEdge(dut.tlu.tlu_clk_in)
        await RisingEdge(dut.tlu.tlu_clk_in)
        await RisingEdge(dut.tlu.tlu_clk_in)

        ## Check TS didn't change
        tsval = dut.tlu_ts_out.value & 0xFFFFFF
        await RisingEdge(dut.tlu.tlu_clk_in)
        await RisingEdge(dut.tlu.tlu_clk_in)
        await RisingEdge(dut.tlu.tlu_clk_in)
        assert tsval == dut.tlu_ts_out.value & 0xFFFFFF
        assert tsval != 0
        assert tsval > tsval1 + 1

        await Timer(1, units="us")

    await Timer(50, units="us")
    pass


@cocotb.test(timeout_time=10, timeout_unit="ms", skip=True)
async def test_count_ext_clock(dut):
    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Start external clock
    await Timer(43, units="ns")
    cocotb.start_soon(Clock(dut.ext_timestamp_clk, 100, units="ns").start())

    ## Enable FPGA TS and set external source
    await Timer(10, units="us")
    await driver.layersConfigFPGATimestamp(
        enable=True,
        use_divider=False,
        use_tlu=False,
        flush=True,
    )

    ## Disable
    await Timer(10, units="us")
    await driver.layersConfigFPGATimestamp(
        enable=False,
        use_divider=False,
        use_tlu=False,
        flush=True,
    )
    await driver.rfg.write_layers_cfg_frame_tag_counter(0, flush=True)

    ## Reenable
    await Timer(10, units="us")
    await driver.layersConfigFPGATimestamp(
        enable=True,
        use_divider=False,
        use_tlu=False,
        flush=True,
    )

    await Timer(50, units="us")


@cocotb.test(timeout_time=10, timeout_unit="ms", skip=True)
async def test_count_match_trigger(dut):
    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    dut.ext_timestamp_clk.value = 0

    await Timer(50, units="us")

    ## Configure
    await driver.layersConfigFPGATimestampFrequency(
        targetFrequencyHz=1000000, flush=True
    )
    await driver.layersConfigFPGATimestamp(
        enable=True,
        use_divider=True,
        use_tlu=False,
        flush=True,
    )

    await Timer(50, units="us")

    ## Change match value
    await driver.layersConfigFPGATimestampFrequency(
        targetFrequencyHz=1500000, flush=True
    )

    await Timer(50, units="us")
