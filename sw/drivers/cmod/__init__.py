from drivers.boards.board_driver import BoardDriver

from .injector import Injector
import drivers.astep.housekeeping

import rfg.io
import rfg.core
import rfg.discovery



class CMODBoard(BoardDriver): 

    def __init__(self,rfg):
        BoardDriver.__init__(self,rfg)
        self.houseKeeping = drivers.astep.housekeeping.Housekeeping(self,rfg)#Refactor to remove pointer to rfg and to BoardDriver
        self.injector = None

    def selectUARTIO(self,portPath : str | None = None ):
        """This method is common to all targets now, because all targets have a USB-UART Converter available"""
        if portPath is None:
            from drivers.astep.serial import getSerialPort
            port = drivers.astep.serial.getSerialPort()
            if port is None:
                raise RuntimeError("No Serial Port could be listed")
            else:
                portPath = port.device
        self.rfg.withUARTIO(portPath)
        return self

    def getFPGACoreFrequency(self):
        return 60000000

    def getInjector(self, period=100, clkdiv=300, initdelay=100, cycle=0, ppset=1) -> Injector:
        if self.injector is None:
            self.injector = Injector(self.rfg, period, clkdiv, initdelay, cycle, ppset)
        return self.injector
