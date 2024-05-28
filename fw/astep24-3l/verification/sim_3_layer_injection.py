
import sys
import os

import cocotb
from cocotb.triggers    import Timer,RisingEdge,FallingEdge,with_timeout,Join
from cocotb.clock       import Clock
from cocotbext.uart import UartSource, UartSink

import vip.cctb

import astep24_3l_sim

@cocotb.test(timeout_time = 2 , timeout_unit = "ms")
async def test_injection(dut):

    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    boardDriver = await astep24_3l_sim.getDriver(dut)

    # Get Injection Board from driver
    injBoard = boardDriver.geccoGetInjectionBoard()

    # Configure
    injBoard.initdelay = 4
    injBoard.clkdiv = 2
    injBoard.period = 4
    injBoard.pulsesperset = 4
    injBoard.cycle = 1 # 0 Should mean indefinite

    ## Start
    #########
    async def waitForEdges():
        ## Wait for x pulses
        for i in range(injBoard.pulsesperset):
            await RisingEdge(dut.layers_inj)
            await FallingEdge(dut.layers_inj)

    edgesJob = cocotb.start_soon(waitForEdges())
    await injBoard.start()
    await Join(edgesJob)
   
    
    assert dut.injection_generator.done.value == 1 

    # Make another run 
    injBoard.pulsesperset = 2
    edgesJob = cocotb.start_soon(waitForEdges())
    await injBoard.start()
    await Join(edgesJob)

    assert dut.injection_generator.done.value == 1 
    
   
    await Timer(500, units="us")