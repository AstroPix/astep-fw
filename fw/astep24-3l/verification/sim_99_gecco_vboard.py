import sys
import os
import os.path

import rfg.core
import cocotb
from cocotb.triggers    import Timer,RisingEdge,Join,Combine
from cocotb.clock       import Clock

import vip.cctb
import vip.astropix3

## Import simulation target driver
import astep24_3l_sim

@cocotb.test(timeout_time = 10 , timeout_unit = "ms")
async def test_update_vb(dut):

    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    #rfg.core.debug()

    ##########

    ## Get Voltage Board
    vb = driver.geccoGetVoltageBoard()
    ## Set Dac Values
    vb.dacvalues =  (8, [0, 0, 1.1, 1, 0, 0, 1, 1.100])

    #print("Gecco Bits: ",vb.sendBitsToCard(vb.generateDacBits()))
    #vb.sendBitsToCard(vb.generateDacBits())
    await vb.update(ckdiv = 1 )

    await Timer(50, units="us")