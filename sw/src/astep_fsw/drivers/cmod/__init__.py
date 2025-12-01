from drivers.boards.board_driver import BoardDriver

from .injector import Injector

import rfg.io
import rfg.core
import rfg.discovery



class CMODBoard(BoardDriver): 

    def __init__(self,rfg):
        BoardDriver.__init__(self,rfg)
        self.injector = None

    def getFPGACoreFrequency(self):
        return 60000000

    def getInjector(self, period=100, clkdiv=300, initdelay=100, cycle=0, ppset=1) -> Injector:
        if self.injector is None:
            self.injector = Injector(self.rfg, period, clkdiv, initdelay, cycle, ppset)
        return self.injector
