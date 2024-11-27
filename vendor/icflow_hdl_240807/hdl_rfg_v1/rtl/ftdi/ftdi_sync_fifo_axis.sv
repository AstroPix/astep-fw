
/**
 RFG
 Copyright (C) 2023  Felix Ehrler (felix.ehrler@kit.edu) and Richard Leys (richard.leys@kit.edu) , Rudolf Schimassek (rudolf.schimassek@kit.edu)
 
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

*/
module ftdi_sync_fifo_axis(

    // FTDI interface
    input  wire 		ftdi_clko,
    input  wire         resn,
    
    input  wire 		ftdi_txe_n, // 
    input  wire 		ftdi_rxf_n,

    output reg 		    ftdi_rd_n,
    output reg 		    ftdi_oe_n,
    output reg 		    ftdi_wr_n,

    inout  wire [7:0] 	ftdi_data,

    // Read from FTDI Axis master
    output wire [7:0]    m_axis_tdata,
    output wire          m_axis_tvalid,
    input  wire          m_axis_tready,
    input  wire          m_axis_almost_full,


    // Write to FTDI Axis Slave
    input   wire [7:0]   s_axis_tdata,
    input   wire         s_axis_tvalid,
    output  wire         s_axis_tready,
    input   wire         s_axis_almost_empty

);

    parameter   PRIORITY = 1'b0; // 1'b0 = read priority,  1'b1 = write priority

    // I/O Assignment
    assign ftdi_data = ftdi_oe_n ? s_axis_tdata : 8'hzz;
    assign m_axis_tdata = ftdi_data;

    // Asynchronous assignments, write/read condition are passed to axis interface
    // in axis language, write is valid and read is ready
    wire writefifo_rd_en  = ~ftdi_txe_n && ~ftdi_wr_n;
    wire readfifo_wr_en   = ~ftdi_rxf_n && ~ftdi_rd_n;

    assign m_axis_tvalid = readfifo_wr_en;
    assign s_axis_tready = writefifo_rd_en;

    // FSM
    //---------------
    ftdi_interface_control_fsm fsm_I ( 
        .clk(ftdi_clko), 
        .res_n(resn), 
        .rxf_n(ftdi_rxf_n), 
        .txe_n(ftdi_txe_n), 
        .rd_n(ftdi_rd_n), 
        .oe_n(ftdi_oe_n), 
        .wr_n(ftdi_wr_n),

        .rf_almost_full(m_axis_almost_full), // Read fifo is the direction FTDI -> FPGA (read from FTDI)
        .wf_almost_empty(s_axis_almost_empty), // Write FIFO is the direction FPGA -> FTDI (write to FTDI)
        .wf_empty(!s_axis_tvalid), 
        .prio(1'b1)
    );

endmodule