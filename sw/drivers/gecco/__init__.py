
from drivers.boards.board_driver import BoardDriver
from .voltageboard import VoltageBoard
from .injectionboard import InjectionBoard
import rfg.io
import rfg.core
import rfg.discovery



class GeccoCarrierBoard(BoardDriver):

    def __init__(self,rfg):
        BoardDriver.__init__(self,rfg)
        self.cards = {}

    def getVoltageBoard(self,slot : int ) -> VoltageBoard:
        """Create or return Voltage board for a certain slot"""
        if slot in self.cards:
            return self.cards[slot]
        else:
            vb = VoltageBoard(rfg = self.rfg, slot = slot)
            self.cards[slot] = vb
            return vb

    def getInjectionBoard(self,slot : int ) -> InjectionBoard:
        """Create or return Voltage board for a certain slot"""
        if slot in self.cards:
            return self.cards[slot]
        else:
            vb = InjectionBoard(rfg = self.rfg, slot = slot)
            self.cards[slot] = vb
            return vb



    def selectFTDIFifoIO(self):
        import rfg.io.ftdi
        self.rfg.withFTDIIO("Device A",rfg.io.ftdi.FLAG_LIST_DESCRIPTOR)
        return self
