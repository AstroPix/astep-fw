


import sys
import os
import os.path

#sys.path.append(os.path.dirname(__file__)+"/.generated/")

import cocotb
from cocotb.triggers    import Timer,RisingEdge
from cocotb.clock       import Clock

import vip.cctb
import vip.astropix3

import vip.spi
vip.spi.info()

## Import simulation target driver
import astep24_3l_sim

@cocotb.test(timeout_time = 1 , timeout_unit = "ms")
async def test_layers_spi_chipselect(dut):
    """Test that the Chip Select is behaving according to register constrols"""


    def check_cs(all,l0,l1,l2):
        assert(dut.layers_spi_csn.value == all)
        assert(dut.layer_0_spi_csn.value == l0)
        assert(dut.layer_1_spi_csn.value == l1)
        assert(dut.layer_2_spi_csn.value == l2)


    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## At reset, CS should be one
    check_cs(1,1,1,1)


    ## Now select layer 0
    ## Global CS should go low
    await driver.setLayerConfig(layer = 0 , reset = False, autoread = False, hold = False , chipSelect = True,flush=True)
    await Timer(1, units="us")
    check_cs(0,0,1,1)

    ## Deassert Chip Select
    ##################
    await driver.setLayerConfig(layer = 0 , reset = False, autoread = False, hold = False , chipSelect = False,flush=True)
    await Timer(1, units="us")
    check_cs(1,1,1,1)

    ## Set autoread on Layer 0
    ## Chip Select should go low
    ############
    await driver.setLayerConfig(layer = 0 , reset = False, autoread = True, hold = False , chipSelect = False,flush=True)
    await Timer(1, units="us")
    check_cs(0,0,1,1)

    ## Deassert Chip Select
    ############
    await driver.setLayerConfig(layer = 0 , reset = False, autoread = False, hold = False , chipSelect = False,flush=True)
    await Timer(1, units="us")
    check_cs(1,1,1,1)

    ## Check Python Utility to use layer 0 chip select as global CS
    ############

    ## Assert
    await driver.layersSelectSPI(flush=True)
    await Timer(1, units="us")
    check_cs(0,0,1,1)

    ## Deassert
    await driver.layersDeselectSPI(flush=True)
    await Timer(1, units="us")
    check_cs(1,1,1,1)

    await Timer(10, units="us")



@cocotb.test(timeout_time = 1 , timeout_unit = "ms")
async def test_layer_0_spi_mosi(dut):

    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Create SPI Slave
    slave = vip.spi.VSPISlave(clk = dut.layer_0_spi_clk, csn = dut.layer_0_spi_csn,mosi=dut.layer_0_spi_mosi,miso=dut.layer_0_spi_miso)
    slave.start_monitor()

    ## Write MOSI Bytes to Layer
    await driver.setLayerConfig(layer = 0, reset = False, hold = False, autoread = False , flush = True )
    await driver.layersSelectSPI(flush = True)
    await driver.writeLayerBytes(layer = 0 , bytes = [0xAB],flush=True)
    assert (await slave.getByte()) == 0xAB

    ## Check IDLE byte counter, we are getting 2 bytes on MISO for one send byte on MOSI
    assert (await driver.getLayerStatIDLECounter(0)) == 2

    ## Write 2 MOSI Bytes to Layer
    await driver.layersSelectSPI(flush = True)
    await driver.writeLayerBytes(layer = 0 , bytes = [0xCD,0xEF],flush=True)
    assert (await slave.getByte()) == 0xCD
    assert (await slave.getByte()) == 0xEF

    assert (await driver.getLayerStatIDLECounter(0)) == 6

    await Timer(50, units="us")

@cocotb.test(timeout_time = 2 , timeout_unit = "ms",skip = False)
async def test_layers_spi_mosi(dut):

    ## Setup
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Create SPI Slaves
    spiSlaves = []
    slave = vip.spi.VSPISlave(clk = dut.layer_0_spi_clk, csn = dut.layer_0_spi_csn,mosi=dut.layer_0_spi_mosi,miso=dut.layer_0_spi_miso)
    slave.start_monitor()
    spiSlaves.append(slave)

    slave = vip.spi.VSPISlave(clk = dut.layer_1_spi_clk, csn = dut.layer_1_spi_csn,mosi=dut.layer_1_spi_mosi,miso=dut.layer_1_spi_miso)
    slave.start_monitor()
    spiSlaves.append(slave)

    slave = vip.spi.VSPISlave(clk = dut.layer_2_spi_clk, csn = dut.layer_2_spi_csn,mosi=dut.layer_2_spi_mosi,miso=dut.layer_2_spi_miso)
    slave.start_monitor()
    spiSlaves.append(slave)

        

    ## Send Bytes to all layers
    for i in range(3):
        # Make sure Chip Select is asserted here
        await driver.setLayerConfig(layer = i, reset = False, hold = True, autoread = False , chipSelect = True, flush = True )
        await driver.writeLayerBytes(layer = i , bytes = [0x01,0x02],flush=True)

    ## Check
    for i in range(3):
        if i < 3:
            assert (await spiSlaves[i].getByte()) == 0x01
            assert (await spiSlaves[i].getByte()) == 0x02
        
        ## Check IDLE byte counter, we are getting 2 bytes on MISO for one send byte on MOSI
        assert (await driver.getLayerStatIDLECounter(i)) == 4
        dut._log.info(f"Checked Bytes and Counter for layer={i}")

    await Timer(50, units="us")



@cocotb.test(timeout_time = 1 , timeout_unit = "ms")
async def test_layer_0_spi_miso_disable(dut):

    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Create SPI Slave
    slave = vip.spi.VSPISlave(clk = dut.layer_0_spi_clk, csn = dut.layer_0_spi_csn,mosi=dut.layer_0_spi_mosi,miso=dut.layer_0_spi_miso)
    slave.start_monitor()

    ## Select SPI then write two bytes to the SPI Slave
    await driver.setLayerConfig(layer = 0, reset = False, hold = False, autoread = False , flush = True )
    await driver.layersSelectSPI()
    await driver.writeLayerBytes(layer = 0 , bytes = [0xAB],flush=True)
    await Timer(5, units="us")

    ## Check IDLE byte counter, we are getting 2 bytes on MISO for one send byte on MOSI
    assert (await driver.getLayerStatIDLECounter(0)) == 2

    ## Now Disable MISO and check that IDLE counter still stays 2
    await driver.setLayerConfig(layer = 0, reset = False, hold = False, autoread = False , disableMISO = True, flush = True )
    await driver.layersSelectSPI()
    await driver.writeLayerBytes(layer = 0 , bytes = [0xAB],flush=True)
    await Timer(5, units="us")
    assert (await driver.getLayerStatIDLECounter(0)) == 2