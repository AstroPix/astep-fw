-reflib ${UNISIM}/
${XILINX_VIVADO}/data/verilog/src/glbl.v

## Xilinx sim
#${BASE}/fw/common/xilinx-ip/top_clocking_core_io_uart/top_clocking_core_io_uart_sim_netlist.v
#${BASE}/fw/common/xilinx-ip/top_clocking_core_io_uart/top_clocking_core_io_uart_clk_wiz.v
#${BASE}/fw/common/xilinx-ip/top_clocking_core_io_uart/top_clocking_core_io_uart.v

${BASE}/fw/common/xilinx-ip/clk_sys_to_40/clk_sys_to_40_clk_wiz.v
${BASE}/fw/common/xilinx-ip/clk_sys_to_40/clk_sys_to_40.v


${BASE}/fw/common/xilinx-ip/clk_core_extorint_40/clk_core_extorint_40_clk_wiz.v
${BASE}/fw/common/xilinx-ip/clk_core_extorint_40/clk_core_extorint_40.v



#${BASE}/fw/common/xilinx-ip/axi_uartlite_core/axi_uartlite_core_sim_netlist.v

+incdir+${BASE}/fw/common/xilinx-ip/axis_switch_layer_frame/hdl
${BASE}/fw/common/xilinx-ip/axis_switch_swifs/hdl/axis_infrastructure_v1_1_vl_rfs.v
${BASE}/fw/common/xilinx-ip/axis_switch_swifs/hdl/axis_register_slice_v1_1_vl_rfs.v
${BASE}/fw/common/xilinx-ip/axis_switch_swifs/hdl/axis_switch_v1_1_vl_rfs.v
${BASE}/fw/common/xilinx-ip/axis_switch_swifs/sim/axis_switch_swifs.v
${BASE}/fw/common/xilinx-ip/axis_switch_layer_frame/sim/axis_switch_layer_frame.v

## FIFOS

+incdir+${BASE}/fw/common/xilinx-ip/fifo_axis_1clk_1kB/hdl
${BASE}/fw/common/xilinx-ip/fifo_axis_2clk_spi_hk/fifo_axis_2clk_spi_hk_sim_netlist.v

${BASE}/fw/common/xilinx-ip/fifo_axis_2clk_spi_layer/fifo_axis_2clk_spi_layer_sim_netlist.v

${BASE}/fw/common/xilinx-ip/fifo_axis_2clk_sw_io_16e/fifo_axis_2clk_sw_io_16e_sim_netlist.v

${BASE}/fw/common/xilinx-ip/fifo_axis_1clk_1kB/fifo_axis_1clk_1kB_sim_netlist.v

${BASE}/fw/common/xilinx-ip/fifo_axis_1clk_8x64/fifo_axis_1clk_8x64_sim_netlist.v


${BASE}/fw/common/xilinx-ip/fifo_axis_2clk_spi_loopback/fifo_axis_2clk_spi_loopback_sim_netlist.v

## ADC

${BASE}/fw/common/xilinx-ip/xadc_astep/xadc_astep_sim_netlist.v
