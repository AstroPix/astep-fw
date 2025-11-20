import asyncio
import os
import os.path
import sys

# sys.path.append(os.path.dirname(__file__)+"/.generated/")
import cocotb
import vip.astropix3
import vip.cctb
import vip.spi
from cocotb.clock import Clock
from cocotb.triggers import Combine, FallingEdge, Join, RisingEdge, Timer

vip.spi.info()

## Import simulation target driver
import astep24_3l_sim
import rfg.core

from bitstring import BitArray
from bitstring import Array

@cocotb.test(timeout_time=3, timeout_unit="ms")
async def test_layers_config_sr_bitgen(dut):
    """Tests that the Board Driver generates the config bits"""

    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)
    

    ## Create ASIC config
    driver.setupASICS(
        version=3, lanes=1, chipsPerLane=2, configFile="./files/config_v3_mc.yml"
    )

    ## Get Config for Target Chip 
    configs = driver.getAsic(lane=0).getConfigBits(msbfirst=False,targetChip=0)
    assert 1 == len(configs)
    assert 4 == len(configs[0])
    assert [1,1,0,1] == configs[0]
    await Timer(150, units="us")
    
    ## Get Config for Target Chip 
    configs = driver.getAsic(lane=0).getConfigBits(msbfirst=False,targetChip=1)
    assert 1 == len(configs)
    assert 4 == len(configs[0])
    assert [0,0,0,1] == configs[0]
    await Timer(150, units="us")
    
    
    ## Get Config for all Chips
    configs = driver.getAsic(lane=0).getConfigBits(msbfirst=False,targetChip=-1)
    assert 2 == len(configs)
    assert 4 == len(configs[0])
    assert 4 == len(configs[1])
    assert [0,0,0,1] == configs[0]
    assert [1,1,0,1] == configs[1]
    await Timer(150, units="us")

    await Timer(150, units="us")
    
    
@cocotb.test(timeout_time=3, timeout_unit="ms")
async def test_layers_config_sr(dut):
    """Writs SR Config to each row/layer, check for Load signal for each"""

    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Create ASIC config
    driver.setupASICS(
        version=3, lanes=3, chipsPerLane=1, configFile="./files/config_v3_mc.yml"
    )

    await driver.resetLayersFull(wait=False)
    await driver.resetLayersFull(wait=False)

    ## Send config
    async def wait_for_load(row):
        await FallingEdge(dut._id(f"layers_sr_out_ld{lane}", extended=False))

    for lane in range(3):
        # asic = driver.getAsic(lane=lane)
        fallingEdgeTask = cocotb.start_soon(wait_for_load(lane))
        await driver.writeSRAsicConfig(lane=lane, ckdiv=1, limit=4)
        # await asic.writeConfigSR(ckdiv=1, limit=4)
        ## After last bit to load = 4 written, we can wait for a falling edge of load
        await Join(fallingEdgeTask)

    await Timer(150, units="us")


@cocotb.test(timeout_time=3, timeout_unit="ms")
async def test_layer_0_config_sr_multichip(dut):
    """Configures using SR on layer 0 with a multichip chain"""

    # rfg.core.debug()
    # 
    

    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Create ASIC config
    driver.setupASICS(
        version=3, lanes=1, chipsPerLane=2, configFile="./files/config_v3_mc.yml"
    )

    ## Write Config and wait for edge
    async def wait_for_load():
        await FallingEdge(dut._id(f"layers_sr_out_ld0", extended=False))

    fallingEdgeTask = cocotb.start_soon(wait_for_load())
    await driver.writeSRAsicConfig(lane=0, ckdiv=1, limit=4)
    await Join(fallingEdgeTask)
    # await asyncio.gather(asic.writeConfigSR(ckdiv = 2))
    # ,FallingEdge(dut._id(f"layers_sr_out_ld0", extended=False))
    # await asic.writeConfigSR(ckdiv = 2)
    # await Combine(
    #    asic.writeConfigSR(ckdiv = 2),
    #    ## After last bit to load = 4 written, we can wait for a falling edge of load
    #    FallingEdge(dut._id(f"layers_sr_out_ld0", extended=False))
    # )

    await Timer(150, units="us")




@cocotb.test(timeout_time=3, timeout_unit="ms")
async def test_layer_0_config_sr_readout(dut):
    """Reads back a chip config from SR using CRC Module"""

    ## Create an ASIC Model to send readout bits 
    astropix = vip.astropix3.Astropix3Model(dut, "layer_0", 0)

    ## Clock/Reset
    await vip.cctb.common_clock_reset(dut)
    await Timer(10, units="us")
    driver = await astep24_3l_sim.getDriver(dut)

    ## Create ASIC config
    driver.setupASICS(
        version=3, lanes=1, chipsPerLane=1, configFile="./files/config_v3_readback.yml"
    )
    
    cocotb.start_soon(astropix.runSRInterface(srLength = 35))

    ## Write Config and wait for Load edge
    async def wait_for_load():
        await FallingEdge(dut._id(f"layers_sr_out_ld0", extended=False))

    fallingEdgeTask = cocotb.start_soon(wait_for_load())
    await driver.writeSRAsicConfig(lane=0, ckdiv=1 )
    await Join(fallingEdgeTask)
    dut._log.info("Chip Configured, now start readback")
    
    ## Readback from driver:
    ## Set RB to 1 then toggle CK1 and CK2
    ## Set RB back to 0, then write the config with SIN to 0 and no load, with bits padded to full bytes
    crc = await driver.writeSRReadback(lane = 0 )
    
    dut._log.info(f"CRC={crc}")
    #dut._log.info(f"Bits Bytes len={bytesInFifo}")
    
    ## Get the bits
    (readBits,expectedBits) = await driver.readSRReadbackBits(lane=0)
    dut._log.info(f"Readback={readBits.bin},Expected={expectedBits.bin}")
    
    assert readBits.bin == expectedBits.bin, "Returned bits and expected bits should be the same"
    

    await Timer(150, units="us")