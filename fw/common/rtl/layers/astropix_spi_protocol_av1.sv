`include "axi_ifs.sv"

/**

This module receives Bytes from SPI and interrupt and orchestrates forcing readout
*/
module astropix_spi_protocol_av1 #(
    parameter DATA_WIDTH = 8,
    parameter ID_WIDTH = 8,
    parameter DEST_WIDTH = 8,
    parameter USER_WIDTH = 1,
    parameter LAYER_ID = 3'h0,
    parameter IDLE_BYTE = 8'h3D)(


    // System clock and control
    input wire clk,
    input wire resn,
    input wire interruptn,
    input wire enable,

    // AXIS slave to receive bytes from SPI Readout
    input  wire [DATA_WIDTH-1:0]  s_axis_tdata,
    input  wire                   s_axis_tvalid,
    output reg                    s_axis_tready,
    //  wire                   s_axis_tlast,
    

    // AXIS master to forward bytes to FIFO
    output reg [DATA_WIDTH-1:0]   m_axis_tdata,
    output reg                    m_axis_tvalid,
    input  wire                   m_axis_tready,
    output reg                    m_axis_tlast,
    output wire [DEST_WIDTH-1:0]  m_axis_tdest,


    // Readout control
    output reg                    readout_active,

    // Statistics 
    output reg                    stat_frame_detected,
    output reg                    stat_idle_detected,

    // Status
    output reg                    status_frame_decoding,

    // Configs
    input  wire                   cfg_disable_autoread,
    input  wire [31:0]            cfg_frame_tag_counter,
    input  wire [7:0]             cfg_nodata_continue, // Number of IDLE bytes to keep readout active after interrupt is high
    input  wire                   cfg_layer_reset
);

    // Receiving interface
    //-------------
    wire slave_byte_valid       = s_axis_tready && s_axis_tvalid;
    wire slave_byte_available   = s_axis_tvalid;

    byte_t receive_frame_length; 
    byte_t receive_frame_length_frozen; 

    byte_t forward_byte_buffer;

    reg [31:0] forward_frozen_timestamp;

    // Forware interface to FIFO or switch
    //--------------
    wire master_byte_valid       = m_axis_tvalid && m_axis_tready;
    wire master_byte_waiting     = m_axis_tvalid && !m_axis_tready;

    assign m_axis_tdest     = 8'h00;
    //assign m_axis_tid       = 8'h00;
    //assign m_axis_tuser     = 1'b1;

    // Readout activate delay after interrupt removed
    reg [7:0] nodata_continue_counter;

    // Frame Header Buffer until headers are send 
    reg [7:0] frame_buffer;

    // Process
    //-----------------
    enum {WAIT_FRAME,HEADER_LENGTH,HEADER_ID,RECEIVE,FORWARD,TIMESTAMP0,TIMESTAMP1,TIMESTAMP2,TIMESTAMP3} protocol_state;

    always @(posedge clk) begin 
        if (!resn || cfg_layer_reset) begin 
            s_axis_tready           <= 1'b0;
            
            readout_active          <= 1'b0;
            protocol_state          <= WAIT_FRAME;

            m_axis_tvalid           <= 1'b0;
            m_axis_tlast            <= 1'b0;

            stat_frame_detected     <= 1'b0;
            stat_idle_detected      <= 1'b0;

            status_frame_decoding   <= 1'b0;
        end
        else begin 
            
           // m_axis_tvalid <= 1'b0;

            // Force Readout on interrupt
            //------------
            if (!interruptn && !cfg_disable_autoread) begin 
                readout_active          <= 1'b1;
                nodata_continue_counter <= cfg_nodata_continue;
            end else if (interruptn && protocol_state==WAIT_FRAME) begin
                
                if (nodata_continue_counter==0) begin
                    readout_active <= 1'b0;
                end else begin
                    nodata_continue_counter <= nodata_continue_counter -1;
                end 

            end
            
            
            // Receive Bytes
            //-------------------
            case (protocol_state)
                

                WAIT_FRAME: begin 
                    status_frame_decoding   <= 1'b0;
                    m_axis_tlast            <= 1'b0;
                    s_axis_tready           <= 1'b1; 

                    // Got Frame Header, and not Idle byte
                    if (slave_byte_valid && s_axis_tdata!=IDLE_BYTE) begin 
                        
                        // Send Header Length
                        protocol_state              <= HEADER_LENGTH;

                        receive_frame_length        <= s_axis_tdata[2:0];
                        receive_frame_length_frozen <= s_axis_tdata[2:0];

                        // Length: ID + FRAME LENGTH + 4 TS bytes
                        frame_buffer                <= s_axis_tdata;
                        m_axis_tdata                <= s_axis_tdata[2:0] + 6;
                        m_axis_tvalid               <= 1'b1;
                        s_axis_tready               <= 1'b0; 

                        // Toggle Frame detected for 1 cycle to enable counting
                        stat_frame_detected          <= 1'b1;

                        // Save Counter for timestamp
                        forward_frozen_timestamp     <= cfg_frame_tag_counter;

                        // Report decoding status
                        status_frame_decoding        <= 1'b1;

                    end else if (slave_byte_valid && s_axis_tdata==IDLE_BYTE) begin 

                        // Toggle Frame detected for 1 cycle to enable counting
                        stat_idle_detected <= 1'b1;

                    end
                    else begin 

                        stat_idle_detected  <= 1'b0;

                    end

                end

                HEADER_LENGTH: begin 
                    stat_frame_detected          <= 1'b0;

                    // Send Header ID
                    if (master_byte_valid) begin 
                        protocol_state          <= HEADER_ID;
                        m_axis_tdata            <= LAYER_ID;
                    end
                    

                end

                HEADER_ID: begin 

                    // Send Frame
                    if (master_byte_valid) begin 
                        protocol_state          <= FORWARD;
                        m_axis_tdata            <= frame_buffer;
                    end

                end
            

                FORWARD: begin 
                    
                    stat_frame_detected          <= 1'b0;
                    if (master_byte_valid) begin 

                        // Finished, add other data
                        if (receive_frame_length==0) begin 
                            protocol_state  <= TIMESTAMP0;
                            m_axis_tvalid   <= 1'b1;
                            m_axis_tdata    <= forward_frozen_timestamp[7:0];
                            s_axis_tready   <= 1'b0;
                        end else begin 
                            protocol_state  <= RECEIVE;
                            m_axis_tvalid   <= 1'b0;
                            s_axis_tready   <= 1'b1;
                        end
                        
                        m_axis_tlast <= 1'b0;
                    end
                end

                RECEIVE: begin 
                    if (slave_byte_valid) begin 

                        protocol_state          <= FORWARD; 

                        // Decount one byte
                        receive_frame_length <= receive_frame_length -1;

                        // If master stage is ready for byte, leave slave to ready
                        s_axis_tready <= m_axis_tready;

                        // Output
                        m_axis_tdata            <= s_axis_tdata;
                        m_axis_tvalid           <= 1'b1;
                        

                    end
                end

                

                TIMESTAMP0: begin 
                    if (master_byte_valid) begin 
                        protocol_state  <= TIMESTAMP1;
                        m_axis_tvalid   <= 1'b1;
                        m_axis_tdata    <= forward_frozen_timestamp[15:8];
                    end
                end
                TIMESTAMP1: begin 
                    if (master_byte_valid) begin 
                        protocol_state  <= TIMESTAMP2;
                        m_axis_tvalid   <= 1'b1;
                        m_axis_tdata    <= forward_frozen_timestamp[23:16];
                    end
                end
                TIMESTAMP2: begin 
                    if (master_byte_valid) begin 
                        protocol_state  <= TIMESTAMP3;
                        m_axis_tvalid   <= 1'b1;
                        m_axis_tdata    <= forward_frozen_timestamp[31:24];
                        m_axis_tlast    <= 1'b1;
                    end
                end
                TIMESTAMP3: begin 
                    if (master_byte_valid) begin 
                        protocol_state  <= WAIT_FRAME;
                        m_axis_tvalid   <= 1'b0;
                        m_axis_tlast    <= 1'b0;
                    end
                end

                default: begin 
                    protocol_state <= WAIT_FRAME;
                end
            endcase
        end
    end


endmodule 