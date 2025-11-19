## Import simulation target driver
import astep24_3l_sim
import cocotb
import rfg.cocotb.cocotb_spi
import vip.cctb
from cocotb.clock import Clock
from cocotb.triggers import Combine, FallingEdge, RisingEdge, Timer
from cocotbext.uart import UartSink, UartSource


@cocotb.test(timeout_time=1, timeout_unit="ms")
async def test_clocking_resets(dut):
    await vip.cctb.common_clock_reset(dut)

    await Timer(10, units="us")

    ## Test  Reset -> It will make core resn toggle
    dut.resn.value = 0
    await FallingEdge(dut.clk_core_resn)
    await Timer(2, units="us")
    dut.resn.value = 1
    await RisingEdge(dut.clk_core_resn)
    await Timer(2, units="us")

    await Timer(10, units="us")


@cocotb.test(timeout_time=1, timeout_unit="ms")
async def test_clocking_ext_clk_autoswitch(dut):
    
    
    
    
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    
    ## Get Target Driver
    driver = await astep24_3l_sim.getFTDIDriver(dut)

    ## Test  Reset -> It will make core resn toggle
    dut.resn.value = 0
    await FallingEdge(dut.clk_core_resn)
    await Timer(2, units="us")
    dut.resn.value = 1
    await RisingEdge(dut.clk_core_resn)
    await Timer(2, units="us")
    
    ## Enable TLU to allow clock switching 
    await driver.layersConfigFPGATimestamp(
        enable = True,
        use_divider= True,
        use_tlu= True,
        flush=True
    )
    await Timer(50, units="us")
    
    dut._log.info("TLU enabled, now testing clock swithing")
    

    ## Now Start external clock
    ext_task = await vip.cctb.start_external_clock(dut)

    ## Switch over will produce a reset
    await FallingEdge(dut.clk_core_resn)
    await RisingEdge(dut.clk_core_resn)

    assert dut.clocking_reset_I.clk_ext_selected.value == 1, (
        "Clock Clksel should be 1, meaning external"
    )

    ## Make another reset to test back to non external clock then switchover again
    ## There's only one reset for main reset + switch over because switchover happens fast
    await Timer(50, units="us")
    dut.resn.value = 0
    await FallingEdge(dut.clk_core_resn)
    await Timer(2, units="us")
    dut.resn.value = 1
    await RisingEdge(dut.clk_core_resn)
    
    ## Enable TLU to allow clock switching 
    await driver.layersConfigFPGATimestamp(
        enable = True,
        use_divider= True,
        use_tlu= True,
        flush=True
    )
    await Timer(10, units="us")
    assert dut.clocking_reset_I.clk_ext_selected.value == 1, (
        "Clock Clksel should be 1, meaning external"
    )

    ## Turn off Ext Clock and see that PLL switches back to main clock
    ext_task.cancel()
    await FallingEdge(dut.clk_core_resn)
    await RisingEdge(dut.clk_core_resn)
    
    dut._log.info("Turned off TLU clock, recovered to primary")
    
    ## Turn on Clock again to check it resets again
    await Timer(50, units="us")
    ext_task = await vip.cctb.start_external_clock(dut)
    
    ## Enable TLU to allow clock switching 
    await driver.layersConfigFPGATimestamp(
        enable = True,
        use_divider= True,
        use_tlu= True,
        flush=True
    )
    #await Timer(10, units="us")
    
    
    await FallingEdge(dut.clk_core_resn)
    await RisingEdge(dut.clk_core_resn)

    await Timer(10, units="us")


@cocotb.test(timeout_time=1, timeout_unit="ms")
async def test_clocking_dividers(dut):
    await vip.cctb.common_clock_reset(dut)
    dut.resn.value = 0
    await Timer(2, units="us")
    dut.resn.value = 1

    await RisingEdge(dut.main_rfg_I.spi_layers_ckdivider_divided_clk)
    await RisingEdge(dut.main_rfg_I.spi_hk_ckdivider_divided_clk)

    await Combine(
        RisingEdge(dut.main_rfg_I.spi_layers_ckdivider_divided_resn),
        RisingEdge(dut.main_rfg_I.spi_hk_ckdivider_divided_resn),
    )

    await Timer(50, units="us")


@cocotb.test(timeout_time=1, timeout_unit="ms")
async def test_buffers_reset(dut):
    ## Get Target Driver
    driver = await astep24_3l_sim.getDriver(dut)

    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")

    ## Create SPI Slave
    slave = vip.spi.VSPISlave(
        clk=dut.layer_0_spi_clk,
        csn=dut.layer_0_spi_csn,
        mosi=dut.layer_0_spi_mosi,
        miso=dut.layer_0_spi_miso,
        misoDefaultValue=0xFF,
    )
    slave.start_monitor()

    ## Write MOSI Bytes to Layer
    await driver.writeSPIBytesToLane(lane=0, bytes=[0x00] * 16)
    await Timer(100, units="us")
    dut.resn.value = 0
    await Timer(2, units="us")
    dut.resn.value = 1

    await Timer(50, units="us")


@cocotb.test(timeout_time=2, timeout_unit="ms")
async def test_spi_divider_api(dut):
    # rfg.cocotb.cocotb_spi.debug()

    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")

    ## Get Target Driver
    boardDriver = await astep24_3l_sim.getDriver(dut)

    ## Enable Layer
    await boardDriver.setLayerConfig(
        layer=0,
        reset=False,
        autoread=False,
        hold=False,
        chipSelect=True,
        disableMISO=True,
        flush=True,
    )

    ## Set Clock divider for 2Mhz
    await boardDriver.configureLayerSPIFrequency(2000000, flush=True)
    await boardDriver.writeSPIBytesToLane(
        lane=0, bytes=[0x00] * 8, waitForLastChunk=False
    )
    dut._log.info("Done Writing bytes, waiting for SPI Clock")

    await RisingEdge(dut.layer_0_spi_clk)
    edge1 = cocotb.utils.get_sim_time("ns")
    await RisingEdge(dut.layer_0_spi_clk)
    edge2 = cocotb.utils.get_sim_time("ns")

    await Timer(100, units="us")

    assert edge2 - edge1 == 500, "2Mhz SPI Frequency should show 500ns between edges"

    ## Set Clock divider for 500Khz
    await boardDriver.configureLayerSPIFrequency(500000, flush=True)

    await boardDriver.writeSPIBytesToLane(
        lane=0, bytes=[0x00] * 8, waitForLastChunk=False
    )

    await RisingEdge(dut.layer_0_spi_clk)
    edge1 = cocotb.utils.get_sim_time("ns")
    await RisingEdge(dut.layer_0_spi_clk)
    edge2 = cocotb.utils.get_sim_time("ns")

    await Timer(100, units="us")

    assert edge2 - edge1 == 2000, (
        "500Khz SPI Frequency should show 2000ns between edges"
    )

    ## Set Clock divider for 10Mhz
    await boardDriver.configureLayerSPIFrequency(10000000, flush=True)

    await boardDriver.writeSPIBytesToLane(
        lane=0, bytes=[0x00] * 8, waitForLastChunk=False
    )

    await RisingEdge(dut.layer_0_spi_clk)
    edge1 = cocotb.utils.get_sim_time("ns")
    await RisingEdge(dut.layer_0_spi_clk)
    edge2 = cocotb.utils.get_sim_time("ns")

    assert edge2 - edge1 == 100, "10Mhz SPI Frequency should show 100ns between edges"

    await Timer(100, units="us")
