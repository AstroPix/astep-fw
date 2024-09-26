-reflib ${UNISIM}/
${XILINX_VIVADO}/data/verilog/src/glbl.v

## Xilinx sim
${BASE}/fw/common/xilinx-ip/top_clocking_core_io_uart/top_clocking_core_io_uart_sim_netlist.v


${BASE}/fw/common/xilinx-ip/axi_uartlite_core/axi_uartlite_core_sim_netlist.v

+incdir+${BASE}/fw/common/xilinx-ip/axis_switch_layer_frame/hdl
${BASE}/fw/common/xilinx-ip/axis_switch_swifs/hdl/axis_infrastructure_v1_1_vl_rfs.v
${BASE}/fw/common/xilinx-ip/axis_switch_swifs/hdl/axis_register_slice_v1_1_vl_rfs.v
${BASE}/fw/common/xilinx-ip/axis_switch_swifs/hdl/axis_switch_v1_1_vl_rfs.v
${BASE}/fw/common/xilinx-ip/axis_switch_swifs/sim/axis_switch_swifs.v
${BASE}/fw/common/xilinx-ip/axis_switch_layer_frame/sim/axis_switch_layer_frame.v

+incdir+${BASE}/fw/common/xilinx-ip/fifo_axis_1clk_1kB/hdl
#${BASE}/fw/common/xilinx-ip/fifo_axis_2clk_16e_routing/fifo_axis_2clk_16e_routing_sim_netlist.v
#${BASE}/fw/common/xilinx-ip/fifo_axis_2clk_16e_packet/fifo_axis_2clk_16e_packet_sim_netlist.v
#${BASE}/fw/common/xilinx-ip/fifo_axis_2clk_64e/fifo_axis_2clk_64e_sim_netlist.v
#${BASE}/fw/common/xilinx-ip/fifo_axis_2clk_64e_packet/fifo_axis_2clk_64e_packet_sim_netlist.v

${BASE}/fw/common/xilinx-ip/fifo_axis_2clk_spi_hk/fifo_axis_2clk_spi_hk_sim_netlist.v
${BASE}/fw/common/xilinx-ip/fifo_axis_2clk_spi_layer/fifo_axis_2clk_spi_layer_sim_netlist.v
${BASE}/fw/common/xilinx-ip/fifo_axis_1clk_1kB/fifo_axis_1clk_1kB_sim_netlist.v
${BASE}/fw/common/xilinx-ip/fifo_axis_2clk_sw_io_16e/fifo_axis_2clk_sw_io_16e_sim_netlist.v


${BASE}/fw/common/xilinx-ip/xadc_astep/xadc_astep_sim_netlist.v