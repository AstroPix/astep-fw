
import logging
import atexit

import asyncio
from functools import partial

import spidev
import gpiod
from gpiod.line import Direction, Value

import rfg.core
from rfg.io.spi import SPIBytesDecoder

 
from asyncio       import Queue

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
def debug():
    logger.setLevel(logging.DEBUG)



## Main UART Class
class SPIDEVIO(rfg.core.RFGIO):
    """"""

    readout_timeout = 2

    def __init__(self, path: str,gpioPath: str,csGpioLine:int):
        super().__init__()
        self.devicePath = path
        self.gpioPath   = gpioPath 
        self.csGpioLine = csGpioLine

        ## Init Bytes decoder on receiving queue
        self.spiReadQueue = Queue()
        self.spiDecoder = SPIBytesDecoder(self.spiReadQueue)

    async def open(self):
        
        ## Load GPIO
        self.gpio = gpiod.request_lines(
            self.gpioPath,
            consumer="rfg-driver",
            config={
                self.csGpioLine: gpiod.LineSettings(
                    direction=Direction.OUTPUT, output_value=Value.ACTIVE
                )
            },
        )

        ## Load SPIDEV
        self.spiDev = spidev.SpiDev()
        self.spiDev.open_path(self.devicePath)
        self.spiDev.max_speed_hz = 5000000
        self.spiDev.lsbfirst = False
        #self.spiDev.mode = 0b01

        ## Perform Reset 
        self.gpio.set_value(self.csGpioLine, Value.ACTIVE)
        await asyncio.sleep(0.05)
        self.spiDev.xfer([0x00]*32)
        await asyncio.sleep(0.05)
        self.gpio.set_value(self.csGpioLine, Value.INACTIVE)
        await asyncio.sleep(0.05)
        self.spiDev.xfer([0x00]*16)
        
        ## Now SPI Open and Chip Select active
        atexit.register(exit_close,self)

    async def close(self):
        logger.info("Closing SPIDEV Port")
        self.gpio.set_value(self.csGpioLine, Value.ACTIVE)
        self.gpio.release()
        self.spiDev.close()

    def writeBytesIO(self,bytesToWrite: bytearray):
        # Add one more dummy byte to the write to make sure no byte get stuck in a receiver
        bytesToWrite.append(0x00)
        self.spiDev.writebytes2(bytesToWrite)
        return


    async def writeBytes(self,bytes : bytearray):
        try:
            result = await asyncio.get_running_loop().run_in_executor(None, partial(self.writeBytesIO,bytesToWrite=bytes))
            #print(f"Res uart: {len(result)}")
            return result
        except Exception as e:
            print("Error writebytes: "+str(e))




    def readBytesIO(self,count:int) -> bytes:
        # Read 5 mire bytes than necessary to cover the delay of the logic driving the bytes out
        remaining = count + 5
        bytes = bytearray()
        while remaining > 0 :
            logger.debug("Reading %d bytes from SPI",remaining)
            rbytes = self.spiDev.readbytes(remaining)
            #logger.debug("Read %d bytes from UART",len(rbytes))
            if len(rbytes)>0:
                bytes.extend(rbytes)
                remaining = remaining - len(rbytes)
            else:
                if rfg.io.isIOCancelled():
                    break

        return bytes

    async def readBytes(self,count : int ) -> bytes:

        ## Wait on the decoding queue
        self.spiDecoder.currentExpectedLength = count
        #decodeTask = cocotb.start_soon(self.spiDecoder.run_frame_decoding())

        #print("Reading")
        try:
            result = await asyncio.get_running_loop().run_in_executor(None, partial(self.readBytesIO,count=count))
            for b in result:
                await self.spiReadQueue.put(b)

            await self.spiDecoder.run_frame_decoding()

            readBytes = []
            for x in range(count):
                b = self.spiDecoder.decoded_bytes_queue.get(timeout=self.readout_timeout)
                readBytes.append(b)

            return readBytes

        except Exception as e:
            print("Error readbytes: "+str(e))
            raise e
         
        

        

        




def exit_close(io : SPIDEVIO):
    asyncio.run(io.close())
