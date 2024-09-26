
import sys 
import os 


import  rfg.discovery
import  rfg.cocotb.cocotb_spi
from    rfg.cocotb.cocotb_uart import UARTIO
from    rfg.cocotb.cocotb_spi  import SPIIO


from   drivers.boards.board_driver import BoardDriver
from   drivers.gecco.voltageboard import VoltageBoard
from   drivers.gecco.injectionboard import InjectionBoard

from cocotb.triggers import Timer,RisingEdge

class SimBoard(BoardDriver): 

    def __init__(self,rfg):
        BoardDriver.__init__(self,rfg)


    def getVoltageBoard(self,slot : int = 0 ):
        vb = VoltageBoard(rfg = self.rfg, slot = slot)
        vb.vsupply  = 2.7
        vb.vcal     = .989
        return vb

    def getInjectionBoard(self,slot : int = 1):
        ib = InjectionBoard(rfg = self.rfg, slot = slot)
        ib.voltageBoard = None
        return ib

    def getFPGACoreFrequency(self):
        return 60000000

async def getDriver(dut):

    if os.getenv("ASTEP_HOST_UART",False) is not False:
        return getUARTDriver(dut)
    else:
        return await getSPIDriver(dut)

def getUARTDriver(dut):

    ## Load RF and Setup UARTIO
    firmwareRF = rfg.discovery.loadOneFSPRFGOrFail()

    ## UART
    #########
    if dut._name == "astep24_3l_top":
        rfg_io = UARTIO(dut.uart_rx,dut.uart_tx) ## INtervert Rx/Tx to send to rx and receive from tx!
    else:
        rfg_io = UARTIO(dut.uart_tx_in,dut.uart_rx_out)

    #rfg_io = UARTIO(dut.uart_rx,dut.uart_tx)
    firmwareRF.withIODriver(rfg_io)

    boardDriver = SimBoard(firmwareRF)
    boardDriver.open()

    


    return boardDriver

    
async def getSPIDriver(dut):

    ## Load RF and Setup UARTIO
    firmwareRF = rfg.discovery.loadOneFSPRFGOrFail()

    ## SPI
    #########
    rfg_io = SPIIO(dut)
    await Timer(10, units="us")

    #rfg.cocotb.cocotb_spi.debug()

    ## Sof Reset
    #await rfg_io.softReset()

    firmwareRF.withIODriver(rfg_io)
    await rfg_io.open()
    await Timer(10, units="us")

    boardDriver = SimBoard(firmwareRF)


    return boardDriver