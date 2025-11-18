import importlib.util
import sys

import cocotb
import rfg.discovery
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from rfg.cocotb.cocotb_spi import SPIIO
from rfg.cocotb.cocotb_uart import UARTIO

from drivers.astep.housekeeping import Housekeeping


## Try to load the Firmware RFG package based on currently possible tops
def load_fsp():
    firmwareTops = ["astep24_3l_gecco_astropix3_top", "astep24_3l_top"]
    for candidateTop in firmwareTops:
        if candidateTop in sys.modules:
            return sys.modules[candidateTop]
        elif (spec := importlib.util.find_spec(candidateTop)) is not None:
            print(f"{candidateTop!r} has been imported")
            # from candidateTop import main_rfg
            # If you chose to perform the actual import ...
            module = importlib.util.module_from_spec(spec)
            sys.modules[candidateTop] = module
            spec.loader.exec_module(module)
            return module
            # print(f"{name!r} has been imported")


# import importlib
# boardModule = importlib.find_loader('astep24_3l_gecco_astropix3_top')
# if boardModule is not None:
#    from astep_hktest_top   import main_rfg
# boardModule = importlib.find_loader('astep_ml1_top')
# if boardModule is not None:
#    from astep_ml1_top      import main_rfg


async def common_system_clock(dut):
    cocotb.start_soon(Clock(dut.sysclk, 10, units="ns").start())
    await RisingEdge(dut.sysclk)


async def common_clock_reset_nexys(dut):
    cocotb.start_soon(Clock(dut.sysclk, 10, units="ns").start())
    dut.btnc.value = 0  # Btn pressed is 1
    dut.resn.value = 0
    await Timer(1, units="us")
    dut.resn.value = 1
    await Timer(100, units="us")


async def common_clock_reset_cmod(dut):
    cocotb.start_soon(Clock(dut.sysclk, 10, units="ns").start())
    dut.warm_resn.value = 0
    dut.cold_resn.value = 0
    await Timer(1, units="us")
    dut.warm_resn.value = 1
    dut.cold_resn.value = 1
    await Timer(100, units="us")


async def common_clock_reset(dut):
    cocotb.start_soon(Clock(dut.sysclk, 10, units="ns").start())

    # Init UART TX to FPGA to make sure uart receiver doesn't produce bad data if the uart driver is created later in the test
    if dut._name == "astep24_3l_top":
        dut.uart_rx.value = 1
    else:
        dut.uart_tx_in.value = 1

    ## Other IO Init
    dut.tlu_t0.value = 0
    dut.tlu_trigger.value = 0

    dut.clk_ext.value = 0
    dut.resn.value = 0
    await Timer(1, units="us")
    dut.resn.value = 1
    await RisingEdge(dut.clk_core_resn)


async def start_external_clock(dut):
    return cocotb.start_soon(Clock(dut.clk_ext, 25, units="ns").start())


async def warm_reset(dut):
    dut.resn.value = 0
    await Timer(1, units="us")
    dut.resn.value = 1
    await RisingEdge(dut.clk_core_resn)


def sw_uart_init(dut):
    """This method returns a driver interface for the Readout system, which references RFG and the IO level"""

    ## FW
    ###########
    # loadedFirmware = load_fsp()
    # print("Loaded firmware",loadedFirmware.__name__)
    # rfg = loadedFirmware.main_rfg()
    loadedFirmware = rfg.discovery.loadOneFSPOrFail()
    loadedRFG = loadedFirmware.load_rfg()
    print("Loaded firmware", loadedFirmware.__name__)

    ## UART
    #########
    if loadedFirmware.__name__ == "fsp.astep24_3l_top":
        rfg_io = UARTIO(
            dut.uart_rx, dut.uart_tx
        )  ## INtervert Rx/Tx to send to rx and receive from tx!
    else:
        rfg_io = UARTIO(dut.tx_in, dut.rx_out)

    # print("UART Init: ",len(rfg.commands))
    loadedRFG.withIODriver(rfg_io)
    housekeepingDriver = Housekeeping(loadedRFG)

    return housekeepingDriver


def sw_spi_init(dut):
    """This method returns a driver interface for the Readout system, which references RFG and the IO level"""

    ## FW
    ###########
    # loadedFirmware = load_fsp()
    # print("Loaded firmware",loadedFirmware.name)
    # rfg = loadedFirmware.main_rfg()

    ## UART
    #########
    rfg_io = SPIIO(dut)
    loadedFirmware = load_fsp()
    print("Loaded firmware", loadedFirmware.name)
    rfg = loadedFirmware.main_rfg()
    # print("SPI Init: ",len(rfg.commands))
    rfg.withIODriver(rfg_io)
    housekeepingDriver = Housekeeping(rfg)

    return housekeepingDriver
