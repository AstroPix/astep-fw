
import logging
import math
import asyncio

from enum import Enum

logger = logging.getLogger(__name__)

def debug():
    logger.setLevel(logging.DEBUG)

class RFGRegister(Enum):
    pass

class RFGIO: 
    """
    This class provides a basic interface to send RFG bytes to a specific IO interface
    """

    def open(self):
        pass

    def close(self):
        pass

    async def writeBytes(self,bytes : bytearray):
        pass 

    async def readBytes(self,count : int ) -> bytes:
        pass

class RFGIOCommand:

    write : bool = False 
    addressIncrement = False 
    register : RFGRegister
    length : int = 1 
    values : list[int] = []
    targetQueue: str | None = None
    
    def __init__(self):
        self.write = False
        self.addressIncrement = False 
        self.length = 1 
        self.values = []
        self.targetQueue = None 
        

    def addValue(self,value:int):
        self.values.append(value)
        self.length = len(self.values)

class AbstractRFG:
    """
    This class holds the buffer of command + data to be send in a transaction
    A conversion to byte level protocol is done before sending to the IO class
    """

    currentRegister : RFGRegister | None  = None 

    commands : list[RFGIOCommand]  = []

    io : RFGIO | None = None

    readout_queues = dict()

    def __init__(self):
        self.io = None 
        self.commands = []
        self.currentRegister = None

    def withIODriver(self, io : RFGIO):
        self.io = io
        #io.open()
        return self

    async def flush(self):
        """This method flushes the command buffer to IO"""
        if self.io == None: 
            logger.error("No IO selected to flush RFG commands to")
        else:
            bytes = bytearray()
            logger.debug("Flushing %d commands", len(self.commands))

            ## Transform commands in bytes
            for cmd in self.commands:
                if cmd.write:
                    logger.debug("Adding Write with value of %d bytes,increment=%s", len(cmd.values),cmd.addressIncrement)
                    
                    ## Writes Might be longer than the 65536 limit (2 bytes length)
                    ## It is considered safe in this version to split into multiple writes
                    requiredWrites = int(math.ceil((len(cmd.values)/65535.0)))
                    remainingBytes = len(cmd.values)
                    for i in range(requiredWrites):
                        
                        offset = i * 65535
                        length = remainingBytes if remainingBytes <= 65535 else 65535
                        values = cmd.values[offset:offset+length]
                        remainingBytes -= length 

                        logger.debug(f"- Write part {i}/{requiredWrites},offset={offset},length={length},values array length={len(values)}")
                        

                        if cmd.addressIncrement:
                            bytes.append(0x05)
                        else:
                            bytes.append(0x01)
                        bytes.append(cmd.register.value)
                        #bytes.append(cmd.length.to_bytes(byteorder="little",length=2)[0])
                        #bytes.append(cmd.length.to_bytes(byteorder="little",length=2)[1])
                        bytes.append(length.to_bytes(byteorder="little",length=2)[0])
                        bytes.append(length.to_bytes(byteorder="little",length=2)[1])
                        
                        for v in values:
                            bV = v.to_bytes(byteorder="little",length=1)[0]
                            #logger.debug("-> byte %x", bV)
                            bytes.append(bV)
                else:
                    if cmd.addressIncrement:
                        bytes.append(0x06)
                    else:
                        bytes.append(0x02)
                    bytes.append(cmd.register.value)
                    bytes.append(cmd.length.to_bytes(byteorder="little",length=2)[0])
                    bytes.append(cmd.length.to_bytes(byteorder="little",length=2)[1])

            ## Send
            logger.debug("Flushing %d bytes to write", len(bytes))
            await self.io.writeBytes(bytes)

            ## Reset commands
            self.resetCommands()
            logger.debug("Reset commands run, now %d commands left", len(self.commands))
                

    def resetCommands(self): 
        self.commands = []


    def addWrite(self,register : RFGRegister,value : int,increment:bool = False,valueLength :int = 1,repeat : int = 1 ):
        logger.debug("Write Register %s (%x) Value %x, bytes count %d", register.name,register.value, value,valueLength)

        ## Create new Write command if register changes
        ## If repeated write to same register, write all values in one pass
        if self.currentRegister != register or len(self.commands) == 0: 
            self.currentRegister = register
            newWrite  = RFGIOCommand()
            newWrite.write              = True 
            newWrite.register           = register
            newWrite.addressIncrement    = increment
            self.commands.append(newWrite)
        
        ## Add values to values to be written
        for i in range(repeat):
            for b in value.to_bytes(byteorder="little",length=valueLength):
                cmd = self.commands[len(self.commands)-1]
                logger.debug("- adding byte %x to current %d bytes", b,len(cmd.values))
                cmd.addValue(b)
       

    def addRead(self,register:RFGRegister,count: int,increment:bool = False,targetQueue: str | None = None): 
        self.currentRegister = register
        newRead                     = RFGIOCommand()
        newRead.write               = False 
        newRead.register            = register
        newRead.length              = count
        newRead.addressIncrement    = increment
        newRead.targetQueue         = targetQueue
        self.commands.append(newRead)
        return newRead
        

    async def syncRead(self,register:RFGRegister,count: int,increment:bool = False,targetQueue: str | None = None) -> bytes : 
        logger.debug("Read Register %s (%x), length=%d,command count=%d", register.name,register.value,count,len(self.commands))
        
        ## Add Read command and flush it
        self.addRead(register,count,increment,targetQueue)
        await self.flush()

        ## Now Read
        resBytes =  await self.io.readBytes(count)
        #print("Read bytes: "+str(resBytes))

        ## Send bytes to queue if necessary
        if targetQueue is not None: 
            await self.writeBytesToQueue(targetQueue,resBytes)

        return resBytes

    async def syncReadAsInt(self,register:RFGRegister,count: int,increment:bool = False,targetQueue: str | None = None) -> int: 
        return  int.from_bytes(await self.syncRead(register,count,increment,targetQueue),"little")

    async def writeBytesToQueue(self,name:str, content):
        await (await self.getQueue(name)).put(content)

    async def getQueue(self,name:str):
        if name not in self.readout_queues:
            self.readout_queues[name] = asyncio.Queue()
        return self.readout_queues[name]
