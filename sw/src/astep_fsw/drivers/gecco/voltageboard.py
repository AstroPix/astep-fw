# -*- coding: utf-8 -*-
""""""
"""
Created on 9/09/2023
@author: 
@author: Nicolas Striebig,Richard Leys


Slightly cleaned Model of a Card
19/09/23: Functional Code taken from Nicolas Striebig astropix-python repository

"""
from .card import GeccoCard
from bitstring import BitArray
import copy 



class VoltageBoard(GeccoCard):


    def __init__(self,rfg,slot:int,dacvalues: tuple[int, list[float]] | None = None):
        GeccoCard.__init__(self, rfg,slot)

        self._dacvalues = []  # dacvalues
        self._vcal = 1.0
        self._vsupply = 3.3
        
        if dacvalues is not None:
            self.dacvalues = dacvalues

    def map_dac_to_name(self,dac:int,name:str):

        #@property.setter
        def f(v ): 
            self._dacvalues[dac] =  v
        setattr(self,name,f)

    
    def __vb_vector(self, pos: int, dacs: list[float]) -> BitArray:
        """Generate VB bitvector from position and dacvalues

        :param pos: Card slot
        :param dacs: List with DAC values

        :returns: Voltageboard config vector
        """

        vdacbits = BitArray()

        # Reverse List of dacs in-place
        
        dacs.reverse()

        for vdac in dacs:

            dacvalue = int(vdac * 16383 / self.vsupply / self.vcal)

            vdacbits.append(BitArray(uint=dacvalue, length=14))
            vdacbits.append(BitArray(uint=0, length=2))

        vdacbits.append(BitArray(uint=(0b10000000 >> (pos - 1)), length=8))

        return vdacbits

    def generateDacBits(self) -> BitArray:
        """Generate VB bitvector from position and dacvalues

        :param pos: Card slot
        :param dacs: List with DAC values

        :returns: Voltageboard config vector
        """

        vdacbits = BitArray()

        # Bits are send as Shift Register, so Copy dac values and reverse them because last must be send first
        # Reverse List of dacs in-place
        localDacs = copy.copy(self.dacvalues)
        localDacs.reverse()

        for vdac in localDacs:

            dacvalue = int(vdac * 16383 / self.vsupply / self.vcal)

            vdacbits.append(BitArray(uint=dacvalue, length=14))
            vdacbits.append(BitArray(uint=0, length=2))

        ## Load based on position
        #vdacbits.append(BitArray(uint=(0b10000000 >> (pos - 1)), length=8))

        return vdacbits

    @property
    def vcal(self) -> float:
        """Voltageboard calibration value

        Set DAC to 1V and write measured value to vcal
        """
        return self._vcal

    @vcal.setter
    def vcal(self, voltage: float) -> None:
        if 0.9 <= voltage <= 1.5:
            self._vcal = voltage

    @property
    def vsupply(self) -> float:
        """Voltage supply voltage

        Set voltageboard supply voltage
        """
        return self._vsupply

    @vsupply.setter
    def vsupply(self, voltage: float) -> None:
        if 2.7 <= voltage <= 3.3:
            self._vsupply = voltage

    @property
    def dacvalues(self) -> list[float]:
        """DAC voltages Tuple(Number of DACS, List Dacvalues)"""
        return self._dacvalues

    @dacvalues.setter
    def dacvalues(self, dacvalues: tuple[int, list[float]]) -> None:

        # Get number of dacs and values from tuple
        length, values = dacvalues

        # if length(values) > length strip values
        # if length(values) < length append zeros
        values = values[:length] + [0] * (length - len(values))

        for index, value in enumerate(values):

            # If DAC out of range, set 0
            if not 0 <= value <= 1.8:
                values[index] = 0

        self._dacvalues = values


    async def update(self,ckdiv = 8 ) -> None:
        """Update voltageboard, sends SR bits
        
        :param ckdiv: Number of times the writes are repeated to slow down signals. Set this low in simulations to shorten time
        """

       
        vdacbits = self.generateDacBits()
        await self.sendBitsToCard(bits = vdacbits,ckdiv = ckdiv)

         ## Old 
        #self.write(vbbits)
        # Generate vector
        #vdacbits = self.__vb_vector(self.pos, self.dacvalues)

        # print(f'update_vb pos: {self.pos} value: {self.dacvalues}\n')

        # Generate pattern
        #vbbits = self.gen_gecco_pattern(12, vdacbits, 8)

        # Write to Card
        #self.write(vbbits)