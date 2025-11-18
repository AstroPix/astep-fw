-sv
-64bit
-access +rw
-define SIMULATION
-define TARGET_NEXYS
-define SINGLE_LAYER

## Xilinx
-f ${BASE}/fw/astep24-3l/verification/xilinx_sim_libs.f

## Top
${BASE}/fw/astep24-3l/target-multiboard/astep24_3l_multitarget_top.sv

## Common
+define+RFG_FW_ID=32'h0000ff00
+define+RFG_FW_BUILD=32'h0000ffAB

## Main Verilog
-f ${BASE}/fw/astep24-3l/common/astep24_3l_top.f
