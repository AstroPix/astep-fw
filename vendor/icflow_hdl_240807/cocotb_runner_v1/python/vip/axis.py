import cocotb
from cocotb.triggers    import Timer , RisingEdge , FallingEdge , Join
from cocotb.clock       import Clock
from cocotb.queue       import Queue
from cocotb.binary      import BinaryValue
from enum import Enum

import random

class AxisCycle:
    """This Class represents a Cycle of Axis bus. Used to generate data sequences with pauses"""

    def __init__(self,data,tdest = None , last : bool = False ):
        self.data = data
        self.last = last
        self.tdest = tdest

class VAXIS_Slave_If:

    def __init__( self, dut , offset = 0  ):
        self.dut = dut
        self.offset = offset

    ## Signals getters
    @property
    def _get_tvalid(self):
        if self.dut.m_axis_tvalid.value.n_bits > 1:
            return self.dut.m_axis_tvalid[self.offset]
        else:
            return self.dut.m_axis_tvalid
        
    @property
    def _get_tlast(self):
        if self.dut.m_axis_tlast.value.n_bits > 1:
            return self.dut.m_axis_tlast[self.offset]
        else:
            return self.dut.m_axis_tlast
        
    @property
    def _get_tready(self):
        if self.dut.m_axis_tready.value.n_bits > 1:
            return self.dut.m_axis_tready[self.offset]
        else:
            return self.dut.m_axis_tready
        
    def isValid(self):
        return True if self._get_tvalid.value.is_resolvable and self._get_tvalid.value == 1 else False

    def isReady(self):
        return True if self._get_tready.value.is_resolvable and self._get_tready.value == 1 else False

    def getData(self):
        """Builds an int by going over the single bits"""
        resVal = 0
        ##self.dut._log.info(f"Found Data on sink {self.dut.m_axis_tdata.value.binstr}")
        for i in range(8):
            resVal |= (self.dut.m_axis_tdata[self.offset*8+i].value << i)
        return resVal
    


class VAXIS_Slave(VAXIS_Slave_If) : 
    """Slave Axis connects to master interface"""
    search = "m_axis"


    def __init__( self, dut , clk , offset = 0 ,  queueSize = 4096 ) -> None:
        super().__init__(dut=dut,offset=offset)
        self.inputQueue = Queue(maxsize = queueSize )
        self.clk = clk

    def changeQueueSize(self,queueSize):
        self.inputQueue = Queue(maxsize = queueSize )

    def reset(self):
        self.notReady()

    def ready(self):
        self._get_tready.value = 1

    def notReady(self):
        self._get_tready.value = 0

    

    async def monitor_task(self):
        while True:
            await FallingEdge(self.clk)
            # self.dut.m_axis_tvalid[self.offset].value.is_resolvable and self.dut.m_axis_tvalid[self.offset].value == 1
            #if self.isValid() and self.isReady():
            #    self.dut._log.info(f"[{self.offset}] Got AXIS Slave byte ({self.inputQueue.qsize()+1})")
            #    await self.inputQueue.put(self.getData())
                 
            #print(f"QS={self.data_queue.qsize()},AS={self.data_queue.maxsize}")
            ## If queue is full, set not ready
            if self.inputQueue.qsize() == self.inputQueue.maxsize:
                while self.inputQueue.qsize() == self.inputQueue.maxsize :
                    self.notReady()
                    await RisingEdge(self.clk)
                self.ready()

    def start_monitor(self):
        
        self.monitor = AXIS_Slave_Monitor(self.dut,self.clk,offset=self.offset)
        self.monitor.start_monitor()

        self.monitor_task_handle =  cocotb.start_soon(self.monitor_task())
        return self.monitor_task_handle

    async def stop_monitor(self):
        await self.monitor_task_handle.kill()



class AXIS_Slave_Monitor(VAXIS_Slave_If):


    def __init__( self, dut , clk,offset=0):
        super().__init__(dut,offset=offset)
        self.outputQueue = Queue(maxsize = 4096 )
        self.clk = clk

    async def monitor_task(self):
        while True:
            await FallingEdge(self.clk)
            if self.isValid() and self.isReady():
                self.dut._log.info(f"[{self.offset}] AXIS Slave Monitor: received byte ({self.outputQueue.qsize()+1})")
                cycle = AxisCycle(data = self.getData())
                await self.outputQueue.put(cycle)

    def start_monitor(self):
        self.monitor_task_handle =  cocotb.start_soon(self.monitor_task())
        return self.monitor_task_handle

    async def stop_monitor(self):
        await self.monitor_task_handle.kill()

    
    async def getBytes(self,count = 1 ):
        res = []
        for i in range (count):
            cycle = await self.outputQueue.get()
            if cycle.data is not None:
                res.append(cycle.data)
        return res
    
    async def getAllBytes(self):
        return await self.getBytes(self.getBytesCount())

    def getBytesCount(self):
        return self.outputQueue.qsize()


