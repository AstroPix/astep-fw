

import logging
import queue
from queue import Queue
import asyncio

logger = logging.getLogger(__name__)

def debug():
    logger.setLevel(logging.DEBUG)




## This decoder is used to transform low level bytes into payload bytes following RFG spi framing
class SPIBytesDecoder():
    """This class decodes low level bytes into actual payload bytes"""

    ## Reference to Queue where low level bytes are written
    receive_bytes_queue : Queue | None = None 

    ## Queue to put decoded bytes
    decoded_bytes_queue : Queue | None = None 

    currentExpectedLength = 1

    def __init__(self,receive_queue : Queue):
        self.receive_bytes_queue = receive_queue
        self.decoded_bytes_queue = Queue()


    async def start_frame_decoding(self):
        """Start this task to continuously decode bytes"""
        frame_start = False
        currentLength = 0
        currentQueue = 0
        while True:
            #await self.frame_decoding_semaphore.acquire()
            byte = await self.receive_bytes_queue.get()
            if not frame_start and byte != 0xBC:
                logger.info("Found Start of Frame for readout queue %d",byte)
                currentQueue = byte
                frame_start = True
            elif frame_start and currentLength < self.currentExpectedLength:
                currentLength += 1
                logger.info("Read payload byte %x",byte)
                self.decoded_bytes_queue.put(byte)
                if currentLength is self.currentExpectedLength:
                    logger.info("Reached requested %d bytes",self.currentExpectedLength)
                    frame_start = False 
                    currentLength = 0
            else:
                logger.info("Got IDLE Byte %d",byte)
                pass
                #logger.info("SAFE Reached requested %d bytes",self.currentExpectedLength)
                #frame_start = False 
                #currentLength = 0
    
    async def run_frame_decoding(self):
        """Start this task to continuously decode bytes"""
        frame_start = False
        finished = False
        currentLength = 0
        currentQueue = 0
        while not finished:
            byte = await self.receive_bytes_queue.get()
            if not frame_start and byte != 0xBC:
                logger.info(f"Found Start of Frame for readout queue {hex(byte)}, expect {self.currentExpectedLength} bytes")
                currentQueue = byte
                frame_start = True
            elif frame_start and currentLength < self.currentExpectedLength:
                currentLength += 1
                logger.info(f"Read payload byte {hex(byte)},{currentLength}/{self.currentExpectedLength}")
                self.decoded_bytes_queue.put(byte)
                if currentLength == self.currentExpectedLength:
                    logger.info("Reached requested %d bytes",self.currentExpectedLength)
                    frame_start = False 
                    currentLength = 0
                    finished = True
            else:
                logger.info("Got IDLE Byte %x",byte)
                pass
            #logger.info("SAFE Reached requested %d bytes",self.currentExpectedLength)
            #frame_start = False 
            #currentLength = 0

    def expectReadLength(self,newLength : int) -> None:
        self.currentExpectedLength = newLength

    def getDecodedBytesCount(self):
        return self.decoded_bytes_queue.qsize()

    def drainDecodedBytes(self):
        result = []
        stop = False 
        while True: 
            try:
                result.append(self.decoded_bytes_queue.get(False))
            except queue.Empty:
                break
        return result
         