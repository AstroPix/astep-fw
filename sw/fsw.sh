#!/bin/bash

. ~/.venv/bin/activate
sudo chmod 660 /dev/spidev*
sudo chgrp gpio /dev/spidev*
. ../load.sh
python src/astep_fsw/read_fw_id.py
