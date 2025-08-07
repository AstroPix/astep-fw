# -*- coding: utf-8 -*-
""""""
"""
Created on Sun Jun 27 21:03:43 2021

@author: Nicolas Striebig

Modified for CMOD board on A-STEP
Adrien Laviron Thu Aug 7 2025
"""

import logging


PG_RESET    = 2
PG_SUSPEND  = 3
PG_WRITE    = 4
PG_OUTPUT   = 5
PG_ADDRESS  = 6
PG_DATA     = 7

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
        
        self._period = 0
        self._cycle = 0
        self._clkdiv = 0
        self._initdelay = 0
        self._pulsesperset = 0

        ## RFG Registers
        self.rfg = rfg 
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

        #data = bytearray()

        #data.extend(self.write_register(PG_ADDRESS, address))
        #data.extend(self.write_register(PG_DATA, value))
        #data.extend(self.write_register(PG_WRITE, 1))
        #data.extend(self.write_register(PG_WRITE, 0))

        #return data

    def __patgenCtrl(self, value : int):
        """Use PG_CTRL_RESET or PG_CTRL_SUSPEND as Or pattern, e.g PG_CTRL_RESET | PG_CTRL_SUSPEND """
        self.rfg.addWrite(self._rfgCtrlRegister,value)

    def __patgen(
            self, period: int,
            cycle: int,
            clkdiv: int,
            delay: int) -> bytearray:
        """Generate vector for injectionpattern

        :param period: Set injection period 0-255
        :param cycle: Set injection cycle 0-65535
        :param clkdiv: Set injection clockdivider 0-65535
        :param delay: Set injection pulse delay 0-65535

        :returns: patgen vector
        """

        ## Not used in hw
        #timestamps = [1, 3, 0, 0, 0, 0, 0, 0]
        #for i, val in enumerate(timestamps):
        #    self.__patgenwrite(i, val)

        # Set period
        self.__patgenwrite(8, period)

        # Set flags
        self.__patgenwrite(9, 0b010100)

        # Set runlength
        self.__patgenwrite(10, cycle >> 8)
        self.__patgenwrite(11, cycle % 256)

        # Set initial delay
        self.__patgenwrite(12, delay >> 8)
        self.__patgenwrite(13, delay % 256)

        # Set clkdiv
        self.__patgenwrite(14, clkdiv >> 8)
        self.__patgenwrite(15, clkdiv % 256)
    
    
    #def __patgenreset(self, reset: bool) -> bytes:
    #    self.rfg.addWrite(self._rfgCtrlRegister,PG_CTRL_RESET if reset else 0)
    #    #return self.write_register(PG_RESET, reset)

    #def __patgensuspend(self, suspend: bool) -> bytes:
    #    self.rfg.addWrite(self._rfgCtrlRegister,PG_CTRL_SUSPEND if suspend else 0)
    #    #return self.write_register(PG_SUSPEND, suspend)


    def __configureinjection(self) -> bytes:
        """
        Generate injection vector for set output, pattern and pulses/set

        :returns: config vector
        """

        logger.info("\nWrite Injection Config\n===============================")

            
        self.__patgen(self.period, self.cycle, self.clkdiv, self.initdelay)
        self.__patgenwrite(7, self.pulsesperset)

        #data = output + patgenconfig + pulses
        #logger.debug(f"Injection vector({len(data)} Bytes): 0x{data.hex()}\n")

        #return bytes(data)

    def __start(self):
        """
        Start injection

        :returns: start vector
        """
        ## We are writting Reset on start, reset means the register file values are going to be accepted for next run
        self.__patgenCtrl(PG_CTRL_SUSPEND | PG_CTRL_RESET)
        self.__patgenCtrl(PG_CTRL_NONE)
        self.controlStickBits = PG_CTRL_NONE

        #data = bytearray()

        #data.extend(self.__patgensuspend(True))
        #data.extend(self.__patgenreset(True))
        #data.extend(self.__patgenreset(False))
        #data.extend(self.__patgensuspend(False))

        #logger.debug(f"Start inj({len(data)} Bytes): 0x{data.hex()}\n")

        #return bytes(data)

    def __stop(self):
        """
        Stop injection

        :returns: stop vector
        """
        self.__patgenCtrl(PG_CTRL_SUSPEND | PG_CTRL_RESET)
        self.controlStickBits = PG_CTRL_SUSPEND | PG_CTRL_RESET
        #self.__patgensuspend(True)
        #self.__patgenreset(True)


    def update_inj(self) -> None:
        """Update injectionboard"""

        # Configure injection
        self.__configureinjection()

    async def start(self) -> None:
        """Start injection - This method is synchronous to hardware"""

        # Stop injection
        await self.stop()

        # update inj
        self.update_inj()

        # Start Injection
        self.__start()

        logger.info("Start injection")
        await self.rfg.flush()

    async def stop(self) -> None:
        """Stop injection now"""

        self.__stop()

        logger.info("Stop injection")
        await self.rfg.flush()
