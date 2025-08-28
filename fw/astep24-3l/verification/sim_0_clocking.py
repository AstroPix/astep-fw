



import cocotb
from cocotb.triggers    import Timer,RisingEdge,FallingEdge, Combine
from cocotb.clock       import Clock
from cocotbext.uart import UartSource, UartSink

import vip.cctb

## Import simulation target driver
import astep24_3l_sim

@cocotb.test(timeout_time = 1,timeout_unit="ms")
async def test_clocking_resets(dut):
    await vip.cctb.common_clock_reset(dut)

    await Timer(10, units="us")

    ## Test  Reset -> It will make core resn toggle
    dut.resn.value = 0
    await FallingEdge(dut.clk_core_resn)
    await Timer(2, units="us")
    dut.resn.value =1
    await RisingEdge(dut.clk_core_resn)
    await Timer(2, units="us")



    await Timer(10, units="us")


@cocotb.test(timeout_time = 1,timeout_unit="ms")
async def test_clocking_ext_clk_autoswitch(dut):
    await vip.cctb.common_clock_reset(dut)

    await Timer(10, units="us")

    ## Test  Reset -> It will make core resn toggle
    dut.resn.value = 0
    await FallingEdge(dut.clk_core_resn)
    await Timer(2, units="us")
    dut.resn.value =1
    await RisingEdge(dut.clk_core_resn)
    await Timer(2, units="us")

    ## Now Start external clock
    ext_task = await vip.cctb.start_external_clock(dut)

    ## Switch over will produce a reset
    await FallingEdge(dut.clk_core_resn)
    await RisingEdge(dut.clk_core_resn)

    ## Make another reset to test back to non external clock then switchover again
    ## There's only one reset for main reset + switch over because switchover happens fast
    await Timer(50, units="us")
    dut.resn.value = 0
    await FallingEdge(dut.clk_core_resn)
    await Timer(2, units="us")
    dut.resn.value =1
    await RisingEdge(dut.clk_core_resn)

    assert dut.clocking_reset_I.core_mmmc_clksel == 0, "Clock Clksel should be 0, meaning external"


    ## Turn off Ext Clock and see that PLL switches back to main clock
    ext_task.cancel()
    await FallingEdge(dut.clk_core_resn)
    await RisingEdge(dut.clk_core_resn)

    ## Turn on Clock again to check it resets again
    await Timer(50, units="us")
    ext_task = await vip.cctb.start_external_clock(dut)
    await FallingEdge(dut.clk_core_resn)
    await RisingEdge(dut.clk_core_resn)

    await Timer(10, units="us")

@cocotb.test(timeout_time = 1,timeout_unit="ms")
async def test_clocking_dividers(dut):

    await vip.cctb.common_clock_reset(dut)
    dut.resn.value = 0
    await Timer(2, units="us")
    dut.resn.value = 1

    await RisingEdge(dut.main_rfg_I.spi_layers_ckdivider_divided_clk)
    await RisingEdge(dut.main_rfg_I.spi_hk_ckdivider_divided_clk)

    await Combine(RisingEdge(dut.main_rfg_I.spi_layers_ckdivider_divided_resn),RisingEdge(dut.main_rfg_I.spi_hk_ckdivider_divided_resn))


    await Timer(50, units="us")


@cocotb.test(timeout_time = 1,timeout_unit="ms")
async def test_buffers_reset(dut):

    ## Get Target Driver
    driver = await astep24_3l_sim.getDriver(dut)

    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")

    ## Create SPI Slave
    slave = vip.spi.VSPISlave(clk = dut.layer_0_spi_clk, csn = dut.layer_0_spi_csn,mosi=dut.layer_0_spi_mosi,miso=dut.layer_0_spi_miso,misoDefaultValue=0xFF)
    slave.start_monitor()

    ## Write MOSI Bytes to Layer
    await driver.writeLayerBytes(layer = 0 , bytes = [0x00]*16,flush=True)
    await Timer(100, units="us")
    dut.warm_resn.value = 0
    await Timer(2, units="us")
    dut.warm_resn.value =1

    await Timer(50, units="us")

@cocotb.test(timeout_time = 1,timeout_unit="ms")
async def test_spi_divider_api(dut):

    ## Get Target Driver
    boardDriver = await astep24_3l_sim.getDriver(dut)

    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")

    ## Set Clock divider
    await boardDriver.configureLayerSPIFrequency(2000000,flush=True)
    await Timer(50, units="us")

    ## Set Clock divider
    await boardDriver.configureLayerSPIFrequency(500000,flush=True)
    await Timer(50, units="us")
