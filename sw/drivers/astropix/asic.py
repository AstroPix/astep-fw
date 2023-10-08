# -*- coding: utf-8 -*-
""""""
"""
Created on Fri Jun 25 16:28:27 2021

@author: Nicolas Striebig
Editor for astropix.py module: Autumn Bauman

Functions for ASIC configuration
"""
import logging
import yaml
import sys

from bitstring import BitArray

import logging 
import time
import asyncio
import math

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def debug():
    logger.setLevel(logging.DEBUG)

## Constants
##############

# SR
SPI_SR_BROADCAST    = 0x7E
SPI_SR_BIT0         = 0x00
SPI_SR_BIT1         = 0x01
SPI_SR_LOAD         = 0x03
SPI_EMPTY_BYTE      = 0x00

# Daisychain 3bit Header + 5bit ID
SPI_HEADER_EMPTY    = 0b001 << 5
SPI_HEADER_ROUTING  = 0b010 << 5
SPI_HEADER_SR       = 0b011 << 5

## Main Class Definition

class Asic():
    """Configure ASIC"""

    def __init__(self,rfg , row : int = 0, srRegisterName : str = "LAYERS_SR_OUT") -> None:
        
        
        self._chipversion = None
        self._num_rows = 35
        self._num_cols = 35

        self.asic_config = {}

        self._num_chips = 1

        self._chipname = ""

        ## Added 09/23 Richard
        self.rfg = rfg
        self.row = row  ## Row ID used to send the bytes to the right firmware interface
        self.rfgSRRegisterName = "LAYERS_SR_OUT"


    @property
    def chipname(self):
        """Get/set chipname

        :returns: chipname
        """
        return self._chipname

    @chipname.setter
    def chipname(self, chipname):
        self._chipname = chipname

    @property
    def chipversion(self):
        """Get/set chipversion

        :returns: chipversion
        """
        return self._chipversion

    @chipversion.setter
    def chipversion(self, chipversion):
        self._chipversion = chipversion

    @property
    def chip(self):
        """Get/set chip+version

        :returns: chipname
        """
        return self.chipname + str(self.chipversion)

    @property
    def num_cols(self):
        """Get/set number of columns

        :returns: Number of columns
        """
        return self._num_cols

    @num_cols.setter
    def num_cols(self, cols):
        self._num_cols = cols

    @property
    def num_rows(self):
        """Get/set number of rows

        :returns: Number of rows
        """
        return self._num_rows

    @num_rows.setter
    def num_rows(self, rows):
        self._num_rows = rows
        
    @property
    def num_chips(self):
        """Get/set number of chips in telescope setup

        :returns: Number of chips in telescope setup
        """
        return self._num_chips

    @num_chips.setter
    def num_chips(self, chips):
        self._num_chips = chips

    def enable_inj_row(self, row: int, inplace:bool=False):
        """
        Enable injection in specified row

        Takes:
        row: int -  Row number
        inplace:bool - True - Updates asic after updating pixel mask
        """
        if row < self.num_rows:
            self.asic_config['recconfig'][f'col{row}'][1] = self.asic_config['recconfig'].get(f'col{row}', 0b001_11111_11111_11111_11111_11111_11111_11110)[1] | 0b000_00000_00000_00000_00000_00000_00000_00001
        if inplace: self.asic_update()

    def enable_inj_col(self, col: int, inplace:bool=False):
        """
        Enable injection in specified column

        Takes:
        col: int -  Column number
        inplace:bool - True - Updates asic after updating pixel mask
        """
        if col < self.num_cols:
            self.asic_config['recconfig'][f'col{col}'][1] = self.asic_config['recconfig'].get(f'col{col}', 0b001_11111_11111_11111_11111_11111_11111_11110)[1] | 0b010_00000_00000_00000_00000_00000_00000_00000
        if inplace: self.asic_update()

    def enable_ampout_col(self, col: int, inplace:bool=False):
        """
        Enables analog output, Select Col for analog mux and disable other cols

        Takes:
        col:int - Column to enable
        inplace:bool - True - Updates asic after updating pixel mask
        """
        #Disable all analog pixels
        for i in range(self.num_cols):
            self.asic_config['recconfig'][f'col{col}'][1] = self.asic_config['recconfig'][f'col{col}'][1] & 0b011_11111_11111_11111_11111_11111_11111_11111

        #Enable analog pixel in column <col>
        self.asic_config['recconfig'][f'col{col}'][1] = self.asic_config['recconfig'][f'col{col}'][1] | 0b100_00000_00000_00000_00000_00000_00000_00000
        
        if inplace: self.asic_update()

    def enable_pixel(self, col: int, row: int, inplace:bool=False):
        """
        Turns on comparator in specified pixel

        Takes:
        col: int - Column of pixel
        row: int - Row of pixel
        inplace:bool - True - Updates asic after updating pixel mask
        """
        assert row >= 0 and row < self.num_rows , f"Row outside of accepted range 0 <= row < {self.num_rows}"
        assert col >= 0 and col < self.num_cols , f"Row outside of accepted range 0 <= row < {self.num_cols}"
        if(row < self.num_rows and col < self.num_cols):
            self.asic_config['recconfig'][f'col{col}'][1] = self.asic_config['recconfig'].get(f'col{col}', 0b001_11111_11111_11111_11111_11111_11111_11110)[1] & ~(2 << row)

        if inplace: self.asic_update()

    def disable_pixel(self, col: int, row: int, inplace:bool=False):
        """
        Disable comparator in specified pixel

        Takes:
        col: int - Column of pixel
        row: int - Row of pixel
        inplace:bool - True - Updates asic after updating pixel mask
        """
        if(row < self.num_rows and col < self.num_cols):
            self.asic_config['recconfig'][f'col{col}'][1] = self.asic_config['recconfig'].get(f'col{col}', 0b001_11111_11111_11111_11111_11111_11111_11110)[1] | (2 << row)
        if inplace: self.asic_update()


    def disable_inj_row(self, row: int):
        """Disable row injection switch
        :param row: Row number
        """
        if row < self.num_rows:
            self.asic_config['recconfig'][f'col{row}'][1] = self.asic_config['recconfig'].get(f'col{row}', 0b001_11111_11111_11111_11111_11111_11111_11110)[1] & 0b111_11111_11111_11111_11111_11111_11111_11110


    def disable_inj_col(self, col: int):
        """Disable col injection switch
        :param col: Col number
        """
        if col < self.num_cols:
            self.asic_config['recconfig'][f'col{col}'][1] = self.asic_config['recconfig'].get(f'col{col}', 0b001_11111_11111_11111_11111_11111_11111_11110)[1] & 0b101_11111_11111_11111_11111_11111_11111_11111

    def get_pixel(self, col: int, row: int):
        return self.is_pixel_enabled(col,row)

    def is_pixel_enabled(self, col: int, row: int):
        """
        Checks if a given pixel is enabled

        Takes:
        col: int - column of pixel
        row: int - row of pixel
        """
        if row < self.num_rows:
            if self.asic_config['recconfig'].get(f'col{col}')[1] & (1<<(row+1)):
                return False
            return True

        logger.error("Invalid row %d larger than %d", row, self.num_rows)
        return None

    def reset_recconfig(self):
        """Reset recconfig by disabling all pixels and disabling all injection switches and mux ouputs
        """
        for key in self.asic_config['recconfig']:
            self.asic_config['recconfig'][key][1] = 0b001_11111_11111_11111_11111_11111_11111_11110


    @staticmethod
    def __int2nbit(value: int, nbits: int) -> BitArray:
        """Convert int to 6bit bitarray

        :param value: Integer value
        :param nbits: Number of bits

        :returns: Bitarray of specified length
        """

        try:
            return BitArray(uint=value, length=nbits)
        except ValueError:
            logger.error('Allowed Values 0 - %d', 2**nbits-1)
            return None

    def load_conf_from_yaml(self, filename: str, **kwargs) -> None:
        """Load ASIC config from yaml
        :param chipversion: AstroPix version
        :param filename: Name of yml file in config folder
        """
        ## Name the chip astropix by default
        chipname = kwargs.get('chipname', 'astropix')
        self.chipname = chipname

        with open(f"{filename}", "r", encoding="utf-8") as stream:
            try:
                dict_from_yml = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                logger.error(exc)

        # Get Telescope settings
        try:
            self.num_chips = dict_from_yml[self.chip].get('chain')['length']

            logger.info("%s%d DaisyChain with %d chips found!", self.chipname, self.chipversion, self.num_chips)
        except (KeyError, TypeError):
            logger.debug("%s%d DaisyChain Length config not found!", self.chipname, self.chipversion)

        # Get chip geometry
        try:
            self.num_cols = dict_from_yml[self.chip].get('geometry')['cols']
            self.num_rows = dict_from_yml[self.chip].get('geometry')['rows']

            logger.info("%s%d matrix dimensions found!", self.chipname, self.chipversion)
        except KeyError:
            logger.error("%s%d matrix dimensions not found!", self.chipname, self.chipversion)
            #sys.exit(1)

        # Get chip configs
        if self.num_chips > 1:
            for chip_number in range(self.num_chips):
                try:
                    self.asic_config[f'config_{chip_number}'] = dict_from_yml.get(self.chip)[f'config_{chip_number}']
                    logger.info("Telescope chip_%d config found!", chip_number)
                except KeyError:
                    logger.error("Telescope chip_%d config not found!", chip_number)
                    #sys.exit(1)
        else:
            try:
                self.asic_config = dict_from_yml.get(self.chip)['config']
                logger.info("%s%d config found!", self.chipname, self.chipversion)
            except KeyError:
                logger.error("%s%d config not found!", self.chipname, self.chipversion)
                #sys.exit(1)


    def gen_config_vector(self, msbfirst: bool = False) -> BitArray:
        """
        Generate asic bitvector from digital, bias and dacconfig

        :param msbfirst: Send vector MSB first
        """
        bitvector = BitArray()

        if self.num_chips > 1:
            for chip in range(self.num_chips-1, -1, -1):

                for key in self.asic_config[f'config_{chip}']:
                    for values in self.asic_config[f'config_{chip}'][key].values():
                        bitvector.append(self.__int2nbit(values[1], values[0]))

                if not msbfirst:
                    bitvector.reverse()

                logger.info("Generated chip_%d config successfully!", chip)
        else:
            for key in self.asic_config:
                for values in self.asic_config[key].values():
                    #bitvector.append(self.__int2nbit(values[1], values[0]))
                    if(key=='vdacs'):
                        bitvector_vdac_reversed = BitArray(self.__int2nbit(values[1], values[0]))
                        bitvector_vdac_reversed.reverse()
                        bitvector.append(bitvector_vdac_reversed)
                    else:
                        bitvector.append(self.__int2nbit(values[1], values[0]))

            if not msbfirst:
                bitvector.reverse()

        logger.debug(bitvector)

        return bitvector    

    def readback_asic(self):
        asicbits = self.gen_asic_pattern(self.gen_asic_vector(), True, readback_mode = True)
        print(asicbits)
        self.nexys.write(asicbits)

    def asic_update(self):
        """
        Remakes configbits and writes to asic. 
        Takes no input and does not return
        """
        if self._chipversion == 1:
            dummybits = self.gen_asic_pattern(BitArray(uint=0, length=245), True) # Not needed for v2
            self.nexys.write(dummybits)

        # Write config
        asicbits = self.nexys.gen_asic_pattern(self.gen_asic_vector(), True)
        for value in asicbits:
            self.nexys.write(value)
        logger.info("Wrote configbits successfully")

    ## SR Update
    async def writeConfigSR(self,ckdiv = 8 , limit : int | None = None ):
        """This method writes the Config bits through the register file bits (SIN,CK1,CK2, LOAD)
        
        Args:
            ckdiv(int) : Repeats the write for ck1/ck2/load ckdiv times to strech the signal. Set this value higher for faster software interface
            limit(int) : Only write limit bits to SR - Mostly useful in simulation to limit runtime which checking the I/O are correctly driven
        """
        ## Generate Bit vector for config 
        bits = self.gen_config_vector(msbfirst = False)
        if limit is not None: 
            bits = bits[:limit]

        logger.info("Writing SR Config for row=%d,len=%d",self.row,len(bits))

        ## Find target register to write to for IO 
        targetRegister = self.rfg.Registers[self.rfgSRRegisterName]

        ## Write to SR using register
        for bit in bits: 


            # SIN (bit 3 in register)
            sinValue = (1 if bit == True else 0) << 2
            self.rfg.addWrite(register = targetRegister, value = sinValue)

            # CK1
            self.rfg.addWrite(register = targetRegister, value = sinValue | 0x1 , repeat = ckdiv)
            self.rfg.addWrite(register = targetRegister, value = sinValue , repeat = ckdiv)

            # CK2
            self.rfg.addWrite(register = targetRegister, value = sinValue | 0x2 , repeat = ckdiv)
            self.rfg.addWrite(register = targetRegister, value = sinValue , repeat = ckdiv)
            
        
        ## Set Load (loads start bit 4)
        self.rfg.addWrite(register = targetRegister, value = sinValue | (0x1 << (self.row +3)) , repeat = ckdiv)
        self.rfg.addWrite(register = targetRegister, value = 0 , repeat = ckdiv)


        await self.rfg.flush()

    ## SPI 
    #############

    def createSPIRoutingFrame():
        pass 


    def createSPIConfigFrame(self, load: bool = True, n_load: int = 10, broadcast: bool = False, targetChip: int = 0)  -> bytearray:
        """
        "Converts the ASIC Config bits to the corresponding bytes to send via SPI

        :param value: Bytearray vector of config bits
        :param load: Load signal
        :param n_load: Length of load signal

        :param broadcast: Enable Broadcast
        :param targetChip: Set chipid if !broadcast

        :returns: SPI ASIC config pattern
        """

        ## Generate Bit vector for config 
        value = self.gen_config_vector(msbfirst = False)

        # Number of Bytes to write
        #length = len(value) * 5 + 4

        ##logger.info("SPI Write Asic Config")
        

        # Write SPI SR Command to set MUX
        if broadcast:
            data = bytearray([SPI_SR_BROADCAST])
        else:
            data = bytearray([SPI_HEADER_SR | targetChip])

        # data
        for bit in value:

            sin = SPI_SR_BIT1 if bit == 1 else SPI_SR_BIT0

            data.append(sin)

        # Append Load signal and empty bytes
        if load:

            data.extend([SPI_SR_LOAD] * n_load)

            data.extend([SPI_EMPTY_BYTE] * n_load)


        logger.debug("Length: %d\n Data (%db): %s\n", len(data), len(value), value)

        return data


    async def writeConfigSPI(self, targetChip : int = 0 ):
        """Generate Config Shift Register bits, spi protocol bytes and send them"""

        spiBytes = self.createSPIConfigFrame(targetChip = targetChip)
        logger.info("Writing SPI Config for chip %d,row=%d,len=%d",targetChip,self.row,len(spiBytes))

        step  = 256
        steps = int(math.ceil(len(spiBytes)/step))
        for chunk in range(0, len(spiBytes), step):
            chunkBytes = spiBytes[chunk:chunk+step]
            logger.info("Writing Chunck %d/%d len=%d",(chunk/step+1),steps,len(chunkBytes))
            await getattr(self.rfg, f"write_layer_{self.row}_mosi_bytes")(chunkBytes,True)

            ## Sleep to give time for the FW to send the bytes, this will be better synchronised in the future
            ## Must be improved
            await asyncio.sleep(0.1)         
            logger.info("Current MISO Write count=%d",await self.rfg.read_layer_0_mosi_write_size())

