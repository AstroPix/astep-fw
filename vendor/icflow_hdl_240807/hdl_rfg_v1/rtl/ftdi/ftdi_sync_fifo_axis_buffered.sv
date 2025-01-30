
/**
Copyright 2023 Karlsruher Institute für Technologie - R. Leys ; N.Striebig ; F.Ehrler ; I.Peric

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
module ftdi_sync_fifo_axis_buffered(

    // FTDI interface
    input  wire 		ftdi_clko,
    input  wire         resn,
    
    input  wire 		ftdi_txe_n, // 
    input  wire 		ftdi_rxf_n,

    (* IOB = "true" *) output reg 		    ftdi_rd_n,
    (* IOB = "true" *) output reg 		    ftdi_oe_n,
    (* IOB = "true" *) output reg 		    ftdi_wr_n,

    inout  wire [7:0] 	ftdi_data,

    // Read from FTDI Axis master
    output reg [7:0]    m_axis_tdata,
    output reg          m_axis_tvalid,
    input  wire         m_axis_tready,
    input  wire         m_axis_almost_full,


    // Write to FTDI Axis Slave
    input   wire [7:0]   s_axis_tdata,
    input   wire         s_axis_tvalid,
    output  reg          s_axis_tready,
    input   wire         s_axis_almost_empty

);

    wire ftdi_data_available = !ftdi_rxf_n;
    wire ftdi_write_possible = !ftdi_txe_n && !ftdi_data_available && ftdi_oe_n==1;

    // Writing to FTDI, means reading from slave AXIS
    wire  ftdi_read_data_valid = ftdi_data_available && !ftdi_oe_n && !ftdi_rd_n;

    // Reading from FTDI, means writing to master axis
    wire ftdi_can_akcnowledge_data = m_axis_tready && ftdi_data_available && ftdi_oe_n==0;
    wire m_axis_byte_valid = m_axis_tvalid && m_axis_tready;



    // FTDI data is I/O
    (* IOB = "true" *) reg [7:0] ftdi_data_out;
    assign ftdi_data = !ftdi_oe_n ? 8'hzz : ftdi_data_out; // If OE is 1, we can write

    // Drive the control signals and output data on negedge
    always @(posedge ftdi_clko) begin 
        if (!resn) begin 
        
            ftdi_rd_n <= 1'b1;
            ftdi_wr_n <= 1'b1;
            ftdi_oe_n <= 1'b1;

            m_axis_tvalid <= 1'b0;
            s_axis_tready <= 1'b1;
        end
        else begin

            // Data Read from FTDI, RDN and OEN
            // When Data is available, turn OEN to 0, then RDN to 0
            // As long as data is avaiable, if the output axis interface is stalling, just pause RDN

             // OEn
            if (m_axis_tready && ftdi_data_available && ftdi_oe_n==1) begin 
                ftdi_oe_n <= 1'b0;
            end else if (!ftdi_data_available) begin 
                ftdi_oe_n <= 1'b1;
            end

            // RDn
            if (ftdi_can_akcnowledge_data) begin 
                ftdi_rd_n <= 1'b0;
            end else begin 
                ftdi_rd_n <= 1'b1;
            end

            // Data In
            if (ftdi_rxf_n==1) begin 
                m_axis_tvalid <= 1'b0;
            end else if ((ftdi_oe_n==0 && ftdi_rd_n==0) || ftdi_can_akcnowledge_data ) begin 
                m_axis_tdata <= ftdi_data;
                m_axis_tvalid <= 1'b1;
            end
            
            // Data Write to FTDI: OEN is managed by read - if not reading, we are free to write
            //-----------
            
            // WRn: if oe and txe
            if (ftdi_oe_n && ftdi_write_possible && s_axis_tvalid && !ftdi_data_available) begin 
                ftdi_wr_n     <= 1'b0;
            end
            else if (!s_axis_tvalid || ftdi_data_available) begin 
                ftdi_wr_n     <= 1'b1;
            end

            // Ready: on valid axis cycle and no place in ftdi, stop ready
            if (s_axis_tvalid && s_axis_tready && !ftdi_write_possible) begin 
                s_axis_tready   <= 1'b0;
            end else if (s_axis_tvalid) begin 
                s_axis_tready   <= ftdi_write_possible;
            end else begin 
                s_axis_tready   <= 1'b1;
            end

            // Output data to out register on axis valid cycle
            if (s_axis_tvalid && s_axis_tready) begin
                ftdi_data_out   <= s_axis_tdata;
            end
          

            
        end

    end

endmodule