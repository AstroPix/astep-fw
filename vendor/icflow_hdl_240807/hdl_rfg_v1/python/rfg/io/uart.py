
import logging
import atexit

import asyncio
from functools import partial

import serial
from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo

import rfg.core 

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
def debug():
    logger.setLevel(logging.DEBUG)


## Main UART Class
class UARTIO(rfg.core.RFGIO):
    """"""

    serialPort : serial.Serial | None = None 

    port : str | None = None 
    baud : int = 921600
    timeout : int = 3

    def listPorts(self) -> list[ListPortInfo] : 
        list_ports.comports()

    async def open(self):
        if self.port == None: 
            logger.error("No COM port path selected")
        else: 
            self.serialPort = serial.Serial(port = self.port,baudrate=self.baud,timeout=self.timeout)
            atexit.register(exit_close,self)
            logger.info(f"Opened Serial port {self.port} with baud {self.baud} bps")
            #self.serialPort.open()

    async def close(self):
        logger.info("Closing Serial Port")
        if self.serialPort != None:
            if self.serialPort.is_open:
                self.serialPort.close()
            self.serialPort = None 
        pass

    def writeBytesIO(self,bytesToWrite: bytearray):
        remaining = len(bytesToWrite)
        total = len(bytesToWrite)
        while remaining > 0:
            logger.debug("Writing %d bytes to UART",len(bytesToWrite))
            written = self.serialPort.write(bytesToWrite[total-remaining:total:1])
            logger.debug("Written %d bytes to UART",written)
            if written>0:
                remaining = remaining - written
            else:
                if rfg.io.isIOCancelled():
                    break
        

    async def writeBytes(self,bytes : bytearray):
        try:
            result = await asyncio.get_running_loop().run_in_executor(None, partial(self.writeBytesIO,bytesToWrite=bytes))
            #print(f"Res uart: {len(result)}")
            return result
        except Exception as e:
            print("Error writebytes: "+str(e))

       
        

    def readBytesIO(self,count:int) -> bytes:
        remaining = count 
        bytes = bytearray()
        while remaining > 0 :
            logger.debug("Reading %d bytes from UART",remaining)
            rbytes = self.serialPort.read(remaining)
            #logger.debug("Read %d bytes from UART",len(rbytes))
            if len(rbytes)>0:
                bytes.extend(rbytes)
                remaining = remaining - len(rbytes)
            else:
                if rfg.io.isIOCancelled():
                    break
            
        return bytes

    async def readBytes(self,count : int ) -> bytes:
        
        #print("Reading")
        try:
            result = await asyncio.get_running_loop().run_in_executor(None, partial(self.readBytesIO,count=count))
            #print(f"Res uart: {len(result)}")
            return result
        except Exception as e:
            print("Error readbytes: "+str(e))
       
        
        

def exit_close(io : UARTIO):
    io.close()