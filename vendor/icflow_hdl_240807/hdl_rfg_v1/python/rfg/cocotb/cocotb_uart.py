
import logging
import rfg.core
from cocotbext.uart import UartSource, UartSink 

logger = logging.getLogger(__name__)

def debug():
    logger.setLevel(logging.DEBUG)


class UARTIO(rfg.core.RFGIO):
    """"""

    source : UartSource | None = None
    sink   : UartSink   | None = None  

    port : str | None = None 
    baud : int = 921600
    timeout : int = 3

    def __init__(self, tx,rx, baud = 921600):
        self.tx = tx
        self.rx = rx
        self.baud = baud

    async def open(self):
        #dir(dut)
        #dir(self.dut)["uart_tx_in"]
        self.uart_source = UartSource(self.tx, baud= self.baud, bits=8)
        self.uart_sink   = UartSink(self.rx,  baud= self.baud, bits=8)


    async def close(self):
        self.uart_source = None
        self.uart_sink =   None
        pass

    async def writeBytes(self,bytes : bytearray):
        await self.uart_source.write(bytes)
        await self.uart_source.wait()
        pass

    async def readBytes(self,count : int ) -> bytes:
        readBytes = []
        for x in range(count):
            await self.uart_sink.wait(timeout = 1 , timeout_unit = "ms")
            readBytes.extend(await self.uart_sink.read(1))
        return readBytes

