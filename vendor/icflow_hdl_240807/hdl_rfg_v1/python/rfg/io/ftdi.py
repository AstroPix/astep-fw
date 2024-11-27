""""""
"""
Created on 30/09/23

@author: Nicolas Striebig KIT, Richard Leys KIT

"""

import logging 
import rfg.core 
import re
import atexit
import asyncio
from functools import partial


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
def debug():
    logger.setLevel(logging.DEBUG)

FLAG_LIST_SERIAL = 0 
FLAG_LIST_DESCRIPTOR = 2

try:
    import ftd2xx as ftd
except ModuleNotFoundError as e:
        logger.error(f"FTD2XX python module is not installed: {str(e)}")
        exit(-1)
except OSError as e:
        logger.error(f"FTD2XX Library is not installed: {str(e)}")
        exit(-1)

def isFTDIConnected():
    """Return true if an FTDI Device was detected"""
    try:
        device_serial = ftd.listDevices(0)
        if device_serial is None:
            return False 
        return True
    except ftd.DeviceError as e:
        return False

def listFTDIDevices(flag = FLAG_LIST_SERIAL):
    """Returns a list with info as requested, or an empty list if no device is connected"""
    try: 
        res =  ftd.listDevices(flag)
        return [] if res is None else list(enumerate(res)) 
    except ftd.DeviceError as e:
        return []    

def listFTDIDevicesMatching(searchPattern : str , flag = FLAG_LIST_SERIAL):
    devices = listFTDIDevices(flag)
    return  [indexAndDesc for indexAndDesc in devices if searchPattern in str(indexAndDesc[1])]
    


class FTDIIO(rfg.core.RFGIO):

    _deviceHandle : ftd.FTD2XX | None = None 

    def __init__(self,searchPattern : str , searchFlag:int = FLAG_LIST_SERIAL):
        self.searchPattern = searchPattern
        self.searchFlag = searchFlag
        self._deviceHandle = None 

    def open(self):
        matchingDevices = listFTDIDevicesMatching(self.searchPattern,self.searchFlag)
        if len(matchingDevices) == 0:
            raise OSError(f"Cannot Open FTDI RFG IO, no device matches pattern {self.searchPattern}")
        elif len(matchingDevices) > 1:
            raise OSError(f"Cannot Open FTDI RFG IO, more than one device matches pattern {self.searchPattern}")
        else:
            self.matchedDevice = matchingDevices[0] ## (index,descriptor)
            self._deviceHandle = ftd.open(self.matchedDevice[0])
            atexit.register(exit_close,self)
            self.__setup()
            logger.info(f"Opened FTDI Device {self.matchedDevice[1]}")

    def __setup(self) -> None:
        """Set FTDI USB connection settings for Synchronous mode"""

        self._deviceHandle.setTimeouts(1000, 1000)  # Timeout RX,TX
        self._deviceHandle.setBitMode(0xFF, 0x00)  # Reset
        self._deviceHandle.setBitMode(0xFF, 0x40)  # Set Synchronous 245 FIFO Mode
        self._deviceHandle.setLatencyTimer(2)
        self._deviceHandle.setUSBParameters(65536, 65536)  # Set Usb frame

    def close(self):
        if self._deviceHandle is not None:
            try: 
                self._deviceHandle.close()
                logger.info(f"Closed FTDI Device {self.matchedDevice[1]}")
            finally:
                self.matchedDevice = None 
                self._deviceHandle = None


    def readBytesIO(self,count:int) -> bytes:
        remaining = count 
        bytes = bytearray()
        while remaining > 0:
            logger.debug("Reading %d bytes from FTDI",remaining)
            rbytes = self._deviceHandle.read(remaining)
            #logger.info("Read %d bytes from FTDI",len(rbytes))
            if len(rbytes)>0:
                bytes.extend(rbytes)
                remaining = remaining - len(rbytes)
            else:
                if rfg.io.isIOCancelled():
                    break

        return bytes


    def writeBytesIO(self,bytesToWrite : bytearray):
        remaining = len(bytesToWrite)
        total = len(bytesToWrite)
        while remaining > 0:
            #logger.debug("Writing %d bytes to FTDI",len(bytes)) 
            outBytes = bytes(bytesToWrite[total-remaining:total:1])
            written = self._deviceHandle.write(outBytes)
            #logger.debug("Written %d bytes to FTDI",written)
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
            
    

    async def readBytes(self,count : int ) -> bytes:
        
        #print("Reading")
        try:
            result = await asyncio.get_running_loop().run_in_executor(None, partial(self.readBytesIO,count=count))
            #print(f"Res uart: {len(result)}")
            return result
        except Exception as e:
            print("Error readbytes: "+str(e))



def exit_close(io : FTDIIO):
    """This function is called through atexit to ensure Device is properly closed upon program exit"""
    io.close()
    
        
