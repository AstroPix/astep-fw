
import asyncio 

## Load Board
##############
import drivers.boards
import drivers.astropix.asic


async def callHK(flipped=True): # adding a setting that can change the byte ordering in the future if we ever fix/change this
    """
    Calls housekeeping from TI ADC128S102 ADC. Loops over each of the 8 input channels.
    Input is two bytes:
    First 2 bits: ignored
    Next 3 bits: Set Channel #
    Last 11 bits: ignored

    Shift register input style requires bytes to be read in left to right. May be fixed in future versions
    """
    ## Open UART Driver for CMOD
    driver = drivers.boards.getCMODUartDriver("COM4")
    driver.open() #does the driver need to be closed between reads?

    asyncio.run(driver.houseKeeping.selectADC())
    
    ## Loop over ADC Settings
    for chan in range(0,8):
        bits = format(chan,'08b')
        if flipped = True:
            byte1 = hex(int(format(7,'08b')[::-1],2)) #this is a hex string is this ok?i
        else:
            byte1 = hex(int(format(7,'08b'),2)) #this is a hex string is this ok?i

        asyncio.run(driver.houseKeeping.writeADCDACBytes([byte1,0x00]))
        adcBytesCount = asyncio.run(driver.houseKeeping.getADCBytesCount())
        adcBytes = asyncio.run(driver.houseKeeping.readADCBytes(adcBytesCount)) #still need to output this from task
        print(f"Got ADC bytes {adcBytes}")
        
        #sleep to give it time between read/writes, maybe not needed for asyncio?
        task = asyncio.create_task(asyncio.sleep(1)) #is this in seconds? us?
        await task

    driver.close()


async def setHV(flipped=True,setVoltage=0): # adding a setting that can change the byte ordering in the future if we ever fix/change this
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
        break

    ## Open UART Driver for CMOD
    driver = drivers.boards.getCMODUartDriver("COM4")
    driver.open() #does the driver need to be closed between reads? 

    #defaulting with Power-down with Hi-Z at the moment
    if setVoltage == 0 and flipped == True:
        asyncio.run(driver.houseKeeping.selectDAC())
        asyncio.run(driver.houseKeeping.writeADCDACBytes([0x0c,0x00]))
    elif setVoltage == 0 and flipped == False:
        asyncio.run(driver.houseKeeping.selectDAC())
        asyncio.run(driver.houseKeeping.writeADCDACBytes([0x30,0x00]))
    else:
        # Turn voltage input into bits
        bytess = format(int((setVoltage/3.3)*2**12-1),'016b')
        if flipped==True:
            byte1 = hex(int(bytess[0:8][::-1],2))
            byte2 = hex(int(bytess[8:16][::-1],2))i
        else:
            byte1 = hex(int(bytess[0:8][::-1],2))
            byte2 = hex(int(bytess[8:16][::-1],2))i
    
        asyncio.run(driver.houseKeeping.selectDAC())
        asyncio.run(driver.houseKeeping.writeADCDACBytes([byte1,byte2]))

    driver.close()
