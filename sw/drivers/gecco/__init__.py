
from drivers.boards.board_driver import BoardDriver
from .voltageboard import VoltageBoard
from .injectionboard import InjectionBoard
import rfg.io
import rfg.core
import rfg.discovery



class GeccoCarrierBoard(BoardDriver): 

    def __init__(self, rfg):
        BoardDriver.__init__(self, rfg)
        self.cards = {}

    def getFPGACoreFrequency(self):
        return 60000000

    def getVoltageBoard(self, slot:int) -> VoltageBoard:
        """Create or return Voltage board for a certain slot"""
        if slot in self.cards:
            return self.cards[slot]
        else:
            vb = VoltageBoard(rfg = self.rfg, slot = slot)
            self.cards[slot] = vb
            return vb

    def getInjectionBoard(self, slot:int) -> InjectionBoard:
        """Create or return Voltage board for a certain slot"""
        if slot in self.cards:
            return self.cards[slot]
        else:
            vb = InjectionBoard(rfg = self.rfg, slot = slot)
            self.cards[slot] = vb
            return vb

    def selectFTDIFifoIO(self):
        import rfg.io.ftdi
        self.rfg.withFTDIIO("Device A", rfg.io.ftdi.FLAG_LIST_DESCRIPTOR)
        return self

    def geccoGetVoltageBoard(self):
        return self.getVoltageBoard(slot = 4)

    def geccoGetInjectionBoard(self):
        return self.getInjectionBoard(slot = 3)

    async def ioSetInjectionToGeccoInjBoard(self, enable:bool, flush:bool=False):
        v = await self.rfg.read_io_ctrl()
        if enable: v |= 0x8 
        else: v &= ~(0x8)
        await self.rfg.write_io_ctrl(v,flush)

    async def enableLayersReadout(self, autoread:bool, flush:bool=False):
        """
        Enables readout
         - Enable autoread and chipselect
         - Enable MISO for select layers
         - Lower hold
        :param autoread: bool, True for autoread
        :param flush:
        """
        await self.setLayerConfig(layer=0, hold=False, reset=False, autoread=autoread, chipSelect=True, disableMISO=False, flush=flush)

    async def disableLayersReadout(self, flush:bool = True):
        """
        Disable readout
         - Raise Hold
         - Disable autoread, chipselect and MISO
        """
        await self.setLayerConfig(layer=0, hold=True, reset=False, autoread=False, chipSelect=False, disableMISO=True, flush=flush)

