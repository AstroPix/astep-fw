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
        self.cfg = yaml.safe_load(stream)
      except yaml.YAMLError as exc:
        raise exc#Useless right now, may want to do something smart with logging later
    self.nchips = self.cfg["astropix3"]["chain"]["length"]
    # V3 single chip: self.nchips = self.cfg["astropix3"]["telescope"]["nchips"]
    self.nrows = self.cfg["astropix3"]["geometry"]["rows"]
    self.ncols = self.cfg["astropix3"]["geometry"]["cols"]# Not used, but we could use them to check 

  def getCfgYaml(self):
    raise NotImplementedError()

  def setCfgBytes(self, bitarray):
    raise NotImplementedError()

  def getCfgBits(self, targetChip:int = None, msbfirst:bool = False) -> BitArray:#This is just a copy from the function in drivers/astropix/asic.py
    """
    Generate asic bitvector from digital, bias and dacconfig
    :param msbfirst: Send vector MSB first
    :param targetChip: Returns only the bits for the selected Astropix - if set to -1, returns for all the Astropix - no effect if the configuration is not multichip
    """
    bitvector = BitArray()
    configSource = self.cfg["astropix3"][f'config_{targetChip}'] if (self.nchips>1) else self.cfg["astropix3"]["config"]#Latter used for V3 single chip
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

  ## Add functions here to turn pixels, injection, analog on/off, set voltages/thresholds.
  ## Said functions are in astep-fw/sw/drivers/astropix/asic.py


if __name__ == "__main__":
  C=AstroPixCfg()
  C.setCfgYaml("scripts/config/quadchip_allOn.yml")
  for i in range(4): print(C.getCfgBits(i))

