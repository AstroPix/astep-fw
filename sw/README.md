# Chip Operation with astep.py, benchtest.py, and chipOp_flight.py

Software in this 'sw' repository enables communication with hardware, chip configuration, data collection, and includes the first step of the data pipeline. Further details for interfacing with hardware/firmware and outlines for useful software packages and strategies can be found in the [astep-fw documentation](https://astropix.github.io/astep-fw/sw/getting_started/).


## Folder Structure

- **drivers** - folder for classes needed for chip operation
    - **astep**
        - housekeeping.py - support methods for integration of housekeeping through DAC/ACD/sense of FPGA
        - serial.py - support for testing serial connection of FPGA
    - **astropix**
        - asic.py - support for definition/routing of commands/settings to chip (including pixel enable/disable, config file load, generation of config stream for writing to chip, etc)
    - **boards**
        - _init__.py - initialize board_driver class, entry point to drive Firmware functionalities
        - board_driver.py - support for interacting with FPGA/FW functionalities (including open/close connection to hardware, set/send clocks, select/deselect SPI, set/get register values, get readout buffer, etc)
    - **cmod** 
        - _init__.py - initialize CMOD hardware (including set FPGA frequency, etc)
    - **gecco** 
        - _init__.py - initialize NEXYS hardware (including set FPGA frequency, get/set objects for GECCO aux boards, etc)
        - card.py - support for generating Shift Register Sequence to the right card with proper load signal
        - injectionboard.py - support for config of GECCO aux injection board (including generate/write config bits, get/set register values, start/stop injection, etc)
        - voltageboard.py - support for config of GECCO aux voltage board (including generate/write config bits, etc)
- **scripts** - executable code for configuring and running AstroPix quad chips
    - benchtest.py - robust script for bench testing / debugging. Many options for different styles of running and data collection
    - chipOp_flight.py - bare-bones version of benchtest.py intended for ultimate use on flight. Few test features and only core operation.
    - **config** - folder of all configuration files, stored as *.yml. Apply the appropriate file for each run.
    - **debug** - test script for debugging the setup of different FPGA environments
        - **cmod** - hardcoded scripts for test running with CMOD FPGA
        - **gecco** - hardcoded scripts for test running with GECCO/NEXYS FPGA
- **ui_control_v1** - source and executable code for GECCO GUI
    - WIP
- **astep.py** - wrapper for backend in 'drivers', intended to streamline user experience
- **requirements.txt** - Python requirements

## Run Scripts

1. Source environment: `load.bat` or `./load.sh`
2. Move to software folder: `cd sw/`
3. Confirm that apropriate settings/paths are set in your run script of choice (`benchtest.py` or `chipOp_flight.py`)
4. Run script _from the software folder_ like `python scripts/benchtest.py` or `python scripts/chipOp_flight.py`
    - If selected, output data will be stored in `sw/data/`
    - List all available runtime options like `python scripts/benchtest.py -h`
