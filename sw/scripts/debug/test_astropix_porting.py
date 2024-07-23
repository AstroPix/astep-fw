import asyncio
from astropix import astropixRun


astro = astropixRun(chipversion=2, inject=None)

async def main():
    await astro.open_fpga()

    await astro.asic_init(yaml="config_c0_r0", analog_col = 0)

    await astro.init_voltages(vthreshold=500) ## th in mv

    await astro.init_injection(inj_voltage=0.8, onchip=False)

    print(f"Header: {astro.get_log_header()}")

asyncio.run(main())