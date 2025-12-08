
import importlib
import importlib.util
from threading import Event

## import rfg.core
from .. import core as rfg_core
from . import uart

## IO Flag to ensure any blocking lowlevel IO is stopped when main application requests it
stopIO = Event()

def cancelIO():
    """Flags all IO Drivers to stop any long running blocking IO"""
    stopIO.set()

def isIOCancelled():
    return stopIO.is_set()


## If Python Serial is installed, offer to use UART IO
serialLoader = importlib.util.find_spec('serial')
if serialLoader is not None:

    def withUARTIO(self,port, baud:int | None = None) -> core.AbstractRFG :
        uartIO = uart.UARTIO()
        uartIO.port = port
        if not baud is None:
            uartIO.baud = baud
        self.withIODriver(uartIO)
        return self

    core.AbstractRFG.withUARTIO = withUARTIO

## If Python spidev is installed, offer to use UART IO
spidevLoader = importlib.util.find_spec('spidev')
if spidevLoader is not None:
    import rfg.io.spidev


    def withSPIDEVIO(self,path:str,gpioPath: str,csGpioLine:int) -> rfg.core.AbstractRFG :
        spiIO = rfg.io.spidev.SPIDEVIO(path,gpioPath,csGpioLine)
        self.withIODriver(spiIO)
        return self

    rfg.core.AbstractRFG.withSPIDEVIO = withSPIDEVIO


## If FTDI D2XX is installed, offer to use FTDI
ftdiLoader = importlib.util.find_spec('ftd2xx')
if ftdiLoader is not None:

    import rfg.io.ftdi as ftd

    def withFTDIIO(self,searchPattern : str, searchFlag = ftd.FLAG_LIST_SERIAL ) -> rfg_core.AbstractRFG :
        io = ftd.FTDIIO(searchPattern = searchPattern, searchFlag = searchFlag)
        self.withIODriver(io)
        return self

    rfg_core.AbstractRFG.withFTDIIO = withFTDIIO

    pass
