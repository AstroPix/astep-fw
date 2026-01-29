


import sys
import os
import os.path

#sys.path.append(os.path.dirname(__file__)+"/.generated/")

import cocotb
from cocotb.triggers    import Timer,RisingEdge
from cocotb.clock       import Clock

import vip.cctb

import vip.spi
vip.spi.info()

## Import simulation target driver
import astep24_3l_sim

@cocotb.test(timeout_time = 500 , timeout_unit = "us")
async def test_hk_ext_spi_adc(dut):

    ## Init Driver
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Create VIP SPi Slave , cpha is 1 so that the slave samples on posedge which is the second edge (clock is 1 by default)
    slave = vip.spi.VSPISlave(clk = dut.ext_spi_clk, csn = dut.ext_adc_spi_csn,mosi=dut.ext_spi_mosi,miso = dut.ext_adc_spi_miso,misoSize=1,cpol=1,cpha=1,msbFirst=True)
    slave.start_monitor()

    ##
    #await driver.houseKeeping.configureSPI(adc=True,dac=False)
    #await Timer(2, units="us")
    await driver.configureHKSPIFrequency(10000000,flush=True)
    await driver.houseKeeping.selectSPI(adc=True,dac=False)
    
    byte1 = format(7<<3,'08b') # = ‘00111000’
    
    #byte1 = byte1[::-1] = ‘00011100’
    
    byte1 = int(byte1,2)
    
    
    await driver.houseKeeping.writeADCDACBytes([0x7<<3,0xAB,0xCD])
    await Timer(20, units="us")
    
    assert (await slave.getByte()) == 0x38
    assert (await slave.getByte()) == 0xAB
    assert (await slave.getByte()) == 0xCD

    ## Read buffer
    adcBytesCount = await driver.houseKeeping.getADCBytesCount()
    assert(adcBytesCount == 3)
    adcBytes = await driver.houseKeeping.readADCBytes(adcBytesCount)
    assert(len(adcBytes) ==3)
    assert adcBytes == [0x3D,0x3D,0x3D]
    await Timer(5, units="us")

    print(f"Bytes={adcBytes}")
    await driver.houseKeeping.selectSPI(adc=False,dac=False)

    await Timer(50, units="us")


@cocotb.test(timeout_time = 1 , timeout_unit = "ms")
async def test_hk_ext_spi_dac(dut):

    ## Init Driver
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Create VIP SPi Slave
    slave = vip.spi.VSPISlave(clk = dut.ext_spi_clk, csn = dut.ext_dac_spi_csn,mosi=dut.ext_spi_mosi,miso = dut.ext_adc_spi_miso,misoSize=1,cpol=0)
    slave.start_monitor()

    ##
    await driver.houseKeeping.configureSPI(adc=False,dac=True)
    await Timer(2, units="us")
    await driver.houseKeeping.selectSPI(adc=False,dac=True)
    await driver.houseKeeping.writeADCDACBytes([0xAB,0xCD])
    await Timer(50, units="us")
    assert((await driver.houseKeeping.getADCBytesCount())==0)


    slaveByte = await slave.getByte()
    print("Slave Byte: ",slaveByte)
    assert (slaveByte) == 0xAB
    assert (await slave.getByte()) == 0xCD

    await Timer(50, units="us")
