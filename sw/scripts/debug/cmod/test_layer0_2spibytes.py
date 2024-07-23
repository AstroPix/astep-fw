
import asyncio, time
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
    await boardDriver.layersSelectSPI(flush=True)
    await boardDriver.writeBytesToLayer(0,[0x00,0x01],flush=True)
    await boardDriver.layersDeselectSPI(flush=True)
    print("Writing [0x00,0x01]")

    time.sleep(2)

    ## Read bytes
    nmbBytes = await boardDriver.readoutGetBufferSize()
    print(f"Got {nmbBytes} bytes")
    print(await boardDriver.readoutReadBytes(nmbBytes*2))


asyncio.run(main())
