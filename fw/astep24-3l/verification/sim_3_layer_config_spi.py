


import sys
import os
import os.path
import asyncio
import logging 

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

SPI_HEADER_SR       = 0b011 << 5
SPI_SR_BROADCAST    = 0x7E

@cocotb.test(timeout_time = 3 , timeout_unit = "ms")
async def test_layers_config_spi_chip0(dut):
    """"""

    ## Set SPI Slave monitor 
    slave = vip.spi.VSPISlave(clk = dut.layer_0_spi_clk, csn = dut.layer_0_spi_csn,mosi=dut.layer_0_spi_mosi,miso=dut.layer_0_spi_miso)
    slave.start_monitor()

    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Create ASIC config
    driver.setupASICS(version = 3, rows = 3 , chipsPerRow = 2, configFile = "./files/config_v3_mc.yml")

    ## Write Config via SPI
    ## Don't forget to unreset and chip select
    await driver.setLayerConfig(layer = 0 , reset=False, autoread=False, hold=True, chipSelect=False, disableMISO=True, flush=True)
    await driver.layersSelectSPI()
    asic = driver.getAsic(0)
    await asic.writeConfigSPI(targetChip = 0)
    await driver.layersDeselectSPI()

    await Timer(10, units="us")
    
    # Check header
    assert (await slave.getByte() == (SPI_HEADER_SR | 0))
    await slave.clearBytes()

    ## Test Broadcast
    await driver.layersSelectSPI()
    await asic.writeConfigSPI(broadcast = True)
    await driver.layersDeselectSPI()

    await Timer(10, units="us")

    # Check header
    assert (await slave.getByte() == (SPI_SR_BROADCAST))

    await Timer(150, units="us")

@cocotb.test(timeout_time = 3 , timeout_unit = "ms")
async def test_layers_config_spi_chip0_checkbits(dut):
    """"""

    ## Set SPI Slave monitor
    astropix = vip.astropix3.Astropix3Model(dut,"layer_0",0)
    
    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Create ASIC config
    driver.setupASICS(version = 3, rows = 3 , chipsPerRow = 2, configFile = "./files/config_v3_mc.yml")

    ## Write Config via SPI
    ## Don't forget to unreset and chip select
    await driver.setLayerConfig(layer = 0 , reset=False, autoread=False, hold=True, chipSelect=False, disableMISO=True, flush=True)
    await driver.layersSelectSPI()
    asic = driver.getAsic(0)
    await asic.writeConfigSPI(targetChip = 0)
    await driver.layersDeselectSPI()

    await Timer(10, units="us")
    
    ## Check Config using astropix model
    srbits = await astropix.parseSPIBytesAsConfig()

    ## Chip 0 in the config is 1011, so the SR bits must be reversed: 1101
    assert(srbits == [1,1,0,1])

    await Timer(150, units="us")

@cocotb.test(timeout_time = 5 , timeout_unit = "ms")
async def test_layers_config_spi_chips_checkbits(dut):
    """Sends config in target chip, broadcast to check config bits send"""

    #dut._log.setLevel(logging.DEBUG)

    ## Set SPI Slave monitor
    astropix = vip.astropix3.Astropix3Model(dut,"layer_0",0)
    
    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Create ASIC config
    driver.setupASICS(version = 3, rows = 3 , chipsPerRow = 2, configFile = "./files/config_v3_mc.yml")

    ## Write Config via SPI to Chip 0
    ## Don't forget to unreset and chip select
    ##################
    await driver.setLayerConfig(layer = 0 , reset=False, autoread=False, hold=True, chipSelect=False, disableMISO=True, flush=True)
    await driver.layersSelectSPI()
    asic = driver.getAsic(0)
    await asic.writeConfigSPI(targetChip = 0)
    await driver.layersDeselectSPI()

    await Timer(300, units="us")
    
    ## Chip 0 in the config is 1011, so the SR bits must be reversed: 1101
    dut._log.info("Checking Config came from Chip 0")
    assert(await astropix.parseSPIBytesAsConfig() == [1,1,0,1] )

    ## Write Config via SPI to Chip 1
    ## Don't forget to unreset and chip select
    ##################
    await driver.setLayerConfig(layer = 0 , reset=False, autoread=False, hold=True, chipSelect=False, disableMISO=True, flush=True)
    await driver.layersSelectSPI()
    asic = driver.getAsic(0)
    await asic.writeConfigSPI(targetChip = 1)
    await driver.layersDeselectSPI()

    await Timer(300, units="us")
    
    ## Chip 1 in the config is 1000, so the SR bits must be reversed: 0001
    dut._log.info("Checking Config came from Chip 1")
    assert(await astropix.parseSPIBytesAsConfig() == [0,0,0,1] )

    ## Write Config via SPI as Broadcast from Chip 0
    ## Don't forget to unreset and chip select
    ##################
    await driver.setLayerConfig(layer = 0 , reset=False, autoread=False, hold=True, chipSelect=False, disableMISO=True, flush=True)
    await driver.layersSelectSPI()
    asic = driver.getAsic(0)
    await asic.writeConfigSPI(broadcast = True, targetChip = 0)
    await driver.layersDeselectSPI()

    await Timer(300, units="us")
    
    ## Config source was chip 0
    dut._log.info("Checking BR Config came from Chip 0")
    assert(await astropix.parseSPIBytesAsConfig(broadcast = True) == [1,1,0,1] )


    ## Write Config via SPI as Broadcast from Chip 1
    ## Don't forget to unreset and chip select
    ##################
    await driver.setLayerConfig(layer = 0 , reset=False, autoread=False, hold=True, chipSelect=False, disableMISO=True, flush=True)
    await driver.layersSelectSPI()
    asic = driver.getAsic(0)
    await asic.writeConfigSPI(broadcast = True, targetChip = 1)
    await driver.layersDeselectSPI()

    await Timer(300, units="us")
    
    ## Config source was chip 1
    dut._log.info("Checking BR Config came from Chip 1")
    assert(await astropix.parseSPIBytesAsConfig(broadcast = True) == [0,0,0,1] )


    

    await Timer(150, units="us")


@cocotb.test(timeout_time = 3 , timeout_unit = "ms",skip=False)
async def test_layer_0_config_sr_multichip(dut):
    """Configures using SR on layer 0 with a multichip chain"""

    #rfg.core.debug()

    ## Set SPI Slave monitor
    astropix = vip.astropix3.Astropix3Model(dut,"layer_0",0)

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

    ## Check number of bits received on SR
    
    #await asyncio.gather(asic.writeConfigSR(ckdiv = 2))
    #,FallingEdge(dut._id(f"layers_sr_out_ld0", extended=False))
    #await asic.writeConfigSR(ckdiv = 2)
    #await Combine(
    #    asic.writeConfigSR(ckdiv = 2),
    #    ## After last bit to load = 4 written, we can wait for a falling edge of load
    #    FallingEdge(dut._id(f"layers_sr_out_ld0", extended=False))
    #)
    
    await Timer(150, units="us")
