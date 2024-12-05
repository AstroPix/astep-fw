# ASTEP FW+SW package

This repository contains the firware and support software sources for the ASTEP Firmware.

This firmware targets at the moment the following hardware:

- Gecco Digilent Nexys Video for Astropix v2/v3/v4(upcomin), with various I/O configuration required for the carrier boards:
    - Single layer readout for Single Chips Carrier
    - Single layer readout for Telescope (1 Layer with 4 chips in daisychain,imported from astropix-fw, not tested)
- Digilent CMOD A35T for 3 Layers Flight configuration:
    - 3 Layers of Astropix with each 1 QuadChip (4 Chips in DaisyChain)
    - CMOD connected to FPGA board interposer
    - I/O Configuration adapted in consequence (no lvds outputs, no clock outputs before software enable etc...)

## Main Documentation

The complete documentation for this repository is written using mkdocs from the docs/ folder, and is published on Github Pages here: [https://astropix.github.io/astep-fw/](https://astropix.github.io/astep-fw/)

If you want to work on the documentation, just build the static website: 

```bash
source load.sh # Sets up the environment for all tools to be present
sudo apt install tcl tcllib # Install a few packages for tooling
make docs
```
To start a reloading server to live edit:

```bash
source load.sh # Sets up the environment for all tools to be present
make docs.serve
```

## Setup 

For environment setup regarding drivers installation, packages etc. Refer to the main documentation:

- For Hardware: [Hardware Setup Page](https://astropix.github.io/astep-fw/setup/hardware)
- For Tools alltogether: [Tooling Setup Page](https://astropix.github.io/astep-fw/setup/tooling)

## Quick Reference 

Here are some typical commands to work with this repository for quick reference: 

### Load the Environment

Always source the load.sh script when opening the terminal, this sets up a few environment variables to ensure all the scripts work fine and the software drivers are accessible from any work folder 

```bash
source load.sh
```
For Windows users, you can use the **load.bat** and **load.ps1** for command prompt or power shell:

Command Prompt: 

```batch
xxxx> load.bat
```

Power Shell:

```powershell
PS xxxx> load.ps1
```


### Load your tools

If a script called **load.local.sh** is present at the root of the repository, it is loaded by the load.sh script 
This script is ignored for GIT, you can put scripts that will load your tools, like Vivado for example:

Linux:

```bash
cd <Vivado install-dir>
source settings64.sh
```

For windows there is no main load script for the moment, but to load Vivado, your can do:

```bash
cd <Vivado install-dir>
settings64.bat
```

### Build Firmware fully

The build method for the Firmware is imported from Nicolas Striebig work on astropix-fw repository with some minor changes to add version numbers to the build firmware and support building for multiple fpga targets:


If you want to change the parameters for the builds, edit the entry scripts for the targets: 
- gecco-astropix2.tcl
- gecco-astropix3.tcl
- cmodr2-astep.tcl 

You can build the firmware using the Makefile targets:

```bash
# Sourcing the load script is not essential for FW building, just make sure vivado is accessible from your terminal

# Got to multiboard target folder:
cd fw/astep24-3l/target-multiboard

# To Build a firmware in the terminal line fully, use the ***.build targets:

make gecco-astropix2.build # Gecco Astropix 2
make gecco-astropix3.build # Gecco Astropix 3
make cmodr2-astep.build # CMOD Astropix 3

# Outputs are located in the vivado-run/bitstreams folder
```

Or to Run the script manually:

```bash
# Create a vivado-run folder:
mkdir vivado-run 
# Start vivado from the sub folder
cd vivado-run
vivado -mode batch -source ../gecco-astropix2.tcl
vivado -mode batch -source ../gecco-astropix3.tcl
vivado -mode batch -source ../cmodr2-astep.tcl
```

or by running vivado directly:


```bash
# Sourcing the load script is not essential for FW building, just make sure vivado is accessible from your terminal

# Got to multiboard target folder:
cd fw/astep24-3l/target-multiboard
# To Run the script manually:
# Create a vivado-run folder:
mkdir vivado-run 
# Start vivado from the sub folder
cd vivado-run
vivado -mode batch -source ../gecco-astropix2.tcl
vivado -mode batch -source ../gecco-astropix3.tcl
vivado -mode batch -source ../cmodr2-astep.tcl

# Outputs are located in the vivado-run/bitstreams folder
```

### Build Firmware through Vivado UI

The TCL scripts were adapted to allow not building the firmware inline but only create the project so that users can run the steps through the GUI (convenient for development)

If you start the TCL script with an Environment variable called OPEN=1 set, it will open the GUI.

You can also use the make targets ***.open for this: 

```bash
# Sourcing the load script is not essential for FW building, just make sure vivado is accessible from your terminal

# Got to multiboard target folder:
cd fw/astep24-3l/target-multiboard

## Using makefile 
make gecco-astropix2.open 

# To Run the script manually:
export OPEN=1
mkdir vivado-run 
cd vivado-run
vivado -mode batch -source ../gecco-astropix2.tcl

# Now use vivado as usual
```
