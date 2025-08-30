
/**
    This module receives bytes from AXIS and transmits to the classic rf_protocol_processor
    Readout paths writes back to the target port


*/
module rfg_axis_protocol  #(
    parameter DATA_WIDTH = 8,
    parameter ID_DEST_WIDTH = 8,
    parameter AXIS_MASTER_DEST = 0) (


    // System Signals
    input wire                      clk,
    input wire                      resn,

    // Axi Stream Side for Interconnect
    //-----------------------

    // AXI Stream master port, to write bytes out to the IO interface port
    output logic [DATA_WIDTH-1:0]    m_axis_tdata,
    output logic                     m_axis_tvalid,
    input  wire                     m_axis_tready,
    output logic                     m_axis_tlast,
    output reg  [ID_DEST_WIDTH-1:0] m_axis_tid, // ID is passed back to readout from header
    output reg  [ID_DEST_WIDTH-1:0] m_axis_tdest, // Destination is set from slave ID input


    // AXIS slave to receive protocol bytes from IO interface
    input  wire [DATA_WIDTH-1:0]    s_axis_tdata,
    input  wire                     s_axis_tvalid,
    output reg                      s_axis_tready,
    input  wire [ID_DEST_WIDTH-1:0] s_axis_tid, // Source Port from slave so that answers are forwared back to the right port

    output reg [15:0]               rfg_address,
    output reg [7:0]                rfg_write_value,
    output reg                      rfg_write,
    output reg                      rfg_write_last,
    output reg                      rfg_read,
    input  wire                     rfg_read_valid,
    input  wire [7:0]               rfg_read_value

);


        // AXIS Output
        //--------------

        wire m_axis_write_valid         = m_axis_tvalid && m_axis_tready;
        wire m_axis_write_stall         = m_axis_tvalid && !m_axis_tready;
        wire m_axis_write_invalid       = !m_axis_tvalid;
        wire m_axis_write_available     = m_axis_tready;

        // Receive Bytes for protocol
        //---------------
        wire axis_sink_byte_valid       = s_axis_tready && s_axis_tvalid;

        typedef struct packed {
            bit [7:4] vchannel;
            bit extended_address;
            bit address_increment;
            bit read;
            bit write;
        } header_t;

        header_t rfg_header;
        word_t   rfg_length;
        word_t   rfg_current_length;

        wire rfg_header_write        = rfg_header[0];
        wire rfg_header_incr_address = rfg_header[1];


        // Output
        //-----------

        // Read Path FIFO
        // RFG Reads are writting to this fifo, the AXIS output state reads from the fifo
        //-------------
        reg read_buffer_write;
        wire read_buffer_full;
        wire read_buffer_almost_full;
        wire read_buffer_empty;
        wire read_buffer_almost_empty;
        reg [8:0] read_buffer_data_in;
        wire [8:0] read_buffer_data_out;
        mini_fwft_fifo # (
            .AWIDTH(4),
            .DWIDTH(9)
        )
        mini_fwft_fifo_inst (
            .clk(clk),
            .resn(resn),
            .full(read_buffer_full),
            .almost_full(read_buffer_almost_full),
            .empty(read_buffer_empty),
            .almost_empty(read_buffer_almost_empty),
            .write(read_buffer_write),
            .read(m_axis_write_valid),
            .data_in(read_buffer_data_in),
            .data_out(read_buffer_data_out)
        );

        assign m_axis_tdata = read_buffer_data_out[7:0];
        assign m_axis_tlast = read_buffer_data_out[8];
        assign m_axis_tvalid = !read_buffer_empty;


        // Main Process
        //----------------


        typedef enum logic [3:0] {
            HEADER,
            ADDRESS,
            ADDRESSB,
            LENGTHA,
            LENGTHB,
            WRITE_VALUE,
            READ_VALUE,
            READ,
            FORWARD,
            READ_FINISH
        }   rfg_protocol_states;
        rfg_protocol_states rfg_state;

        assign rfg_read = !read_buffer_almost_full && rfg_state == READ;

        always @(posedge clk) begin
            if (resn==0) begin

                rfg_state           <= HEADER;
                rfg_write           <= 1'b0;
                rfg_write_last      <= 1'b0;

                s_axis_tready       <= 1'b0;

                //m_axis_tlast        <= 'b0;
                read_buffer_write   <= 1'b0;



            end
            else begin


                // RFG Main Protocol
                //----------------
                case (rfg_state)

                    HEADER: begin

                        // Reset interfaces outputs
                        s_axis_tready   <= 1'b1;
                        rfg_write       <= 1'b0;
                        rfg_write_last  <= 1'b0;

                        if (axis_sink_byte_valid && (s_axis_tdata[0] || s_axis_tdata[1])) begin
                            rfg_state     <= ADDRESS;
                            rfg_header    <= s_axis_tdata;

                            // Update the master destination bus with the source
                            // This allows multiple I/O interfaces to send data to this module
                            // The readout will then route the bytes back to the correct interface
                            m_axis_tdest <= s_axis_tid;
                        end
                    end

                    // Address is 1 or 2 bytes depending on header
                    // --------------
                    ADDRESS: begin

                        // 12/12/2024: Added Extended address mode to allow 16bit addresses
                        if (axis_sink_byte_valid && rfg_header.extended_address) begin
                            rfg_state     <= ADDRESSB;
                            rfg_address[7:0]   <= s_axis_tdata;
                        end
                        else if (axis_sink_byte_valid) begin
                            rfg_state     <= LENGTHA;
                            rfg_address   <= {8'h00,s_axis_tdata};
                        end
                    end

                    ADDRESSB: begin
                        if (axis_sink_byte_valid) begin
                            rfg_address[15:8]   <= s_axis_tdata;
                            rfg_state           <= LENGTHA;
                        end

                    end


                    // 2 Bytes of Length
                    // ----------------------
                    LENGTHA: begin
                        if (axis_sink_byte_valid) begin
                            rfg_state       <= LENGTHB;
                            rfg_length[7:0] <= s_axis_tdata;
                        end
                    end

                    LENGTHB: begin
                        if (axis_sink_byte_valid) begin

                            // Update Length
                            rfg_length[15:8]    <= s_axis_tdata;
                            rfg_current_length  <= {s_axis_tdata,rfg_length[7:0]};

                            // Tag the AXIS Master out with vchannel as Destination queue for software
                            m_axis_tid <= {4'h00,rfg_header.vchannel};

                            // Transition to Read/Write
                            if (rfg_header.write) begin
                                rfg_state   <= WRITE_VALUE;
                            end
                            else if (rfg_header.read) begin
                                rfg_state   <= READ;
                                //rfg_read    <= 1'b1;
                            end
                            else begin
                                rfg_state   <= HEADER;
                            end
                        end
                    end

                    // Read:
                    // READ state reads from RFG side
                    // When all data is written to local fifo buffer, go to READ_FINISH to wait until AXIS Master stage writes the last byte
                    //-------------

                    READ: begin

                        // Go to finish
                        if (rfg_current_length=='d1 && rfg_read  ) begin
                            rfg_state               <= READ_FINISH;
                        end

                        // Read and write to FIFO
                        if (rfg_read_valid) begin
                            read_buffer_write       <= 1'b1;
                            read_buffer_data_in    <=  {1'b0,rfg_read_value};

                        end
                        else if (!(read_buffer_write && read_buffer_full)) begin
                            read_buffer_write       <= 1'b0;
                        end

                        // Read
                        if (rfg_read & !read_buffer_full) begin
                            rfg_current_length  <= rfg_current_length - 1'd1;

                        end


                        // Address increment
                        if (rfg_read && rfg_header.address_increment) begin
                            rfg_address <= rfg_address + 1'd1;
                        end

                    end

                    READ_FINISH: begin
                        if (rfg_read_valid) begin
                            read_buffer_write       <= 1'b1;
                            read_buffer_data_in    <= {1'b1,rfg_read_value};
                        end else if (read_buffer_write && !read_buffer_full) begin
                            read_buffer_write       <= 1'b0;
                        end
                        if ( m_axis_tlast && m_axis_write_valid) begin
                            rfg_state               <= HEADER;
                        end
                    end

                    // Write to RFG until all data written
                    //-------------

                    WRITE_VALUE: begin
                        if (axis_sink_byte_valid) begin

                            // Write out
                            rfg_write       <= 1'b1;
                            rfg_write_value <= s_axis_tdata;
                            rfg_write_last  <= rfg_current_length == 1'b1;

                            // Decrease done length, go back to header if finished
                            if (rfg_current_length == 'd1 ) begin
                                rfg_state           <= HEADER;
                            end
                            else begin
                                rfg_current_length  <= rfg_current_length - 1'd1;
                            end
                        end
                        else begin
                            rfg_write       <= 1'b0;
                            rfg_write_last  <= 1'b0;
                        end

                        // Address increment
                        if (rfg_write && rfg_header.address_increment) begin
                            rfg_address <= rfg_address + 1'd1;
                        end
                    end

                endcase



            end
        end




endmodule
