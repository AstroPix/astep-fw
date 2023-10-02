
import rfg.core
import importlib
from threading import Event 

## IO Flag to ensure any blocking lowlevel IO is stopped when main application requests it
stopIO = Event()

def cancelIO():
    """Flags all IO Drivers to stop any long running blocking IO"""
    stopIO.set()

def isIOCancelled():
    return stopIO.is_set()


## If Python Serial is installed, offer to use UART IO
serialLoader = importlib.find_loader('serial')
if serialLoader is not None: 
    import rfg.io.uart


    def withUARTIO(self,port, speed:int | None = None) -> rfg.core.AbstractRFG :
        uartIO = rfg.io.uart.UARTIO()
        uartIO.port = port 
        if not speed is None:
            uartIO.baud = speed
        self.withIODriver(uartIO)
        return self

    rfg.core.AbstractRFG.withUARTIO = withUARTIO


## If FTDI D2XX is installed, offer to use FTDI
ftdiLoader = importlib.find_loader('ftd2xx')
if ftdiLoader is not None: 
    
    import rfg.io.ftdi as ftd

    def withFTDIIO(self,searchPattern : str, searchFlag = ftd.FLAG_LIST_SERIAL ) -> rfg.core.AbstractRFG :
        io = ftd.FTDIIO(searchPattern = searchPattern, searchFlag = searchFlag)
        self.withIODriver(io)
        return self

    rfg.core.AbstractRFG.withFTDIIO = withFTDIIO

    pass
    #import rfg.io.uart