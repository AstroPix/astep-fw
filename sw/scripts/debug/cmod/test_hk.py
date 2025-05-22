
import asyncio 

## Load Board
##############
import drivers.boards
import drivers.astropix.asic

import time
import binascii

async def callHK(lsbFirst=True): # adding a setting that can change the byte ordering in the future if we ever fix/change this
    """
    Calls housekeeping from TI ADC128S102 ADC. Loops over each of the 8 input channels.
    Input is two bytes:
    First 2 bits: ignored
    Next 3 bits: Set Channel #
    Last 11 bits: ignored

    Shift register input style requires bytes to be read in left to right. May be fixed in future versions
    """
    ## Open UART Driver for CMOD
    driver = drivers.boards.getCMODUartDriver("COM6")
    await driver.open() #does the driver need to be closed between reads?
    await driver.houseKeeping.selectADC()
    
    ## Loop over ADC Settings
    for chan in range(0,8):
        bits = format(chan,'08b') #fix the formatting 
        if lsbFirst == True:
            byte1 = int(bits[::-1],2) #this is a hex string is this ok?
        else:
            byte1 = int(bits,2) #this is a hex string is this ok?

        print(f"{hex(byte1)}")
        await driver.houseKeeping.writeADCDACBytes([byte1,0x00])
        adcBytesCount = await driver.houseKeeping.getADCBytesCount()
        adcBytes = await driver.houseKeeping.readADCBytes(adcBytesCount) #still need to output this from task
        print(f"Got ADC bytes {binascii.hexlify(adcBytes)}")
        
        #sleep to give it time between read/writes, maybe not needed for asyncio?
        task = asyncio.create_task(asyncio.sleep(1)) #is this in seconds? us?
        await task

    await driver.close()


async def setHV(lsbFirst=True,setVoltage=0): # adding a setting that can change the byte ordering in the future if we ever fix/change this
    """
    Sends set voltage to TI DAC121S101 for setting HV bias
    Input is two bytes
    First 2 bits: ignored
    Next two bits: set ops mode:
        | Bit 13 | Bit 14 |
             0        0  - Normal Ops
             0        1  - Power-Down with 1kOhm to GND
             1        0  - Power-Down with 100kOhm to GND
             1        1  - Power-Down with Hi-Z
    last 12 bits contain the voltage setting, full scale from 0V to 3.3V
    Input is in Volts

    """
    if setVoltage > 3.3 or setVoltage < 0:
        print(f"Set Voltage Input not accepted!")
        return

    ## Open UART Driver for CMOD
    driver = drivers.boards.getCMODUartDriver("COM6")
    await driver.open() #does the driver need to be closed between reads? 
    await driver.houseKeeping.selectDAC()

    #defaulting with Power-down with Hi-Z at the moment
    if setVoltage == 0 and lsbFirst == True:
        await driver.houseKeeping.writeADCDACBytes([0x0c,0x00])
    elif setVoltage == 0 and lsbFirst == False:
        await driver.houseKeeping.writeADCDACBytes([0x30,0x00])
    else:
        # Turn voltage input into bits
        bytess = format(int((setVoltage/3.3)*2**12-1),'016b')
        if lsbFirst==True:
            byte1 = int(bytess[0:8][::-1],2) #hex()
            byte2 = int(bytess[8:16][::-1],2)
        else:
            byte1 = int(bytess[0:8],2)
            byte2 = int(bytess[8:16],2)
    
        await driver.houseKeeping.selectDAC()
        await driver.houseKeeping.writeADCDACBytes([byte1,byte2])

    await driver.close()


async def main(ramp):

    t0 = time.time()
    t_end = t0+30

    #while time.time() < t_end:
    #    await callHK()

    if ramp == "up":
        for v in [.5, 1., 1.5, 1.9, 2.05]:
            await setHV(setVoltage=v)
            time.sleep(1)
    elif ramp == "down":
        for v in [1.9, 1.5, 1., .5, 0.]:
            await setHV(setVoltage=v)
            time.sleep(1)
    else:
        await setHV(setVoltage=0.   ) #1.825V = 150V pre-1Mohm Res, #2.05V = 150V post-1MOhm Res



if __name__ == "__main__":
    asyncio.run(main("down"))
