
`include "axi_ifs.sv" 

/**
    This module receives bytes from AXIS and transmits to the classic rf_protocol_processor
    Readout paths writes back to the target port

    @require ./rfg_axis_protocol_srl_fifo.sv
    @incdir  ${HDLBUILDV1_HOME}/svlib/includes
*/
module rfg_axis_protocol  #(
    parameter DATA_WIDTH = 8,
    parameter ID_WIDTH = 8,
    parameter AXIS_MASTER_DEST = 0) (


    // System Signals
    input wire                      aclk,
    input wire                      aresetn,

    // Axi Stream Side for Interconnect
    //-----------------------
    
    // AXI Stream master port, to write bytes out to the IO interface port
    output wire [DATA_WIDTH-1:0]    m_axis_tdata,
    output wire                     m_axis_tvalid,
    input  wire                     m_axis_tready,
    output wire                     m_axis_tlast,
    output reg [ID_WIDTH-1:0]       m_axis_tid, // ID is passed back to readout from header
    output reg  [7:0]               m_axis_tdest, // Destination is set from slave ID input

    
    // AXIS slave to receive protocol bytes from IO interface
    input  wire [DATA_WIDTH-1:0]    s_axis_tdata,
    input  wire                     s_axis_tvalid,
    output reg                      s_axis_tready,
    input  wire [ID_WIDTH-1:0]      s_axis_tid, // Source Port from slave so that answers are forwared back to the right port
    input  wire [7:0]               s_axis_tdest,
 

    output reg [7:0]                rfg_address,
    output reg [7:0]                rfg_write_value,
    output reg                      rfg_write,
    output reg                      rfg_write_last,
    output reg                      rfg_read,
    input  wire                     rfg_read_valid,
    input  wire [7:0]               rfg_read_value
);


        // AXIS
        //--------------

        // Master inferface to write data to SW I/O
        AXIS #(
        .AXIS_ADDR_WIDTH(8),
        .AXIS_USER_WIDTH(1),
        .AXIS_DATA_WIDTH(DATA_WIDTH),
        .AXIS_ID_WIDTH(ID_WIDTH))    switch_m_axis_if ();

        assign m_axis_tdata             = switch_m_axis_if.tdata;
        assign m_axis_tvalid            = switch_m_axis_if.tvalid;
        assign m_axis_tlast             = switch_m_axis_if.tlast;
        always_comb begin 
            switch_m_axis_if.tready     = m_axis_tready;
        end

        wire m_axis_write_valid         = switch_m_axis_if.tvalid && switch_m_axis_if.tready;
        wire m_axis_write_stall         = switch_m_axis_if.tvalid && !switch_m_axis_if.tready;
        wire m_axis_write_invalid       = !switch_m_axis_if.tvalid;
        wire m_axis_write_available     = switch_m_axis_if.tready;

        // Receive Bytes for protocol
        //---------------
        wire axis_sink_byte_valid       = s_axis_tready && s_axis_tvalid;

        typedef struct packed {
            bit [7:4] vchannel;
            bit RSVD;
            bit address_increment;
            bit read;
            bit write;
        } header_t;
        
        header_t rfg_header;
        word_t   rfg_length;
        word_t   rfg_current_length;
        word_t   rfg_master_length;
        //byte_t rfg_value;

        wire rfg_header_write        = rfg_header[0];
        wire rfg_header_incr_address = rfg_header[1];

 
        // Output
        //-----------

        // Read Path FIFO
        //-------------
        reg read_buffer_write;
        reg read_buffer_read;
        wire read_buffer_full;
        wire read_buffer_almost_full;
        wire read_buffer_empty;
        wire read_buffer_almost_empty;
        reg [7:0] read_buffer_data_in;
        wire [7:0] read_buffer_data_out;

        mini_fwft_fifo # (
            .AWIDTH(2),
            .DWIDTH(8)
        )
        mini_fwft_fifo_inst (
            .clk(aclk),
            .resn(aresetn),
            .full(read_buffer_full),
            .almost_full(read_buffer_almost_full),
            .empty(read_buffer_empty),
            .almost_empty(read_buffer_almost_empty),
            .write(read_buffer_write),
            .read(!m_axis_write_stall),
            .data_in(read_buffer_data_in),
            .data_out(read_buffer_data_out)
        );
        /*rfg_axis_protocol_srl_fifo read_buffer(
            .clk(aclk),
            .resn(aresetn),
            .write_value(read_buffer_data_in),
            .read_value(read_buffer_data_out),
            .write(read_buffer_write),
            .read(!m_axis_write_stall),
            .full(read_buffer_full),
            .almost_full(read_buffer_almost_full),
            .empty(read_buffer_empty),
            .almost_empty(read_buffer_almost_empty)
        );*/


        // Main Process
        //----------------
        

        typedef enum {RFP_HEADER,RFP_ADDRESS,RFP_LENGTHA,RFP_LENGTHB,RFP_WRITE_VALUE,RFP_READ_VALUE,RFP_READ,RFP_FORWARD,RFP_READ_FINISH}   rf_protocol_states;
        rf_protocol_states rfp_state;
        
        assign rfg_read = !read_buffer_almost_full && rfp_state == RFP_READ;

        always @(posedge aclk) begin 
            if (aresetn==0) begin 

                rfp_state       <= RFP_HEADER;
                rfg_write       <= 1'b0;
                rfg_write_last  <= 1'b0;
           
                s_axis_tready <= 1'b0;

                switch_m_axis_if.reset_master();
                //m_axis_tdest  <= 8'h00;
                //m_axis_tid    <= {}

                read_buffer_write <= 1'b0;
                read_buffer_read  <= 1'b0;

            end
            else begin 
           
                // Readback AXIS Master stage
                //-------------
                case (rfp_state)
                    
                    RFP_READ,RFP_READ_FINISH: begin 

                        // If not empty, transfer data and set valid
                        if (read_buffer_empty && m_axis_write_valid && rfp_state == RFP_READ_FINISH) begin 
                            switch_m_axis_if.m_invalid();
                        end
                        else if ((!read_buffer_empty && read_buffer_read && !m_axis_tvalid) || (!read_buffer_empty && m_axis_write_valid)) begin 
                            switch_m_axis_if.m_write_start(AXIS_MASTER_DEST,8'h00,read_buffer_data_out);
                            if (rfg_master_length==1) begin 
                                switch_m_axis_if.m_last();
                            end
                        end

                        // Pause reading if not ready
                        read_buffer_read <= m_axis_tready;

                        // Count valid cycles
                        if (!m_axis_write_stall && !read_buffer_empty) begin 
                            rfg_master_length <= rfg_master_length -1;
                        end
                    end
                    default: begin 
                        read_buffer_read <= 1'b1;
                    end
                endcase

                // RFG Side state
                //----------------
                case (rfp_state)

                    RFP_HEADER: begin 

                        // Reset interfaces outputs
                        s_axis_tready   <= 1'b1;
                        rfg_write       <= 1'b0;
                        rfg_write_last  <= 1'b0;
                        //rfg_read        <= 1'b0;
                        switch_m_axis_if.m_invalid();

                        if (axis_sink_byte_valid && (s_axis_tdata[0] || s_axis_tdata[1])) begin 
                            rfp_state     <= RFP_ADDRESS;
                            rfg_header    <= s_axis_tdata;
                            
                            // Update the master destination bus with the source
                            // This allows multiple I/O interfaces to send data to this module
                            // The readout will then route the bytes back to the correct interface
                            m_axis_tdest <= s_axis_tid;
                        end
                    end

                    RFP_ADDRESS: begin 
                        if (axis_sink_byte_valid) begin 
                            rfp_state     <= RFP_LENGTHA;
                            rfg_address   <= s_axis_tdata;
                        end
                    end

                    RFP_LENGTHA: begin 
                        if (axis_sink_byte_valid) begin 
                            rfp_state       <= RFP_LENGTHB;
                            rfg_length[7:0] <= s_axis_tdata;
                        end
                    end

                    RFP_LENGTHB: begin 
                        if (axis_sink_byte_valid) begin 

                            // Update Length
                            rfg_length[15:8]    <= s_axis_tdata;
                            rfg_current_length  <= {s_axis_tdata,rfg_length[7:0]};
                            rfg_master_length   <= {s_axis_tdata,rfg_length[7:0]};

                            // Tag the AXIS Master out with vchannel as Destination queue for software
                            m_axis_tid <= {4'h00,rfg_header.vchannel};

                            // Transition to Read/Write
                            if (rfg_header.write) begin 
                                rfp_state   <= RFP_WRITE_VALUE;
                            end
                            else if (rfg_header.read) begin 
                                rfp_state   <= RFP_READ;
                                //rfg_read    <= 1'b1;
                            end
                            else begin 
                                rfp_state   <= RFP_HEADER;
                            end
                        end
                    end

                    RFP_READ_FINISH: begin 
                        if (rfg_read_valid) begin 
                            read_buffer_write       <= 1'b1;
                            read_buffer_data_in    <= rfg_read_value;
                        end else if (read_buffer_write && !read_buffer_full) begin
                            read_buffer_write       <= 1'b0;
                        end
                        if (read_buffer_empty && m_axis_write_valid) begin 
                            rfp_state               <= RFP_HEADER;
                        end
                    end
                    RFP_READ: begin 

                        // Go to finish
                        if (rfg_current_length==1 && rfg_read /*&& (read_buffer_write && !read_buffer_full)*/) begin 
                            rfp_state               <= RFP_READ_FINISH;
                        end

                        // Read and write to FIFO
                        if (rfg_read_valid) begin 
                            read_buffer_write       <= 1'b1;
                            read_buffer_data_in    <= rfg_read_value;
                        end
                        else if (!(read_buffer_write && read_buffer_full)) begin 
                            read_buffer_write       <= 1'b0;
                        end

                        // Read
                        //rfg_read <= !read_buffer_almost_full && (rfg_current_length > 1) ;

                        if (/*read_buffer_write && !read_buffer_full*/ rfg_read) begin 
                            rfg_current_length  <= rfg_current_length - 1; 
                        end

                        // Address increment
                        if (rfg_read && rfg_header.address_increment) begin
                            rfg_address <= rfg_address + 1;
                        end

                    end

                    RFP_WRITE_VALUE: begin 
                        if (axis_sink_byte_valid) begin 

                            // Write out
                            rfg_write       <= 1'b1;
                            rfg_write_value <= s_axis_tdata;
                            rfg_write_last  <= rfg_current_length == 1'b1;

                            // Decrease done length, go back to header if finished
                            if (rfg_current_length == 1 ) begin 
                                rfp_state           <= RFP_HEADER;
                            end
                            else begin
                                rfg_current_length  <= rfg_current_length - 1; 
                            end
                        end
                        else begin
                            rfg_write       <= 1'b0; 
                            rfg_write_last  <= 1'b0;
                        end

                        // Address increment
                        if (rfg_write && rfg_header.address_increment) begin
                            rfg_address <= rfg_address + 1;
                        end
                    end

                endcase

                // Data
                //----------------

            end
        end

        // Low Level Protocol Handler (OrderSorter originally)
        //------------------------
        
        

endmodule