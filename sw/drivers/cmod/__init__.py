from drivers.boards.board_driver import BoardDriver
import rfg.io
import rfg.core
import rfg.discovery



class CMODBoard(BoardDriver): 

    def __init__(self,rfg):
        BoardDriver.__init__(self,rfg)
        self.cards = {}

    def getFPGACoreFrequency(self):
        return 20000000

    def getInjectionBoard(self,slot : int ) -> InjectionBoard:
        """Create or return Voltage board for a certain slot"""
        if slot in self.cards:
            return self.cards[slot]
        else:
            vb = InjectionBoard(rfg = self.rfg, slot = slot)
            self.cards[slot] = vb
            return vb
