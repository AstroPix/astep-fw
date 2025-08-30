
import sys
import os

import cocotb
from cocotb.triggers    import Timer,RisingEdge
from cocotb.clock       import Clock
from cocotbext.uart import UartSource, UartSink

import vip.cctb
import rfg.cocotb.cocotb_spi

## Import simulation target driver
import astep24_3l_sim



@cocotb.test(timeout_time = 1 , timeout_unit = "ms")
async def test_fw_id_uart(dut):

    driver = await astep24_3l_sim.getUARTDriver(dut)
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")


    ## Read Firmware Type
    version = await driver.readFirmwareVersion()
    print("Version: ",version)
    assert version == 0xffab

    ## Read Firmware ID
    id = await driver.readFirmwareID()
    print("FW ID:",hex(id))
    assert id == 0xff00


@cocotb.test(timeout_time = 1 , timeout_unit = "ms")
async def test_fw_id_spi(dut):

    #rfg.core.debug()
    #rfg.cocotb.cocotb_spi.debug()
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)


    ## Read Firmware Type
    version = await driver.readFirmwareVersion()
    print("Version: ",version)
    assert version == 0xffab

    ## Read Firmware ID
    id = await driver.readFirmwareID()
    print("FW ID:",hex(id))
    assert id == 0xff00



@cocotb.test(timeout_time = 1 , timeout_unit = "ms")
async def test_fw_id_ftdi(dut):

    #rfg.core.debug()
    #rfg.cocotb.cocotb_spi.debug()
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getFTDIDriver(dut)


    ## Read Firmware Type
    version = await driver.readFirmwareVersion()
    print("Version: ",hex(version))
    assert version == 0xffab

    ## Read Firmware ID
    id = await driver.readFirmwareID()
    print("FW ID:",hex(id))
    assert id == 0xff00


@cocotb.test(timeout_time = 20 , timeout_unit = "ms")
async def test_ftdi_large_read(dut):
    """This test reads firmware id before and after a large read to make sure the rfg protocol returns the requested number of bytes and the simulation code receives them correctly"""
    #rfg.core.debug()
    #rfg.cocotb.cocotb_spi.debug()
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")

    # Run test with all drivers
    ########
    #drivers = [await astep24_3l_sim.getFTDIDriver(dut)]
    drivers = [await astep24_3l_sim.getFTDIDriver(dut),await astep24_3l_sim.getDriver(dut),await astep24_3l_sim.getUARTDriver(dut)]
    #drivers = [await astep24_3l_sim.getUARTDriver(dut)]
    #drivers = [await astep24_3l_sim.getDriver(dut)]
    for driver in drivers:


    #driver = await astep24_3l_sim.getFTDIDriver(dut)
        print(f"======== Start driver test {driver} ")

        version = await driver.readFirmwareVersion()
        print("Version: ",hex(version))
        assert version == 0xffab

        ## Read Firmware Type
        await driver.readoutReadBytes(1024)



        bufferSize = await driver.readoutGetBufferSize()
        assert 0 == bufferSize

        ## Read Firmware Type
        version = await driver.readFirmwareVersion()
        print("Version: ",hex(version))
        assert version == 0xffab

        await Timer(100, units="us")
