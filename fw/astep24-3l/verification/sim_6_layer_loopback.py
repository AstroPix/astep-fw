import logging
import os
import os.path
import random
import sys

## Import simulation target driver
import astep24_3l_sim
import cocotb
import vip.astropix3
import vip.cctb
from cocotb.clock import Clock
from cocotb.triggers import Combine, Join, RisingEdge, Timer, with_timeout


async def freeze_fpga_timestamp(dut, driver):
    """Make FPGA TS count a bit, then freeze it using a TLU trigger"""

    ## Enable FPGA Timestamp counting
    await driver.layersConfigFPGATimestamp(
        enable=True,
        use_divider=False,
        use_tlu=True,
        flush=True,
    )
    await Timer(10, units="us")
    dut.tlu_trigger.value = 1
    for i in range(2):
        await RisingEdge(dut.clk_core)
    dut.tlu_trigger.value = 0


@cocotb.test(timeout_time=500, timeout_unit="ms")
async def test_loopback_layer0(dut):
    ## Reset and driver
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Stop frame tag counter, read it's value to be able to check data frames
    await freeze_fpga_timestamp(dut, driver)
    tagCounterBytes = await driver.rfg.read_layers_fpga_timestamp_counter_raw()

    ## Get LP Driver for Layer 0
    lpModel = driver.getLoopbackModelForLayer(0)

    ## Enable and prepare some bytes in MISO
    ## The bytes should minimally conform to astropix frame, otherwise the frame decoder might kick in wrong
    await lpModel.enableLoopback()

    ## Configure layer and run some dummy bytes to get the Loopback reset correctly
    await driver.setLayerConfig(
        layer=0,
        reset=True,
        autoread=False,
        hold=False,
        chipSelect=False,
        disableMISO=False,
        flush=True,
    )
    await driver.setLayerConfig(
        layer=0,
        reset=False,
        autoread=False,
        hold=False,
        chipSelect=True,
        disableMISO=False,
        flush=True,
    )

    await driver.writeSPIBytesToLane(lane=0, bytes=[0x00] * 16)
    await Timer(50, units="us")

    # Now we can write to the loopback
    await lpModel.writeMISOBytes([0x02, 0xAB, 0xCD])
    await driver.writeSPIBytesToLane(lane=0, bytes=[0x00] * 16)
    await Timer(50, units="us")

    ## Check Size in readout buffer
    assert await driver.readoutGetBufferSize() == 9
    readoutBytes = await driver.readoutReadBytes(9)

    assert readoutBytes == [0x08, 0x01, 0x02, 0xAB, 0xCD] + tagCounterBytes[0:4]
    await Timer(100, units="us")


@cocotb.test(timeout_time=2, timeout_unit="ms")
async def test_loopback_layer0_autoread(dut):
    ## Reset and driver
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Stop frame tag counter, read it's valud to be able to check data frames
    await freeze_fpga_timestamp(dut, driver)
    tagCounterBytes = await driver.rfg.read_layers_fpga_timestamp_counter_raw()

    ## Get LP Driver for Layer 0
    lpModel = driver.getLoopbackModelForLayer(0)

    ## Enable and prepare some bytes in MISO
    ## The bytes should minimally conform to astropix frame, otherwise the frame decoder might kick in wrong
    await lpModel.enableLoopback()

    ## Configure layer and run some dummy bytes to get the Loopback reset correctly
    await driver.setLayerConfig(
        layer=0,
        reset=False,
        autoread=False,
        hold=False,
        chipSelect=False,
        disableMISO=False,
        flush=True,
    )
    await driver.setLayerConfig(
        layer=0,
        reset=False,
        autoread=True,
        hold=False,
        chipSelect=True,
        disableMISO=False,
        flush=True,
    )
    await driver.writeSPIBytesToLane(lane=0, bytes=[0x00] * 16)
    await Timer(50, units="us")

    # Now we can write to the loopback
    await lpModel.writeMISOBytes([0x02, 0xAB, 0xCD])
    # await driver.writeSPIBytesToLane(lane = 0, bytes = [0x00] * 16, flush=True)
    await Timer(50, units="us")

    ## Check Size in readout buffer
    assert await driver.readoutGetBufferSize() == 9
    readoutBytes = await driver.readoutReadBytes(9)

    assert readoutBytes == [0x08, 0x01, 0x02, 0xAB, 0xCD] + tagCounterBytes[0:4]
    await Timer(100, units="us")


@cocotb.test(timeout_time=500, timeout_unit="ms")
async def test_loopback_all_layers(dut):
    ## Reset and driver
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Stop frame tag counter, read it's valud to be able to check data frames
    await freeze_fpga_timestamp(dut, driver)
    tagCounterBytes = await driver.rfg.read_layers_fpga_timestamp_counter_raw()

    for layer in range(3):
        ## Get LP Driver for Layer 0
        lpModel = driver.getLoopbackModelForLayer(layer)

        ## Trigger Layer 0 Master, read bytes should be  the prepared ones
        await driver.setLayerConfig(
            layer=layer,
            reset=True,
            autoread=False,
            hold=False,
            chipSelect=False,
            disableMISO=False,
            flush=True,
        )

        await lpModel.enableLoopback()
        await driver.setLayerConfig(
            layer=layer,
            reset=False,
            autoread=False,
            hold=False,
            chipSelect=True,
            disableMISO=False,
            flush=True,
        )
        await driver.writeSPIBytesToLane(lane=layer, bytes=[0x00] * 16)
        await Timer(50, units="us")

        ## Enable and prepare some bytes in MISO
        ## The bytes should minimally conform to astropix frame, otherwise the frame decoder might kick in wrong

        await lpModel.writeMISOBytes([0x02, 0xAB + layer, 0xCD])
        await driver.writeSPIBytesToLane(lane=layer, bytes=[0x00] * 16)
        await Timer(50, units="us")

        ## Check Size in readout buffer
        assert await driver.readoutGetBufferSize() == 9
        readoutBytes = await driver.readoutReadBytes(9)

        ## Check bytes
        assert (
            readoutBytes
            == [0x08, layer + 1, 0x02, 0xAB + layer, 0xCD] + tagCounterBytes[0:4]
        )

    await Timer(100, units="us")