class VAXIS_Master_If:

    def __init__( self, dut , offset = 0  ):
        self.dut = dut
        self.offset = offset

    ## Signals getters
    @property
    def _get_tvalid(self):
        if self.dut.s_axis_tvalid.value.n_bits > 1:
            return self.dut.s_axis_tvalid[self.offset]
        else:
            return self.dut.s_axis_tvalid
        
    @property
    def _get_tlast(self):
        if self.dut.s_axis_tlast.value.n_bits > 1:
            return self.dut.s_axis_tlast[self.offset]
        else:
            return self.dut.s_axis_tlast
        
    @property
    def _get_tready(self):
        if self.dut.s_axis_tready.value.n_bits > 1:
            return self.dut.s_axis_tready[self.offset]
        else:
            return self.dut.s_axis_tready
        
    def isValid(self):
        return True if self._get_tvalid.value.is_resolvable and self._get_tvalid.value == 1 else False

    def isReady(self):
        return True if self._get_tready.value.is_resolvable and self._get_tready.value == 1 else False

    def isLast(self):
        return True if self.hasLast() is True and self._get_tlast.value.is_resolvable and self._get_tlast.value == 1 else False

    def hasLast(self):
        try:
            #self.dut._id("s_axis_tlast",extended=True)
            self._get_tlast.value.is_resolvable
            return True
        except Exception as e :
            self.dut._log.info(f"Cannot find tlast: {e}")
            return False

    def hasTDest(self):
        try:
            #self.dut._id("s_axis_tdest",extended=True)
            self.dut.s_axis_tdest.value.is_resolvable
            return True
        except Exception as e: 
            return False

    def hasTID(self):
        try:
            self.dut.s_axis_tid.value.is_resolvable
            return True
        except Exception:
            return False
        
    def hasTUser(self):
        try:
            self.dut.s_axis_tuser.value.is_resolvable
            return True
        except Exception:
            return False 

    def getData(self):
        """Builds an int by going over the single bits"""
        resVal = 0
        ##self.dut._log.info(f"Found Data on sink {self.dut.m_axis_tdata.value.binstr}")
        for i in range(8):
            resVal |= (self.dut.s_axis_tdata[self.offset*8+i].value << i)
        return resVal
    

