
SHELL=/bin/bash
CCTB_ARGS=

install: sudo npm -gi junit-cli-report-viewer

## Purge Clean
## This target tries to delete as much as possible, for example to remove work files and help more easily check git status
mrproper: clean
	@make -C target-multiboard/ clean

## Clean
#########
clean: 
	@rm -Rf verification/.icflow

clean_sim:
	@rm -Rf verification/.icflow/sim/xcelium.d

## RFG
rfg: common/main_rfg.sv
common/main_rfg.sv: common/astep24_3layers.rfg.tcl
	@cd common && icf_rfg ./astep24_3layers.rfg.tcl -md $(BASE)/docs/markdown/fw/main_rfg.md

## Firmware build
##############
gecco-astropix2: gecco-astropix2.fw
gecco-astropix3: gecco-astropix3.fw
%.fw: 
	@make -C target-multiboard/ $(basename $@).build

## Verification  sim_hk.verify
############
verify: export PYTHONPATH := $(shell pwd)/verification/:$(BASE)/fw/common/verification:$(PYTHONPATH)
verify: clean_sim verification/.icflow/sim/design.txt
	@cd verification/ && clear && icf_cctb
	@junit-cli-report-viewer verification/.icflow/sim/results.xml


%.verify: export PYTHONPATH := $(shell pwd)/verification:$(BASE)/fw/common/verification:$(PYTHONPATH)
%.verify: clean_sim verification/.icflow/sim/design.txt
	@echo "Verifying $(basename $@) with args $(CCTB_ARGS) and path $(shell echo \${PYTHONPATH})"
	@cd verification/  &&  IC_SIM_TB=$(basename $@) icf_cctb $(CCTB_ARGS)
	@cd verification/.icflow/sim && npm run report


%.verify_synth: CCTB_ARGS:=-sim_synth
%.verify_synth: %.verify
	

%.inspect: CCTB_ARGS := -ui
%.inspect: %.verify
	

%.inspect_synth: CCTB_ARGS:=-ui -sim_synth
%.inspect_synth: %.verify
	

verification/.generated/rtl/astep24_3l_top_sim.f: verification/gen_verilog.tcl
	@cd verification && tclsh gen_verilog.tcl

verification/.icflow/sim/design.txt: verification/files/design.txt
	@mkdir -p verification/.icflow/sim/
	@cp verification/files/design.txt verification/.icflow/sim/