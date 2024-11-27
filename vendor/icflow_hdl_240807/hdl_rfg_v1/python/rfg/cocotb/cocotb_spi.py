
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

logger = logging.getLogger(__name__)

def debug():
    logger.setLevel(logging.DEBUG)
    vip.spi.debug()
    rfg.io.spi.debug()

def info():
    logger.setLevel(logging.INFO)
    rfg.io.spi.info()
    vip.spi.info()

class SPIIO(rfg.core.RFGIO):
    """"""

    readout_timeout = 2

    def __init__(self,dut,msbFirst=True):
        
        ## Init VSPI
        self.spi = VSPIMaster(dut,dut.spi_clk,dut.spi_csn,dut.spi_mosi,dut.spi_miso,msbFirst)

        ## Init Bytes decoder on receiving queue
        self.spiDecoder = SPIBytesDecoder(self.spi.miso_queue)

    async def open(self):
        """This Method send 10 bytes while CS is 1, it is to ensure the FIFO are reset properly"""
        # Send a frame with CS 1 and not ready bits in to avoid sim error on "x"
        # Send another bunch of empty bytes after chip selected to finalize resetting the FIFOS
        logger.info(f"RFG SPI Master, MSB First = {self.spi.msbFirst}")
        await self.spi.send_frame([0x00]*10,use_chip_select = False,no_readout=True)
        self.spi.assert_chip_select()
        await Timer(1, units="us")
        await self.spi.send_frame([0x00]*10,use_chip_select = False,no_readout=True)
      
        #cocotb.start_soon(self.spiDecoder.start_protocol_decoding())

    async def close(self):
        self.spi.reset()
    
    async def writeBytes(self,b : bytearray):
        b.append(0x00)
        b.append(0x00)
        logger.debug("RFG Writing %d bytes",len(b))
        await self.spi.send_frame(b,use_chip_select = False)
        return len(b)

    async def readBytes(self,count : int ) -> bytes:
        logger.debug(f"RFG Readingc {count} bytes")
        ## Wait on the decoding queue
        self.spiDecoder.currentExpectedLength = count
        decodeTask = cocotb.start_soon(self.spiDecoder.run_frame_decoding())
        
        await self.spi.send_frame(map(lambda x: 0x00, range(count+10)),use_chip_select = False)
        readBytes = []
        for x in range(count):
            b = self.spiDecoder.decoded_bytes_queue.get(timeout = self.readout_timeout)
            readBytes.append(b)

        await Join(decodeTask)
        
        return readBytes 
