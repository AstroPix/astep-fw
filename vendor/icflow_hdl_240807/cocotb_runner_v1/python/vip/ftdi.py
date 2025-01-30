import cocotb
from cocotb.triggers    import Timer , RisingEdge , FallingEdge , Join , Event
from cocotb.clock       import Clock
from cocotb.queue       import Queue

class FTDISyncFIFO:

    def __init__(self,dut,queueSize = 16 ):
        self.ftdi_clko  = dut.ftdi_clko
        self.ftdi_txe_n = dut.ftdi_txe_n
        self.ftdi_rxf_n = dut.ftdi_rxf_n

        self.ftdi_rd_n = dut.ftdi_rd_n
        self.ftdi_oe_n = dut.ftdi_oe_n
        self.ftdi_wr_n = dut.ftdi_wr_n

        self.ftdi_data = dut.ftdi_data

        self.ftdi_clko.value = 0
        self.ftdi_txe_n.value = 1
        self.ftdi_rxf_n.value = 1
        
        self.outputQueue = Queue(maxsize = queueSize)
        self.outputDoneEvent = Event()
        self.inputQueue  = Queue(maxsize = queueSize)

        self.clk_handle = None
        
        
        #cocotb.start_soon(self.outputProcess())
       # cocotb.start_soon(self.inputProcess())

    def start(self):
        cocotb.start_soon(self.outputProcess())
        cocotb.start_soon(self.inputProcess())

    def start_clk(self):
        if self.clk_handle is None:
            self.clk_handle = cocotb.start_soon(Clock(self.ftdi_clko,16.67,"ns").start())


    async def inputProcess(self):
        await RisingEdge(self.ftdi_clko)
        self.ftdi_txe_n.value = 0
        while True:
            await RisingEdge(self.ftdi_clko)
            
            ## Wait for data
            if self.ftdi_oe_n.value ==1 and self.ftdi_wr_n.value == 0:
                await self.inputQueue.put(int(self.ftdi_data.value))

            ## If Queue is full, stop
            #print(f"QS={self.inputQueue.qsize()},AS={self.inputQueue.maxsize}")
            while self.inputQueue.qsize() == self.inputQueue.maxsize:
                self.ftdi_txe_n.value = 1
                await RisingEdge(self.ftdi_clko)

            self.ftdi_txe_n.value = 0

    async def outputProcess(self):
        while True:
            bytes = await self.outputQueue.get()
            self.start_clk()

            ## Signal data ready
            self.ftdi_rxf_n.value = 0
            
            ## Wait for OEn to output data
            await FallingEdge(self.ftdi_oe_n)

            ## Output first byte
            self.ftdi_data.value = bytes[0]
            await RisingEdge(self.ftdi_clko)

            ## Output next bytes on posedge after first byte
            for i in range(len(bytes)-1):
                await RisingEdge(self.ftdi_clko)
                if self.ftdi_rd_n.value==0:
                    await Timer(1,"ns") #7.15
                    self.ftdi_data.value = bytes[i+1]
                else:
                    while self.ftdi_rd_n.value==1:
                        await RisingEdge(self.ftdi_clko)
                    await Timer(1,"ns") #7.15
                    self.ftdi_data.value = bytes[i+1]  

            ## Done
            await RisingEdge(self.ftdi_clko)
            self.ftdi_rxf_n.value = 1
            self.outputDoneEvent.set()


    async def writeBytes(self,bytes):
        await self.outputQueue.put(bytes)
        await self.outputDoneEvent.wait()

    async def getBytes(self,count = 1 ):
        res = []
        for i in range (count):
            res.append(await self.inputQueue.get())
        return res