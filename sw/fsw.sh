#!/bin/bash

. .venv/bin/activate
#sudo chmod 660 /dev/spidev*
#sudo chgrp gpio /dev/spidev*
. ../load.sh
python scripts/debug/beagle/read_fw_id.py
