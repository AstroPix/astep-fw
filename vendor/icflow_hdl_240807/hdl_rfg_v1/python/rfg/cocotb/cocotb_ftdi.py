
import logging

from queue          import Queue

import vip.spi
from   vip.spi      import VSPIMaster

import rfg.core
import rfg.io.spi
from   rfg.io.spi   import SPIBytesDecoder

import cocotb
from cocotb.triggers import Join
from cocotb.triggers import Timer,RisingEdge

from vip.ftdi import FTDISyncFIFO


import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

logger = logging.getLogger(__name__)

def debug():
    logger.setLevel(logging.DEBUG)
    vip.spi.debug()
    rfg.io.spi.debug()

def info():
    logger.setLevel(logging.INFO)
    rfg.io.spi.info()
    vip.spi.info()

class FTDIFIFOIO(rfg.core.RFGIO):
    """"""

    readout_timeout = 2

    def __init__(self,dut):

        ## Init VSPI
        self.ftdi = FTDISyncFIFO(dut)


    async def open(self):
        self.ftdi.start()

        #cocotb.start_soon(self.spiDecoder.start_protocol_decoding())

    async def close(self):
        self.ftdi.stop()

    async def writeBytes(self,b : bytearray):
        await self.ftdi.outputQueue.put(b)
        return len(b)

    async def readBytes(self,count : int ) -> bytes:
        read = []
        for i in range(count):
            b = await self.ftdi.inputQueue.get()
            #print(f"Got byte {i} from ftdi input")
            read.append(b)

        return bytes(read)
