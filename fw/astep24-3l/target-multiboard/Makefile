# gecco-astropix2.build 
ALL_BUILDS=gecco-astropix3.build cmodr2-astep.build
CCTB_ARGS ?= 

clean:
	@rm -Rf vivado-run/ .Xil bitstreams reports
	@rm -f .openMode* *.log *.rpt

%.open: 
	@echo "Opening Project for target $(basename $@)"
	@mkdir -p vivado-run
	@cd vivado-run && OPEN=1 vivado  -source ../$(basename $@).tcl

build: export CI=1
build: $(ALL_BUILDS)
%.build:
	@echo "Building Project for target $(basename $@)"
	@mkdir -p vivado-run
	@cd vivado-run && vivado -mode batch -source ../$(basename $@).tcl

verify.nexys: export PYTHONPATH := $(shell pwd)/../verification:$(BASE)/fw/common/verification:$(PYTHONPATH)
verify.nexys: CCTB_ARGS := $(CCTB_ARGS) -f $(shell pwd)/astep24_3l_multitarget_top.nexys.sim.f
verify.nexys: export IC_SIM_TB := sim_top_nexys
verify.nexys:
	@icf_cctb $(CCTB_ARGS)

inspect.nexys: export IC_SIM_UI := 1
inspect.nexys: verify.nexys

verify.cmod: export PYTHONPATH := $(shell pwd)/../verification:$(BASE)/fw/common/verification:$(PYTHONPATH)
verify.cmod: CCTB_ARGS := $(CCTB_ARGS) -f $(shell pwd)/astep24_3l_multitarget_top.cmod.sim.f
verify.cmod: export IC_SIM_TB := sim_top_cmod
verify.cmod:
	@echo "Args: $(CCTB_ARGS)"
	@icf_cctb $(CCTB_ARGS)

inspect.cmod: export IC_SIM_UI := 1
inspect.cmod: verify.cmod

