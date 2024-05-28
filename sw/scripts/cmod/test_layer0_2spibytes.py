
import asyncio
import drivers.astep.serial
import drivers.boards

## Use first UART automatically
boardDriver = drivers.boards.getCMODUartDriver("COM4")#drivers.astep.serial.getFirstCOMPort())
boardDriver.open()

async def main():
    ## Write 2 Bytes to Layer 0
    await boardDriver.configureLayerSPIFrequency(2000000,flush= False)
    await boardDriver.setLayerConfig(0,reset=False,autoread = False, hold= True, flush=True)

    ## Write bytes
    await boardDriver.writeBytesToLayer(0,[0xAB,0xCD],flush=True)

asyncio.run(main())
