# -*- coding: utf-8 -*-
""""""

"""
Created on Fri Jun 25 16:28:27 2021

@author: Nicolas Striebig
Editor for astropix.py module: Autumn Bauman

Functions for ASIC configuration
"""
import logging

# import asyncio
import math
import sys
import time

import yaml
from bitstring import BitArray

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def debug():
    logger.setLevel(logging.DEBUG)


## Constants
##############

# SR
SPI_SR_BROADCAST = 0x7E
SPI_SR_BIT0 = 0x00
SPI_SR_BIT1 = 0x01
SPI_SR_LOAD = 0x03
SPI_SR_TDAC_LOAD = 0x06
SPI_EMPTY_BYTE = 0x00

# Daisychain 3bit Header + 5bit ID
SPI_HEADER_EMPTY = 0b001 << 5
SPI_HEADER_ROUTING = 0b010 << 5
SPI_HEADER_SR = 0b011 << 5


class Asic:
    """Configure ASIC"""

    def __init__(
        self, chipname: str = "astropix", chipversion: int = 3, nchips: int = 1
    ) -> None:
        """ """
        self._chipname = chipname
        self._chipversion = chipversion
        self._num_chips = nchips
        self._num_rows = 35
        self._num_cols = 35

        self.asic_config = {}
        self.asic_tdac_config = {}

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
        """Get/set number of chips in chain setup
        :returns: Number of chips in chain setup
        """
        return self._num_chips

    @num_chips.setter
    def num_chips(self, chips):
        self._num_chips = chips


    @property
    def internal_vdac(self, chip: int, dac: str) -> None:
        return self.asic_config[f"config_{chip}"]['vdacs'][dac]

    @num_chips.setter
    def internal_vdac(self, chip: int, dac: str, voltage: float, vdda: float = 1.8, nbits: int = 10) -> None:
        """Set integrated VDAC voltage

        :param dac: Name of dac
        :param voltage: Voltage from 0 to 1.8
        :param vdd: Supply voltage VDDA
        :param nbits: VDAC resolution
        """
        if dac in self.asic_config[f"config_{chip}"]['vdacs'] and 0 <= voltage <= 1.8:
            dacval = voltage * vdda / 2**nbits
            self.asic_config[f"config_{chip}"]['vdacs'][dac] = dacval
            logger.debug('Set internal vdac: %s to %d V (dacval: %d)', dac, voltage, dacval)
        else:
            logger.warning('Can not set internal vdac: %s to %d V!', dac, voltage)

    def interrupt_pushpull(self, chip: int, enable: bool):
        self.asic_config[f"config_{chip}"]["digitalconfig"]["interrupt_pushpull"][1] = (
            0 if enable is False else 1
        )

    def enable_inj_row(self, chip: int, row: int):
        """
        Enable injection in specified row
        Takes:
        row: int -  Row number
        """
        if row < self.num_rows:
            self.asic_config[f"config_{chip}"]["recconfig"][f"col{row}"][1] = (
                self.asic_config[f"config_{chip}"]["recconfig"].get(
                    f"col{row}", 0b001_11111_11111_11111_11111_11111_11111_11110
                )[1]
                | 0b000_00000_00000_00000_00000_00000_00000_00001
            )
        

    def enable_inj_col(self, chip: int, col: int):
        """
        Enable injection in specified column
        Takes:
        col: int -  Column number
        """
        if col < self.num_cols:
            self.asic_config[f"config_{chip}"]["recconfig"][f"col{col}"][1] = (
                self.asic_config[f"config_{chip}"]["recconfig"].get(
                    f"col{col}", 0b001_11111_11111_11111_11111_11111_11111_11110
                )[1]
                | 0b010_00000_00000_00000_00000_00000_00000_00000
            )
        

    def enable_ampout_col(self, chip: int, col: int):
        """
        Enables analog output, Select Col for analog mux and disable other cols
        Takes:
        chip:int - chip to enable analog out in daisy chain
        col:int - column in row0 for analog output
        """

        # Disable all analog pixels
        for i in range(self.num_cols):
            self.asic_config[f"config_{chip}"]["recconfig"][f"col{col}"][1] = (
                self.asic_config[f"config_{chip}"]["recconfig"][f"col{col}"][1]
                & 0b011_11111_11111_11111_11111_11111_11111_11111
            )

        # Enable analog pixel in column <col>
        self.asic_config[f"config_{chip}"]["recconfig"][f"col{col}"][1] = (
            self.asic_config[f"config_{chip}"]["recconfig"][f"col{col}"][1]
            | 0b100_00000_00000_00000_00000_00000_00000_00000
        )


    def enable_pixel(self, chip: int, col: int, row: int):
        """
        Turns on comparator in specified pixel
        Takes:
        chip: int - chip in the daisy chain
        col: int - Column of pixel
        row: int - Row of pixel
        """
        assert row >= 0 and row < self.num_rows, (
            f"Row outside of accepted range 0 <= row < {self.num_rows}"
        )
        assert col >= 0 and col < self.num_cols, (
            f"Row outside of accepted range 0 <= row < {self.num_cols}"
        )
        #logger.info(f"Enable pixel: {self.asic_config}")
        if row < self.num_rows and col < self.num_cols:
            self.asic_config[f"config_{chip}"]["recconfig"][f"col{col}"][1] = (
                self.asic_config[f"config_{chip}"]["recconfig"].get(
                    f"col{col}", 0b001_11111_11111_11111_11111_11111_11111_11110
                )[1]
                & ~(2 << row)
            )

    def disable_pixel(self, chip: int, col: int, row: int):
        """
        Disable comparator in specified pixel

        Takes:
        chip: int - chip in the daisy chain
        col: int - Column of pixel
        row: int - Row of pixel
        """
        if row < self.num_rows and col < self.num_cols:
            self.asic_config[f"config_{chip}"]["recconfig"][f"col{col}"][1] = (
                self.asic_config[f"config_{chip}"]["recconfig"].get(
                    f"col{col}", 0b001_11111_11111_11111_11111_11111_11111_11110
                )[1]
                | (2 << row)
            )

    def disable_inj_row(self, chip : int, row: int):
        """Disable row injection switch
        :param row: Row number
        """
        if row < self.num_rows:
            self.asic_config[f"config_{chip}"]["recconfig"][f"col{row}"][1] = (
                self.asic_config[f"config_{chip}"]["recconfig"].get(
                    f"col{row}", 0b001_11111_11111_11111_11111_11111_11111_11110
                )[1]
                & 0b111_11111_11111_11111_11111_11111_11111_11110
            )

    def disable_inj_col(self, chip : int, col: int):
        """Disable col injection switch
        :param col: Col number
        """
        if col < self.num_cols:
            self.asic_config[f"config_{chip}"]["recconfig"][f"col{col}"][1] = (
                self.asic_config[f"config_{chip}"]["recconfig"].get(
                    f"col{col}", 0b001_11111_11111_11111_11111_11111_11111_11110
                )[1]
                & 0b101_11111_11111_11111_11111_11111_11111_11111
            )

    def get_pixel(self, chip : int, col: int, row: int):
        return self.is_pixel_enabled(chip, col, row)

    def set_vinj(self,chip:int,inj:float):
        #logger.info(f"Set vinj: {self.asic_config}")
        self.asic_config[f"config_{chip}"]["vdacs"]["vinj"][1] = int( inj / 1000 * 1024 / 1.8 ) 

    def is_pixel_enabled(self, chip : int, col: int, row: int):
        """
        Checks if a given pixel is enabled
        Takes:
        col: int - column of pixel
        row: int - row of pixel
        """
        if row < self.num_rows:
            if self.asic_config[f"config_{chip}"]["recconfig"].get(f"col{col}")[1] & (1 << (row + 1)):
                return False
            return True

        logger.error("Invalid row %d larger than %d", row, self.num_rows)
        return None

    def reset_recconfig(self, chip : int):
        """
        Reset recconfig by disabling all pixels and disabling all injection switches and mux ouputs
        """
        for key in self.asic_config[f"config_{chip}"]["recconfig"]:
            self.asic_config[f"config_{chip}"]["recconfig"][key][1] = (
                0b001_11111_11111_11111_11111_11111_11111_11110
            )

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
            logger.error("Bad setting - Allowed Values 0 - %d", 2**nbits - 1)
            # return None
            sys.exit(1)

    def load_conf_from_yaml(self, filename: str, **kwargs) -> None:
        """Load ASIC config from yaml
        :param chipversion: AstroPix version
        :param filename: Name of yml file in config folder
        """
        ## Name the chip astropix by default
        chipname = kwargs.get("chipname", "astropix")
        self.chipname = chipname

        with open(f"{filename}", "r", encoding="utf-8") as stream:
            try:
                dict_from_yml = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                logger.error(exc)

        # Get Chain settings
        try:
            self._num_chips = dict_from_yml[self.chip].get("chain")["length"]
            logger.info(
                "%s%d  Configuration file with %d chips found!",
                self.chipname,
                self.chipversion,
                self._num_chips,
            )
        except (KeyError, TypeError):
            logger.debug(
                "%s%d DaisyChain Length config not found!",
                self.chipname,
                self.chipversion,
            )
            logger.debug(
                "Use %s%d DaisyChain Length %i from chipsPerRow run parameter",
                self.chipname,
                self.chipversion,
                self._num_chips,
            )
        logger.info(
            "%s%d Number of chips in chain: %d ",
            self.chipname,
            self.chipversion,
            self._num_chips,
        )

        # Get chip geometry
        try:
            self.num_cols = dict_from_yml[self.chip].get("geometry")["cols"]
            self.num_rows = dict_from_yml[self.chip].get("geometry")["rows"]

            logger.info(
                "%s%d matrix dimensions found!", self.chipname, self.chipversion
            )
        except KeyError:
            logger.error(
                "%s%d matrix dimensions not found!", self.chipname, self.chipversion
            )
            # sys.exit(1)

        # Get chip configs
        for chip_number in range(self._num_chips):
            try:
                self.asic_config[f"config_{chip_number}"] = dict_from_yml.get(
                    self.chip
                )[f"config_{chip_number}"]
                logger.info("Chain chip_%d config found!", chip_number)
            except KeyError:
                logger.error("Chain chip_%d config not found!", chip_number)
                raise RuntimeError(f"Chain chip_{chip_number} config not found, check the config file syntax!")
        
        # Get chip TDAC configs
        if self.chipversion == 4:
            for chip_number in range(self.num_chips):
                try:
                    self.asic_tdac_config[f'tdac_config_{chip_number}'] = dict_from_yml.get(self.chip)[f'tdac_config_{chip_number}']
                    logger.info("Chain chip_%d TDAC config found!", chip_number)
                except KeyError:
                    logger.error("Telescope chip_%d tdac config not found!", chip_number)
                    raise RuntimeError(f"Chain chip_{chip_number} TDAC config not found, check the config file syntax!")

    def getChipsConfigs(self, msbfirst: bool = False, targetChip: int = -1) -> BitArray:
        """
        Generate asic bitvector from digital, bias and dacconfig.
        Use this method to get the List of Shift Register Config bits for one or multiple astropix in a daisychain

        This method returns an array of bitvector, each for a chip in the daisychain, in reverse order!
        It means if you have 2 chips, you will get first the bits of chip_1, then chip_0
        
        If the targetChip parameter is used, the array contains one bitvector for the target chip.

        Args:

            msbfirst(bool,optional): Send vector MSB first
            targetChip(int,optional): Returns only the bits for the selected Astropix - if set to -1, returns for all the Astropix - no effect if the configuration is not multichip
        """

        chipConfigs = []

        rangeStart = self._num_chips - 1 if targetChip == -1 else targetChip
        rangeStop = -1 if targetChip == -1 else targetChip - 1
        for chip in range(rangeStart, rangeStop, -1):
            chipBitvector = BitArray()
            for key in self.asic_config[f"config_{chip}"]:
                for values in self.asic_config[f"config_{chip}"][key].values():
                    if key == "vdacs":
                        bitvector_vdac_reversed = BitArray(
                            self.__int2nbit(values[1], values[0])
                        )
                        bitvector_vdac_reversed.reverse()
                        chipBitvector.append(bitvector_vdac_reversed)
                    else:
                        chipBitvector.append(self.__int2nbit(values[1], values[0]))

            logger.debug("Generated chip_%d config successfully!", chip)

            if not msbfirst:
                chipBitvector.reverse()

            # Add chip config to result
            chipConfigs.append(chipBitvector)

        return chipConfigs
    
    def getChipsTDACConfigs(self, row: int = 0, msbfirst: bool = False, targetChip: int = -1) -> BitArray:
        """
        Generate asic bitvector from digital, bias and dacconfig.
        Use this method to get the List of Shift Register Config bits for one or multiple astropix in a daisychain

        This method returns an array of bitvector, each for a chip in the daisychain, in reverse order!
        It means if you have 2 chips, you will get first the bits of chip_1, then chip_0
        
        If the targetChip parameter is used, the array contains one bitvector for the target chip.

        Args:

            msbfirst(bool,optional): Send vector MSB first
            targetChip(int,optional): Returns only the bits for the selected Astropix - if set to -1, returns for all the Astropix - no effect if the configuration is not multichip
        """

        chipTDACConfigs = []

        rangeStart = self._num_chips - 1 if targetChip == -1 else targetChip
        rangeStop = -1 if targetChip == -1 else targetChip - 1
        for chip in range(rangeStart, rangeStop, -1):
            chipBitvector = BitArray()
            chipBitvector.append(self.__int2nbit(self.asic_tdac_config[f"tdac_config_{chip}"][f"row{row}"][1], self.asic_tdac_config[f"tdac_config_{chip}"][f"row{row}"][0]))

            logger.debug("Generated chip_%d TDAC row %d config successfully!", chip, row)

            if not msbfirst:
                chipBitvector.reverse()

            # Add chip config to result
            chipTDACConfigs.append(chipBitvector)

        return chipTDACConfigs
        
    def getConfigBits(self, msbfirst: bool = False, targetChip: int = -1, limit:int|None = None, tdac: bool = False ) -> BitArray:
        """
        Generate asic bitvector from digital, bias and dacconfig.
        Use this method to get the List of Shift Register Config bits for one or multiple astropix in a daisychain

        This method returns all bits concatenated!

        Args:

            msbfirst(bool,optional): Send vector MSB first
            targetChip(int,optional): Returns only the bits for the selected Astropix - if set to -1, returns for all the Astropix - no effect if the configuration is not multichip
        """
        if tdac:
            configs = self.getChipsTDACConfigs(msbfirst=msbfirst,targetChip=targetChip)
        else:
            configs = self.getChipsConfigs(msbfirst=msbfirst,targetChip=targetChip)

        bitsConcatenated = BitArray()
        bits = []
        for config in configs:
            bits.extend(config)
            bitsConcatenated.append(config)

        if limit is not None:
            bitsConcatenated = bitsConcatenated[:limit]

        return bitsConcatenated

    def getRoutingFrame(self, firstChipID: int = 0, paddingBytes: int = 2):
        """
        Returns the Routing Bytes to write to Astropix - writting to the Chip is done by th Board Driver

        Args:

            paddingBytes(int): The number of dummy 0x00 bytes to add after the initial routing command header - Set this to roughly the number of chips in the daisychain * 2
            firstChipID(int): The ID for the first chip, the following chip in the daisychain will be assigned firstChipID+1
        """
        frame = [SPI_HEADER_ROUTING | firstChipID] + [0x00] * paddingBytes
        logger.debug(
            f"Routing frame length={len(frame)},paddingBytesCount={paddingBytes}"
        )
        return frame

    def getSPIConfigFrame(
        self,
        load: bool = True,
        n_load: int = 10,
        broadcast: bool = False,
        targetChip: int = 0,
        config: BitArray | None = None,
        tdac: bool = False
    ) -> bytearray:
        """
        Converts the ASIC Config bits to the SPI Bytes to write to Astropix
        This method only creates a frame for a single chip. Make sure the targetChip parameter is within configured range

        :param load: bool, includes load signal, default=True
        :param n_load: int, length of load signal, default=10
        :param broadcast: bool, Enable Broadcast - in that case the config of targetChip will be broadcasted, default=False
        :param layer: int, daisy chain to target, default=0
        :param targetChip: int, ChipID of source config, set in header if !broadcast, default=0
        :param config: BitArray, vector of config bits, default=None (generated from targetchip and layer)
        :returns: SPI ASIC config pattern

        """

        assert targetChip >= 0 and targetChip < self._num_chips, (
            "Target Chip is out of range"
        )

        ## Generate Bit vector for config
        if config is None:
            config = self.getConfigBits(
                targetChip=targetChip,
                msbfirst=False,
                tdac=tdac,
            )
            logger.info("SPI Config bits, tdac %s, len=%d", tdac, len(config))

        # Write SPI SR Command to set MUX
        if broadcast:
            data = bytearray([SPI_SR_BROADCAST])
        else:
            data = bytearray([SPI_HEADER_SR | targetChip])

        # data
        for bit in config:
            sin = SPI_SR_BIT1 if bit else SPI_SR_BIT0
            data.append(sin)

        # Append Load signal and empty bytes
        if load:
            if tdac:
                data.extend([SPI_SR_TDAC_LOAD] * n_load)
            else:
                data.extend([SPI_SR_LOAD] * n_load)

        # Append 2 Empty bytes per chip in the chip, to ensure the config frame is pushed completely through the chain
        data.extend([SPI_EMPTY_BYTE] * ((self._num_chips - 1) * 2))
        logger.debug("Length: %d\n Data (%db): %s\n", len(data), len(config), config)
        return data

    def ram_set_all(self, value:int, layer: int = 0, row: int = 0):
        bits_per_field = 5

        all_values=0
        for _ in range(self.num_cols):
            all_values=(all_values << bits_per_field) | value

        self.asic_tdac_config[f"tdac_config_{layer}"][f"row{row}"] = [self.num_cols*bits_per_field, all_values]
    ##################################
    ## OLD ORIGINAL CODE WHERE THE ASIC MODEL also Wrote its config via RFG
    ## NOW Methods above generate the Bytes and bits sequences for SPI or SR config and the Board Driver writes them to the correct register in the firmware
    ###########################

    ## SR Update
    # async def writeConfigSR(self, ckdiv=8, limit:int|None=None):
    #    """This method writes the Config bits through the register file bits (SIN,CK1,CK2, LOAD)
    #    Args:
    #        ckdiv(int) : Repeats the write for ck1/ck2/load ckdiv times to strech the signal. Set this value higher for faster software interface
    #        limit(int) : Only write limit bits to SR - Mostly useful in simulation to limit runtime which checking the I/O are correctly driven
    #    """
    #    ## Generate Bit vector for config
    #    bits = self.gen_config_vector_SR(msbfirst = False)
    #    if limit is not None:
    #        bits = bits[:limit]

    #    logger.info("Writing SR Config for row=%d,len=%d",self.row,len(bits))

    #    ## Find target register to write to for IO
    #    targetRegister = self.rfg.Registers[self.rfgSRRegisterName]

    #    ## Write to SR using register
    #    for bit in bits:

    #        # SIN (bit 3 in register)
    #        sinValue = (1 if bit == True else 0) << 2
    #        self.rfg.addWrite(register = targetRegister, value = sinValue, repeat = ckdiv) #ensure SIN has higher delay than CLK1 to avoid setup violation / incorrect sampling

    #        # CK1
    #        self.rfg.addWrite(register = targetRegister, value = sinValue | 0x1 , repeat = ckdiv)
    #        self.rfg.addWrite(register = targetRegister, value = sinValue , repeat = ckdiv)

    #        # CK2
    #        self.rfg.addWrite(register = targetRegister, value = sinValue | 0x2 , repeat = ckdiv)
    #        self.rfg.addWrite(register = targetRegister, value = sinValue , repeat = ckdiv)
    #
    #    ## Set Load (loads start bit 4)
    #    self.rfg.addWrite(register = targetRegister, value = sinValue | (0x1 << (self.row +3)) , repeat = ckdiv)
    #    self.rfg.addWrite(register = targetRegister, value = 0 , repeat = ckdiv)

    #    await self.rfg.flush()

    # async def writeSPIRoutingFrame(self, firstChipID: int = 0x00):
    #    #print(bin(SPI_HEADER_ROUTING | firstChipID))
    #    # await getattr(self.rfg, f"write_layer_{self.row}_mosi_bytes")([SPI_HEADER_ROUTING | firstChipID] + [0x00]*(self._num_chips-1)*4,True)
    #    await self.writeSPI([SPI_HEADER_ROUTING | firstChipID] + [0x00]*(self._num_chips-1)*4)

    # def createSPIConfigFrame(self, load: bool = True, n_load: int = 10, broadcast: bool = False, targetChip: int = 0, value=None)  -> bytearray:
    #    """
    #    Converts the ASIC Config bits to the corresponding bytes to send via SPI
    #    :param value: Bytearray vector of config bits
    #    :param load: Load signal
    #    :param n_load: Length of load signal
    #    :param broadcast: Enable Broadcast - in that case the config of targetChip will be broadcasted
    #    :param targetChip: Chipid of source config, set in header if !broadcast
    #    :returns: SPI ASIC config pattern
    #    """

    #    ## Generate Bit vector for config
    #    if value is None:
    #        value = self.gen_config_vector_SPI(msbfirst = False,targetChip = targetChip)

    #    # Number of Bytes to write
    #    #length = len(value) * 5 + 4
    #

    #    # Write SPI SR Command to set MUX
    #    if broadcast:
    #        data = bytearray([SPI_SR_BROADCAST])
    #    else:
    #        data = bytearray([SPI_HEADER_SR | targetChip])

    #    # data
    #    for bit in value:

    #        sin = SPI_SR_BIT1 if bit == 1 else SPI_SR_BIT0

    #        data.append(sin)

    #    # Append Load signal and empty bytes
    #    if load:
    #        data.extend([SPI_SR_LOAD] * n_load)

    #    # Append 2 Empty bytes per chip in the chip, to ensure the config frame is pushed completely through the chain
    #    data.extend([SPI_EMPTY_BYTE] * ((self._num_chips-1) *4))

    #    logger.debug("Length: %d\n Data (%db): %s\n", len(data), len(value), value)

    #    return data
    #
    # async def writeSPI(self, payload, timeout=1.):
    #    """Writes the payload over SPI
    #    :param payload: bytearray to be written (by chunks of 256 bytes)
    #    :param timeout: maximum duration allowed for a single chunk
    #    :raises: RuntimeError if a chunks times out
    #    """
    #    step  = 256
    #    steps = int(math.ceil(len(payload)/step))
    #    for chunk in range(0, len(payload), step):
    #        chunkBytes = payload[chunk:chunk+step]

    #        #if len(chunkBytes) != 256:
    #        #    task = asyncio.create_task(asyncio.sleep(20))
    #        #    await task
    #
    #        logger.info("Writing Chunck %d/%d len=%d",(chunk/step+1),steps,len(chunkBytes))
    #        await getattr(self.rfg, f"write_layer_{self.row}_mosi_bytes")(chunkBytes,True)

    #        # Wait for the current chunk to be written before sending the next one
    #        maxtime = time.time()+timeout
    #        while (await getattr(self.rfg, f"read_layer_{self.row}_mosi_write_size")() > 0 and time.time() <= maxtime):
    #            time.sleep(0.05)
    #            #pass
    #        #logger.info("Current MISO Write count=%d",await getattr(self.rfg, f"read_layer_{self.row}_mosi_write_size")())
    #        if time.time() > maxtime:
    #            raise RuntimeError("Chunck {}/{} len={} timed out".format(int(chunk/step+1),steps,len(chunkBytes)))

    # async def writeConfigSPI(self, broadcast: bool = False, targetChip : int = 0 ):
    #    """Generate Config Shift Register bits, spi protocol bytes and send them"""
    #    spiBytes = self.createSPIConfigFrame(targetChip = targetChip , broadcast = broadcast)
    #    logger.info("Writing SPI Config for chip %d,row=%d,len=%d",targetChip,self.row,len(spiBytes))
    #    await self.writeSPI(spiBytes)
