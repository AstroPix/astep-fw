
## Top
${BASE}/fw/astep24-3l/common/astep24_3l_top.sv
${BASE}/fw/astep24-3l/common/astep24_3l_top_clocking.sv


## Patgen for injection
${BASE}/fw/common/rtl/layers/sync_async_patgen.sv


## RFG Host
${BASE}/fw/astep24-3l/common/main_rfg.sv

${BASE}/fw/common/rtl/host/sw_ftdi245_spi_uart/sw_ftdi245_spi_uart.sv

${BASE}/fw/common/rtl/rfg/ftdi/ftdi_sync_fifo_axis.sv
${BASE}/fw/common/rtl/rfg/ftdi/ftdi_interface_control_fsm.sv

${BASE}/fw/common/rtl/rfg/spi/spi_slave_axis_egress.sv
${BASE}/fw/common/rtl/rfg/spi/spi_slave_axis_igress.sv

${BASE}/fw/common/rtl/rfg/uart/uart_lite_driver.sv

${BASE}/fw/common/rtl/rfg/protocol/rfg_axis_protocol_srl_fifo.sv
${BASE}/fw/common/rtl/rfg/protocol/rfg_axis_protocol.sv
${BASE}/fw/common/rtl/rfg/protocol/rfg_axis_readout_framing.sv

## Layer 
-f ${BASE}/fw/common/rtl/layers/layers_readout_switched.f

## Housekeeping
-f ${BASE}/fw/common/rtl/housekeeping/housekeeping_main.f


## Helpers
+incdir+${BASE}/fw/common/includes
${BASE}/fw/common/rtl/utilities/reset_sync.sv
${BASE}/fw/common/rtl/utilities/async_input_sync.sv
${BASE}/fw/common/rtl/utilities/async_signal_sync.sv
${BASE}/fw/common/rtl/utilities/resets_synchronizer.sv
${BASE}/fw/common/rtl/utilities/edge_detect.sv