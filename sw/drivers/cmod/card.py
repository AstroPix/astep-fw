
from bitstring import BitArray

SIN_GECCO       = 0x02
LD_GECCO        = 0x04


class GeccoCard():
    """This Class helps with generating Shift Register Sequence to the right card with proper load signal"""

    def __init__(self,rfg,slot):
        self.rfg = rfg
        self.slot = slot


    async def sendBitsToCard(self,bits : BitArray,ckdiv :int = 16):
        """Sends the provided bits to the CARD SR. This method sends the sequence with proper load"""

        ## Append the Load bit to the array
        ## Gecco has 8 card slots and the last 8 bits for all Cards are the loads for the cards
        ## This sequence is send to Gecco ShiftREgister Chip, which has its own load
        ## The card's Load is an output of the SHift Register sequence, that's why it is appended to the list and is not a separated signal
        bits.append(BitArray(uint=(0b10000000 >> (self.slot - 1)), length=8))
        #bits.append(BitArray(uint=0b11111111, length=8))

        print(f"Gecco Card sending {len(bits)} bits: ",bits)

        ## Now Send this Sequence to RFG
        targetRegister = self.rfg.Registers["GECCO_SR_CTRL"]
        self.rfg.addWrite(register = targetRegister, value = 0, repeat = 1 ) ## Ensure 0
        for bit in bits:

            ## SIN
            registerValue = SIN_GECCO if bit == 1 else 0
            self.rfg.addWrite(register = targetRegister, value = registerValue, repeat = ckdiv )

            ## Ck 1 then 0
            self.rfg.addWrite(register = targetRegister,value = registerValue | 1 , repeat = ckdiv )
            self.rfg.addWrite(register = targetRegister,value = registerValue  , repeat = ckdiv )
            
        ## Now Load
        self.rfg.addWrite(register = targetRegister,value = LD_GECCO , repeat = ckdiv )
        self.rfg.addWrite(register = targetRegister,value = 0 , repeat = ckdiv )

        ## Now Reset Card Load with 8 bits 00
        for ldbit in range(8):

            ## Ck 1 then 0
            self.rfg.addWrite(register = targetRegister,value = 0 , repeat = ckdiv )
            self.rfg.addWrite(register = targetRegister,value = 1  , repeat = ckdiv )
        
        ## Now Load
        self.rfg.addWrite(register = targetRegister,value = 0 , repeat = ckdiv )
        self.rfg.addWrite(register = targetRegister,value = LD_GECCO , repeat = ckdiv )
        self.rfg.addWrite(register = targetRegister,value = 0 , repeat = ckdiv )

        ## Flush
        await self.rfg.flush()

        return bits