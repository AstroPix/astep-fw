
import cocotb
from cocotb.triggers    import Timer,RisingEdge,FallingEdge, Combine
from cocotb.clock       import Clock
from cocotbext.uart import UartSource, UartSink

import vip.cctb
import rfg

## Import simulation target driver
import astep24_3l_sim


@cocotb.test(timeout_time = 1,timeout_unit="ms")
async def test_clocking_resets(dut):
    await vip.cctb.common_clock_reset_nexys(dut)

    await Timer(10, units="us")


@cocotb.test(timeout_time = 1,timeout_unit="ms")
async def test_read_id(dut):

    driver = astep24_3l_sim.getUARTDriver(dut)
    await vip.cctb.common_clock_reset_nexys(dut)
    await Timer(10, units="us")
    

    ## Read Firmware Type
    version = await driver.readFirmwareVersion()
    print("Version: ",version)
    await Timer(10, units="us")

@cocotb.test(timeout_time = 12,timeout_unit="ms")
async def test_injection(dut):

    rfg.core.debug()
    boardDriver = astep24_3l_sim.getUARTDriver(dut)
    await vip.cctb.common_clock_reset_nexys(dut)
    await Timer(10, units="us")
    

    # Get Injection Board from driver
    injBoard = boardDriver.getInjectionBoard()

    # Configure
    injBoard.initdelay = 4
    injBoard.clkdiv = 2
    injBoard.period = 4
    injBoard.pulsesperset = 4
    injBoard.cycle = 1 # 0 Should mean indefinite

    ## Start
    await injBoard.start()
    await Timer(500, units="us")

    await boardDriver.ioSetInjectionToGeccoInjBoard(enable = False,flush = True)

    await injBoard.start()
    await Timer(500, units="us")



@cocotb.test(timeout_time = 2,timeout_unit="ms")
async def test_spi_1byte_out(dut):

    dut.layer_0_interruptn.value = 1
    boardDriver = astep24_3l_sim.getUARTDriver(dut)
    await vip.cctb.common_clock_reset_nexys(dut)
    await Timer(10, units="us")

    ## Read Firmware Type
    version = await boardDriver.readFirmwareVersion()
    print("Version2: ",version)
    await Timer(10, units="us")

    ## Set Clock divider
    await boardDriver.configureLayerSPIFrequency(500000,flush=True)
    await Timer(50, units="us")


    ## Write bytes to get view on the output
    await boardDriver.setLayerConfig(0,reset = False , autoread = False, hold = True, flush = True)
    await boardDriver.writeBytesToLayer(0,[0xAB,0xCD],flush=True)
    await Timer(100, units="us")

    ## Write bytes to get view on the output
    await boardDriver.setLayerConfig(0,reset = False , autoread = True, hold = True, flush = True)
    await boardDriver.writeBytesToLayer(0,[0xAB,0xCD],flush=True)

    ## Trigger some interrupt based bytes to see if clock changes
    dut.layer_0_interruptn.value = 0
    await Timer(100, units="us")
    dut.layer_0_interruptn.value = 1
    await Timer(100, units="us")


@cocotb.test(timeout_time = 5,timeout_unit="ms")
async def test_sr_short_multilayer(dut):

    rfg.core.debug()
    await vip.cctb.common_clock_reset_nexys(dut)
    driver = await astep24_3l_sim.getDriver(dut)
    await Timer(10, units="us")
    
    ## Setup Asic
    driver.setupASICS(version = 3 , rows = 3 , chipsPerRow= 2, configFile = "../../files/test_config_short.yml" )

    ## Write Config
    asic0 = driver.getAsic(0)
    await asic0.writeConfigSR(ckdiv=1)
    asic0.interrupt_pushpull(chip=0,enable = False)
    await asic0.writeConfigSR(ckdiv=1)

    await Timer(50, units="us")

    asic1 = driver.getAsic(1)
    await asic1.writeConfigSR(ckdiv=1)

    await Timer(50, units="us")

    asic2 = driver.getAsic(2)
    await asic2.writeConfigSR(ckdiv=1)

    await Timer(50, units="us")

    await Timer(150, units="us")