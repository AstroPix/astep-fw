


class Astropix3LBModel():


    def __init__(self,driver,layer):
        self.driver = driver
        self.layer = layer


    async def enableLoopback(self,flush=True):
        """Enable Loopback by setting bit in layer config register"""
        regval =  await getattr(self.driver.rfg, f"read_layer_{self.layer}_cfg_ctrl")()
        regval |= (1<<5)
        await getattr(self.driver.rfg, f"write_layer_{self.layer}_cfg_ctrl")(regval,flush)

    async def disableLoopback(self,flush=True):
        """Disable Loopback by clearing bit in layer config register"""
        regval =  await getattr(self.driver.rfg, f"read_layer_{self.layer}_cfg_ctrl")()
        regval &= ~(1<<5)
        await getattr(self.driver.rfg, f"write_layer_{self.layer}_cfg_ctrl")(regval,flush)


    async def writeMISOBytes(self,b:bytes,flush : bool =True):
        await getattr(self.driver.rfg, f"write_layer_{self.layer}_loopback_miso_bytes")(b,flush)