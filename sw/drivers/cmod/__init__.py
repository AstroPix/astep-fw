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

    async def enableLayersReadout(self, layerlst:list, autoread:bool, flush:bool=False):
        """
        Enables readout for a list of layers:
         - Disable autoread and chipselect for all layers
         - Disable MISO for all layers
         - Enable autoread and chipselect for selected layers
         - Enable MISO for select layers
         - Lower shared hold
        :param layerlst: list of layers numbers (int) for which readout will be enabled
        :param autoread: bool, True for autoread
        :param flush:
        """
        await self.disableLayersReadout(flush=False)
        if 0 in layerlst: await self.setLayerConfig(layer=0, hold=True, reset=False, autoread=autoread, chipSelect=True, disableMISO=False, flush=False)
        if 1 in layerlst: await self.setLayerConfig(layer=1, hold=False, reset=False, autoread=autoread, chipSelect=True, disableMISO=False, flush=False)
        if 2 in layerlst: await self.setLayerConfig(layer=2, hold=False, reset=False, autoread=autoread, chipSelect=True, disableMISO=False, flush=False)
        await self.holdLayers(hold=False, flush=flush)

    async def disableLayersReadout(self, flush:bool=True):
        """
        Disable readout for all layers
         - Raise shared Hold
         - Disable autoread, chipselect and MISO
        """
        await self.setLayerConfig(layer=0, hold=True, reset=False, autoread=False, chipSelect=False, disableMISO=True, flush=False)
        await self.setLayerConfig(layer=1, hold=False, reset=False, autoread=False, chipSelect=False, disableMISO=True, flush=False)
        await self.setLayerConfig(layer=2, hold=False, reset=False, autoread=False, chipSelect=False, disableMISO=True, flush=flush)


