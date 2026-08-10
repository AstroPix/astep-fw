#!/bin/bash

. .venv/bin/activate
. ../load.sh
python scripts/debug/beagle/read_fw_id.py
