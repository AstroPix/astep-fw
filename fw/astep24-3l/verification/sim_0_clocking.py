



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

    ## Test Warm Reset -> It will make core resn toggle
    dut.warm_resn.value = 0
    await FallingEdge(dut.clk_core_resn)
    await Timer(2, units="us")
    dut.warm_resn.value =1
    await RisingEdge(dut.clk_core_resn)
    await Timer(2, units="us")
    

    ## Test Cold Reset -> will stop the clocks completely and reset
    dut.cold_resn.value = 0
    await FallingEdge(dut.clk_core_resn)
    await Timer(2, units="us")
    assert dut.clk_core == 0
    dut.cold_resn.value = 1
    await RisingEdge(dut.clk_core_resn)

    #assert 0 == 1

    await Timer(10, units="us")

@cocotb.test(timeout_time = 1,timeout_unit="ms")
async def test_clocking_dividers(dut):
  
    await vip.cctb.common_clock_reset(dut)
    dut.warm_resn.value = 0
    await Timer(2, units="us")
    dut.warm_resn.value = 1

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