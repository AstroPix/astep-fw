import yaml
from bitstring import BitArray

class AstroPixCfg:
    """
    Class to hold and manipulate configuration files and configuration data for AstroPix detectors
    It contains information for a full daisy-chain (=lane) of chips
    Data is stored internally as a dictionary
    """

    def __init__(self, version=None):
        #Define default values for members here
        """
        """
        self.version = version#we will need versioning
        self.cfg = {}

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
            logger.error('Bad setting - Allowed Values 0 - %d', 2**nbits-1)
            #return None
            sys.exit(1)

    def setCfgYaml(self, filename):
        with open(f"{filename}", "r", encoding="utf-8") as stream:
            try:
                self.cfg = yaml.safe_load(stream)["astropix3"]
            except yaml.YAMLError as exc:
                raise exc#Useless right now, may want to do something smart with logging later
        self.nchips = self.cfg["chain"]["length"]
        # V3 single chip: self.nchips = self.cfg["astropix3"]["telescope"]["nchips"]
        self.nrows = self.cfg["geometry"]["rows"]
        self.ncols = self.cfg["geometry"]["cols"]

    def getCfgYaml(self):
        raise NotImplementedError()

    def setCfgBytes(self, bitarray):
        raise NotImplementedError()

    #The following code is just a copy of the functions in drivers/astropix/asic.py
    def getCfgBits(self, targetChip:int = None, msbfirst:bool = False) -> BitArray:
        """
        Generate asic bitvector from digital, bias and dacconfig
        :param msbfirst: Send vector MSB first
        :param targetChip: Returns only the bits for the selected Astropix - if set to -1, returns for all the Astropix - no effect if the configuration is not multichip
        """
        bitvector = BitArray()
        configSource = self.cfg[f'config_{targetChip}'] if (self.nchips>1) else self.cfg["config"]#Latter used for V3 single chip
        for key in configSource:
            for values in configSource[key].values():
                if(key=='vdacs'):
                    bitvector_vdac_reversed = BitArray(self.__int2nbit(values[1], values[0]))
                    bitvector_vdac_reversed.reverse()
                    bitvector.append(bitvector_vdac_reversed)
                else:
                    bitvector.append(self.__int2nbit(values[1], values[0]))
        if not msbfirst:
            bitvector.reverse()
        return bitvector

    def enable_inj_row(self, chip:int, row: int):
        """
        Enable injection in specified row

        Takes:
        row: int -  Row number
        inplace:bool - True - Updates asic after updating pixel mask
        """
        if row < self.nrows:
            self.cfg[f'config_{chip}']['recconfig'][f'col{row}'][1] = self.cfg[f'config_{chip}']['recconfig'].get(f'col{row}', 0b001_11111_11111_11111_11111_11111_11111_11110)[1] | 0b000_00000_00000_00000_00000_00000_00000_00001

    def enable_inj_col(self, chip:int, col: int):
        """
        Enable injection in specified column

        Takes:
        col: int -  Column number
        inplace:bool - True - Updates asic after updating pixel mask
        """
        if col < self.ncols:
            self.cfg[f'config_{chip}']['recconfig'][f'col{col}'][1] = self.cfg[f'config_{chip}']['recconfig'].get(f'col{col}', 0b001_11111_11111_11111_11111_11111_11111_11110)[1] | 0b010_00000_00000_00000_00000_00000_00000_00000

    def enable_ampout_col(self, chip:int, col:int):
        """
        Enables analog output, Select Col for analog mux and disable other cols

        Takes:
        chip:int - chip to enable analog out in daisy chain
        col:int - column in row0 for analog output
        inplace:bool - True - Updates asic after updating pixel mask
        """

        #Disable all analog pixels
        for i in range(self.num_cols):
            self.cfg[f'config_{chip}']['recconfig'][f'col{col}'][1] = self.cfg[f'config_{chip}']['recconfig'][f'col{col}'][1] & 0b011_11111_11111_11111_11111_11111_11111_11111

        #Enable analog pixel in column <col>
        self.cfg[f'config_{chip}']['recconfig'][f'col{col}'][1] = self.cfg[f'config_{chip}']['recconfig'][f'col{col}'][1] | 0b100_00000_00000_00000_00000_00000_00000_00000

    def enable_pixel(self, chip:int, col: int, row: int):
        """
        Turns on comparator in specified pixel

        Takes:
        chip: int - chip in the daisy chain
        col: int - Column of pixel
        row: int - Row of pixel
        inplace:bool - True - Updates asic after updating pixel mask
        """
        assert row >= 0 and row < self.num_rows , f"Row outside of accepted range 0 <= row < {self.num_rows}"
        assert col >= 0 and col < self.num_cols , f"Row outside of accepted range 0 <= row < {self.num_cols}"
        if(row < self.num_rows and col < self.num_cols):
            self.cfg[f'config_{chip}']['recconfig'][f'col{col}'][1] = self.cfg[f'config_{chip}']['recconfig'].get(f'col{col}', 0b001_11111_11111_11111_11111_11111_11111_11110)[1] & ~(2 << row)

    def disable_pixel(self, chip:int, col: int, row: int):
        """
        Disable comparator in specified pixel

        Takes:
        chip: int - chip in the daisy chain
        col: int - Column of pixel
        row: int - Row of pixel
        inplace:bool - True - Updates asic after updating pixel mask
        """
        if(row < self.num_rows and col < self.num_cols):
            self.cfg[f'config_{chip}']['recconfig'][f'col{col}'][1] = self.cfg[f'config_{chip}']['recconfig'].get(f'col{col}', 0b001_11111_11111_11111_11111_11111_11111_11110)[1] | (2 << row)

    ### Following functions not used and don’t support multi-chip operations nor any recent yaml file format
    #def disable_inj_row(self, row: int):
    #    """Disable row injection switch
    #    :param row: Row number
    #    """
    #    if row < self.num_rows:
    #        self.cfg['recconfig'][f'col{row}'][1] = self.cfg['recconfig'].get(f'col{row}', 0b001_11111_11111_11111_11111_11111_11111_11110)[1] & 0b111_11111_11111_11111_11111_11111_11111_11110

    #def disable_inj_col(self, col: int):
    #    """Disable col injection switch
    #    :param col: Col number
    #    """
    #    if col < self.num_cols:
    #        self.cfg['recconfig'][f'col{col}'][1] = self.cfg['recconfig'].get(f'col{col}', 0b001_11111_11111_11111_11111_11111_11111_11110)[1] & 0b101_11111_11111_11111_11111_11111_11111_11111

    #def get_pixel(self, col: int, row: int):
    #    return self.is_pixel_enabled(col,row)

    #def is_pixel_enabled(self, col: int, row: int):
    #    """
    #    Checks if a given pixel is enabled

    #    Takes:
    #    col: int - column of pixel
    #    row: int - row of pixel
    #    """
    #    if row < self.num_rows:
    #        return self.cfg['recconfig'].get(f'col{col}')[1] & (1<<(row+1))
    #    return None




if __name__ == "__main__":
    C=AstroPixCfg()
    C.setCfgYaml("scripts/config/quadchip_allOff.yml")
    C.enable_inj_col(0, 34)
    C.enable_inj_row(0, 34)
    for i in range(4): print(C.getCfgBits(i))