class VAXIS_Master(VAXIS_Master_If):
    """Master Axis connects to master interface"""
    search = "s_axis"

    data_queue : Queue | None = None

    def __init__( self, dut , clk , offset = 0 , queueSize = 16 ) -> None:
        """Offset is used in case the Interface is connected to a Switch"""
        super().__init__(dut,offset=offset)
        self.clk = clk 
        self.outputQueue = Queue(maxsize = queueSize)

    def reset(self):
        self.notValid()
        self.notLast()
        if self.hasLast() is False:
            self.dut._log.info(f"[{self.offset}] Master won't use tlast, slave doesn't have interface")

    def notValid(self):
        self._get_tvalid.value = 0

    def valid(self):
        self._get_tvalid.value = 1

    def notLast(self):
        if self.hasLast() is True:
            self._get_tlast.value = 0

    def last(self):
        if self.hasLast() is True:
            self._get_tlast.value = 1

    def setTid(self,target):
        for i in range(8):
            self.dut.s_axis_tid[self.offset*8+i].value  = (target >> i & 0x1)

    def setTdest(self,target):
        for i in range(8):
            self.dut.s_axis_tdest[self.offset*8+i].value  = (target >> i & 0x1)

    def setTuser(self,val):
        for i in range(8):
            self.dut.s_axis_tuser[self.offset*8+i].value  = (val >> i & 0x1)
    

    def setData(self,value):
        for i in range(8):
            self.dut.s_axis_tdata[self.offset*8+i].value  = (value >> i & 0x1)
       

    async def driver_task(self):
        while True:
            frame = await self.outputQueue.get()
            for i,axisCycle in enumerate(frame):
                
                # Data contained in cycle.data parameter
                byte = axisCycle.data

                #byte = await self.outputQueue.get()
                #if waitCycle == True:
                
                # Output byte on next clock cycle
                await RisingEdge(self.clk)
                
                ## If tdest, set tdest 
                if self.hasTDest() is True and axisCycle.tdest is not None: 
                    self.setTdest(axisCycle.tdest)

                ## If last, set tlast
                if self.hasLast() is True:
                    self.dut.s_axis_tlast[self.offset].value = 1 if i == len(frame)-1 else 0

                self.dut._log.info(f"[{self.offset}] AXIS Master writing byte {hex(byte)}")

                ## If the cycle has no data, don't set valid
                if axisCycle.data is None:
                    self.notValid()
                else:
                    self.valid()
                    self.setData(byte)
                    if axisCycle.tdest is not None and self.hasTDest() is True:
                        self.setTdest(axisCycle.tdest)

                # Wait until previous byte was taken if necessary
                # Do this on next edge to avoid sync issues with simulator
                await FallingEdge(self.clk)
                if  not self.isReady():
                    self.dut._log.info("AXIS Master waiting for ready")
                    while not self.isReady():
                        await FallingEdge(self.clk)


            ## If empty, stop
            if self.outputQueue.empty() == True: 
                await RisingEdge(self.clk)
                self.notValid()

            

    def start_driver(self):
        self.driver_task_handle =  cocotb.start_soon(self.driver_task())
        return self.driver_task_handle

    async def writeFrame(self,cycles):
        await self.outputQueue.put(cycles)
        #for b in bytes:
        #    await self.outputQueue.put(b)

    async def generateDataCycles(self,count, tdest = 0 , pauses=False):
        """Generate some Axys Data Cycles and add them to the queue - Returns the raw bytes generated"""
        res = []
        bytes = []
        for i in range(count):
            b = random.randint(1,128)
            res.append(AxisCycle(b,tdest=tdest))
            bytes.append(b)

        res[count-1].last = True
        await self.outputQueue.put(res)
        return bytes





class AXIS_Master_Monitor:
  

    def __init__( self, dut , clk, emptyCycles = False):
        self.dut = dut 
        self.outputQueue = Queue(maxsize = 4096 )
        self.clk = clk
        self.emptyCycles = emptyCycles

    def isValid(self):
        return True if self.dut.s_axis_tvalid.value.is_resolvable and self.dut.s_axis_tvalid.value == 1 and self.dut.s_axis_tready.value == 1  else False

    def isReadyNoData(self):
        return True if self.dut.s_axis_tvalid.value.is_resolvable and self.dut.s_axis_tvalid.value == 0 and self.dut.s_axis_tready.value == 1  else False

    def getData(self):
        """Builds an int by going over the single bits"""
        resVal = 0
        ##self.dut._log.info(f"Found Data on sink {self.dut.m_axis_tdata.value.binstr}")
        for i in range(8):
            resVal |= (self.dut.s_axis_tdata[i].value << i)
        return resVal

    async def monitor_task(self):
        while True:
            await FallingEdge(self.clk)
            # self.dut.m_axis_tvalid.value.is_resolvable and self.dut.m_axis_tvalid.value == 1
            if self.isValid():

                self.dut._log.debug(f"AXIS Master Monitor: received byte (queuesize={self.outputQueue.qsize()+1})")
                cycle = AxisCycle(data = self.getData())
                await self.outputQueue.put(cycle)

            elif self.isReadyNoData() and self.emptyCycles:

                self.dut._log.debug("AXIS Master Monitor: Empty data cycle")
                cycle = AxisCycle(data = None)
                await self.outputQueue.put(cycle)
                

    def start_monitor(self):
        self.monitor_task_handle =  cocotb.start_soon(self.monitor_task())
        return self.monitor_task_handle

    async def stop_monitor(self):
        await self.monitor_task_handle.kill()


    async def getBytes(self,count = 1 ):
        res = []
        for i in range (count):
            cycle = await self.outputQueue.get()
            if cycle.empty == False:
                res.append(cycle.data)
        return res
    
    async def getAllBytes(self):
        return await self.getBytes(self.getBytesCount())

    def getBytesCount(self):
        return self.outputQueue.qsize()