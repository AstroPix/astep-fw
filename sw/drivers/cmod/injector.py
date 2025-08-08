# -*- coding: utf-8 -*-
""""""
"""
Created on Sun Jun 27 21:03:43 2021

@author: Nicolas Striebig

Modified for CMOD board on A-STEP
Adrien Laviron Thu Aug 7 2025
"""

import logging

PG_CTRL_NONE        = 0
PG_CTRL_RESET        = 1
PG_CTRL_SUSPEND     = 1 << 1 
PG_CTRL_SYNCED      = 1 << 2
PG_CTRL_TRIGGER     = 1 << 3 
PG_CTRL_WRITE       = 1 << 4


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def debug():
    logger.setLevel(logging.DEBUG)

class Injector:
    """
    Sets injection setting for GECCO Injectionboard
    This class takes care of configuring the injection pattern generator in firmware
    The Injection Board DACs are configured through the associated VoltageBoard instance accessible via self.voltageBoard property
    """

    def __init__(self,rfg,registerNamePrefix = "LAYERS_INJ") -> None:
        self._period = 100
        self._clkdiv = 300
        self._initdelay = 100
        self._cycle = 0
        self._pulsesperset = 1
        ## RFG Registers
        self.rfg = rfg
        self.controlStickBits = PG_CTRL_NONE
        self._rfgCtrlRegister = self.rfg.Registers[f"{registerNamePrefix}_CTRL"]
        self._rfgWaddrRegister = self.rfg.Registers[f"{registerNamePrefix}_WADDR"]
        self._rfgWdataRegister = self.rfg.Registers[f"{registerNamePrefix}_WDATA"]


    @property
    def period(self) -> int:
        """Injection period"""
        return self._period

    @period.setter
    def period(self, period: int) -> None:
        if 0 <= period <= 255:
            self._period = period

    @property
    def cycle(self) -> int:
        """Injection #pulses"""
        return self._cycle

    @cycle.setter
    def cycle(self, cycle: int) -> None:
        if 0 <= cycle <= 65535:
            self._cycle = cycle

    @property
    def clkdiv(self) -> int:
        """Injection clockdivider"""
        return self._clkdiv

    @clkdiv.setter
    def clkdiv(self, clkdiv: int) -> None:
        if 0 <= clkdiv <= 65535:
            self._clkdiv = clkdiv

    @property
    def initdelay(self) -> int:
        """Injection initdelay"""
        return self._initdelay

    @initdelay.setter
    def initdelay(self, initdelay: int) -> None:
        if 0 <= initdelay <= 65535:
            self._initdelay = initdelay

    @property
    def pulsesperset(self) -> int:
        """Injection pulses/set"""
        return self._pulsesperset

    @pulsesperset.setter
    def pulsesperset(self, pulsesperset: int) -> None:
        if 0 <= pulsesperset <= 255:
            self._pulsesperset = pulsesperset

    def __patgenwrite(self, address: int, value: int) -> bytearray:
        """Subfunction of patgen()
        This method writes to the patgen module through register file
        We write Patgen register address, data etc.. to RegisterFile, which propagates a register write in the Patgenmodule
        :param address: Register address in the patgen module
        :param value: Value to append to writebuffer
        """
        self.rfg.addWrite(self._rfgWaddrRegister,address)
        self.rfg.addWrite(self._rfgWdataRegister,value)
        self.__patgenCtrl(self.controlStickBits | PG_CTRL_WRITE)
        self.__patgenCtrl(self.controlStickBits)

    def __patgenCtrl(self, value : int):
        """Use PG_CTRL_RESET or PG_CTRL_SUSPEND as Or pattern, e.g PG_CTRL_RESET | PG_CTRL_SUSPEND """
        self.rfg.addWrite(self._rfgCtrlRegister,value)

    def __patgen(self):
        """Generate vector for injectionpattern
        """
        # Set pulses per set
        self.__patgenwrite(7, self._pulsesperset)
        # Set period
        self.__patgenwrite(8, self._period)
        # Set flags
        self.__patgenwrite(9, 0b010100)
        # Set runlength
        self.__patgenwrite(10, self._cycle >> 8)
        self.__patgenwrite(11, self._cycle % 256)
        # Set initial delay
        self.__patgenwrite(12, self._delay >> 8)
        self.__patgenwrite(13, self._delay % 256)
        # Set clkdiv
        self.__patgenwrite(14, self._clkdiv >> 8)
        self.__patgenwrite(15, self._clkdiv % 256)

    async def stop(self):
        """
        Stop injection
        """
        self.controlStickBits = PG_CTRL_SUSPEND | PG_CTRL_RESET
        self.__patgenCtrl(self.controlStickBits)
        await self.rfg.flush()

    async def start(self) -> None:
        """Start injection - This method is synchronous to hardware"""
        # Stop injection
        await self.stop()
        # Update injector config
        self.__patgen()
        # Load injector config
        self.__patgenCtrl(PG_CTRL_SUSPEND | PG_CTRL_RESET)
        self.__patgenCtrl(PG_CTRL_NONE)
        self.controlStickBits = PG_CTRL_NONE
        await self.rfg.flush()
