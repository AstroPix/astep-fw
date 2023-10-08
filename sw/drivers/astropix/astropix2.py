
from .asic import Asic 

class Astropix2(Asic):


    def __init__(self,rfg,row : int = 0,srRegisterName : str = "LAYERS_SR_OUT"):
        Asic.__init__(self,rfg,row,srRegisterName)
        self._chipversion = 2
        self._num_rows = 35
        self._num_cols = 35