`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 22.07.2023 19:37:27
// Design Name: 
// Module Name: uart_lite_sv_driver
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////
`include "axi_ifs.sv" 

/**

This module is the actual UART Lite driver written in SV

*/
module uart_lite_driver #(
    parameter DEST_WIDTH = 8,
    parameter ID_WIDTH = 8,
    parameter USER_WIDTH = 1,
    parameter DATA_WIDTH = 8,
    parameter C_M_AXI_ADDR_WIDTH = 4,
    parameter C_M_AXI_DATA_WIDTH = 32,
    parameter AXIS_DEST = 0,
    parameter AXIS_SOURCE = 0
    ) (

        // System Signals
        input wire aclk,
        input wire aresetn,

        // Axi Stream Side for Interconnect
        //-----------------------
        
        // AXI Stream master port, for received bytes to be written out
        output wire [7:0]             m_axis_tdata,
        output reg                    m_axis_tvalid,
        input  wire                   m_axis_tready,
        //output wire                   m_axis_tlast,
        output wire [ID_WIDTH-1:0]    m_axis_tid, // Source ID for RFG to route back
        output wire [7:0]             m_axis_tdest, // Destination for RFG Switch
        //output wire [USER_WIDTH-1:0]  m_axis_tuser,
        
        // AXIS slave for eceived bytes to send out to UART
        // Written to by crossbar in NOC design
        input  wire [7:0]             s_axis_tdata,
        input  wire                   s_axis_tvalid,
        output reg                    s_axis_tready,
        //input  wire                   s_axis_tlast,
        //input  wire [ID_WIDTH-1:0]    s_axis_tid,
        //input  wire [7:0]             s_axis_tdest,
        //input  wire [USER_WIDTH-1:0]  s_axis_tuser,
        
        // AXI4-Lite Master to drive the UART Lite core
        //--------------

        // Master Interface Write Address
        output wire [C_M_AXI_ADDR_WIDTH-1:0] M_AXI_AWADDR,
        output wire M_AXI_AWVALID,
        input wire M_AXI_AWREADY,

        // Master Interface Write Data
        output wire [C_M_AXI_DATA_WIDTH-1:0] M_AXI_WDATA,
        output wire [C_M_AXI_DATA_WIDTH/8-1:0] M_AXI_WSTRB,
        output wire M_AXI_WVALID,
        input wire M_AXI_WREADY,

        // Master Interface Write Response
        input wire [2-1:0] M_AXI_BRESP,
        input wire M_AXI_BVALID,
        output wire M_AXI_BREADY,

        // Master Interface Read Address
        output wire [C_M_AXI_ADDR_WIDTH-1:0] M_AXI_ARADDR,
        output wire M_AXI_ARVALID,
        input wire M_AXI_ARREADY,

        // Master Interface Read Data
        input wire [C_M_AXI_DATA_WIDTH-1:0] M_AXI_RDATA,
        input wire [2-1:0] M_AXI_RRESP,
        input wire M_AXI_RVALID,
        output wire M_AXI_RREADY,

        // Sideband signals
        //-----------------
        input wire interrupt_uart,
        output reg uart_init_done,
        output reg uart_got_byte,
        output reg [7:0]    uart_rcv_byte
    
    );
    

    // IF
    //--------------
    AXI_LITE #(
        .AXI_DATA_WIDTH(C_M_AXI_DATA_WIDTH),
        .AXI_ADDR_WIDTH(C_M_AXI_ADDR_WIDTH)) uart_axi_if();
    AXIS #(
        .AXIS_ADDR_WIDTH(DEST_WIDTH),
        .AXIS_USER_WIDTH(USER_WIDTH),
        .AXIS_DATA_WIDTH(DATA_WIDTH),
        .AXIS_ID_WIDTH(ID_WIDTH))     uart_m_axis_if();
        AXIS #(
            .AXIS_ADDR_WIDTH(DEST_WIDTH),
            .AXIS_USER_WIDTH(USER_WIDTH),
            .AXIS_DATA_WIDTH(DATA_WIDTH),
            .AXIS_ID_WIDTH(ID_WIDTH))     uart_s_axis_if();

    assign M_AXI_AWADDR         = uart_axi_if.aw_addr;
    assign M_AXI_AWVALID        = uart_axi_if.aw_valid;
    assign uart_axi_if.aw_ready = M_AXI_AWREADY;
    
    assign M_AXI_WDATA          = uart_axi_if.w_data;
    assign M_AXI_WSTRB          = uart_axi_if.w_strb;
    assign M_AXI_WVALID         = uart_axi_if.w_valid;
    assign uart_axi_if.w_ready  = M_AXI_WREADY;

    assign uart_axi_if.b_valid  = M_AXI_BVALID;
    assign M_AXI_BREADY         = uart_axi_if.b_ready;

    assign M_AXI_ARADDR         = uart_axi_if.ar_addr;
    assign M_AXI_ARVALID        = uart_axi_if.ar_valid;
    assign uart_axi_if.ar_ready = M_AXI_ARREADY;

    assign uart_axi_if.r_data   = M_AXI_RDATA;
    assign uart_axi_if.r_valid  = M_AXI_RVALID;
    assign M_AXI_RREADY         = uart_axi_if.r_ready;

    // AXIS Master output (UART to Switch)
    assign m_axis_tdata             = uart_m_axis_if.tdata;
    assign m_axis_tvalid            = uart_m_axis_if.tvalid;    
    //assign m_axis_tlast             = uart_m_axis_if.tlast;
    //assign m_axis_tid               = uart_m_axis_if.tid;
    assign m_axis_tid               = {ID_WIDTH{AXIS_SOURCE}};
    assign m_axis_tdest             = uart_m_axis_if.tdest;
    //assign m_axis_tuser             = uart_m_axis_if.tuser;
    always_comb begin
        uart_m_axis_if.tready       = m_axis_tready;
    end

    
    assign s_axis_tready            = uart_s_axis_if.tready; 
    always_comb begin
        //uart_s_axis_if.tlast        = s_axis_tlast;
        //uart_s_axis_if.tid          = s_axis_tid;
        //uart_s_axis_if.tdest        = s_axis_tdest;
        //uart_s_axis_if.tuser        = s_axis_tuser;
        uart_s_axis_if.tdata        = s_axis_tdata;
        uart_s_axis_if.tvalid       = s_axis_tvalid;
    end

    // UART Receive stage, will be read by AXIS side
    //-------------
    //reg [7:0]    uart_axi_data;
    reg          uart_rcv_byte_valid;

    typedef struct packed {
        bit err_parity;
        bit err_frame;
        bit err_overrun;
        bit intr_enabled;
        bit tx_fifo_full;
        bit tx_fifo_empty;
        bit rx_fifo_full;
        bit rx_fifo_valid_data;
    } uart_status_t;
    uart_status_t uart_status;
    reg           uart_status_updated;

    // AXIS Receive stage, will be transmitted to UART via AXI
    //----------------
    byte_t uart_byte_to_send;

    
    // Core initialisation
    //----------------
    typedef enum {UFW_INIT,UFW_INIT_SETUP,UFW_INIT_DONE, UFW_IDLE,UFW_WRITE_FIFO,UFW_WAIT_STATUS}  uart_write_states;
    uart_write_states                               uart_write_state;

    // AXI Read: Status and Data read
    //---------
    typedef enum {UFR_WAIT_INIT,UFR_IDLE,UFR_READ_STATUS,UFR_READ_FIFO,UFR_AXI_DATA} uart_fifo_readout_states;
    uart_fifo_readout_states uart_fifo_readout_state;
    uart_fifo_readout_states uart_fifo_readout_state_next;
    
    // 1 if UART core gives interrupt or we are writting data
    // This will trigger reader the status of core to ensure we are not overruning it
    wire axi_start_read = interrupt_uart || uart_write_state == UFW_WRITE_FIFO;

    always@(posedge aclk) begin
        if (aresetn==0) begin
            uart_axi_if.reset_master(); 
            uart_init_done           <= 0;
            
            //uart_axi_if.aw_valid <= 1'b0;
            uart_write_state     <= UFW_INIT;
            //uart_send_byte_ready <= 1'b1;

            // UART -> AXI
            uart_fifo_readout_state         <= UFR_WAIT_INIT;
            uart_fifo_readout_state_next    <= UFR_IDLE;
            uart_rcv_byte                   <= 8'h00;
            uart_rcv_byte_valid             <= 1'b0;
            uart_got_byte                   <= 1'b0;

            uart_status_updated <= 1'b0;

            // AXIS -> UART
            uart_s_axis_if.reset_slave();

            
        end
        else begin

            // AXI Write Path to Core
            //--------------------
            case (uart_write_state)
                UFW_INIT: begin
                    uart_write_state <= UFW_INIT_SETUP;
                end
            
                UFW_INIT_SETUP: begin
                    if (!uart_axi_if.aw_valid)
                    begin
                        uart_axi_if.master_single_write(4'hC,5'b10000);
                    end
                    else if (uart_axi_if.aw_ready && uart_axi_if.w_ready) begin
                        uart_axi_if.master_write_done();
                        uart_write_state <= UFW_INIT_DONE;
                    end
                    
                    
                end
                
                UFW_INIT_DONE: begin
                    uart_init_done <= 1'b1;
                    uart_write_state <= UFW_IDLE;
                end

                UFW_IDLE: begin
                    // Accept Stream byte for UART core if valid asserted and status has no tx fifo full
                    if (uart_s_axis_if.tvalid && !uart_status.tx_fifo_full) begin
                        
                        uart_s_axis_if.s_accept();
                        uart_byte_to_send       <= uart_s_axis_if.tdata;
                        uart_write_state        <= UFW_WRITE_FIFO;
                    end
                    
                end
                
                UFW_WRITE_FIFO: begin

                    uart_s_axis_if.s_not_ready();

                    if (uart_axi_if.aw_valid==0)
                    begin
                        uart_axi_if.master_single_write(4'h04,uart_byte_to_send);
                    end
                    else if (uart_axi_if.aw_ready) begin
                        uart_axi_if.master_write_done();
                        uart_write_state        <= UFW_WAIT_STATUS;
                    end
                end

                UFW_WAIT_STATUS: begin 
                    if (uart_status_updated) begin 
                        uart_write_state <= UFW_IDLE;
                    end
                end


            endcase;


            //---------------------------
            // AXI Read: Read Data and Status Registers
            //---------------------------
            case (uart_fifo_readout_state)
                UFR_WAIT_INIT: begin 
                    if (uart_init_done) begin 
                        uart_fifo_readout_state <= UFR_IDLE;
                    end
                end
                UFR_IDLE: begin
                    if (axi_start_read) begin
                        uart_fifo_readout_state <= UFR_READ_STATUS;
                    end
                end
                
                // Read Status of Module to see if there are data
                //------------
                UFR_READ_STATUS: begin
                    if (!uart_axi_if.ar_valid) begin
                        uart_axi_if.master_read(4'h8);
                    end
                    else if (uart_axi_if.ar_ready) begin
                        uart_axi_if.master_read_done();
                        uart_fifo_readout_state <= UFR_AXI_DATA; 
                        uart_fifo_readout_state_next <= UFR_READ_FIFO;
                    end
                    
                    
                end
            
                // Read Byte from FIFO
                //-----------------
                UFR_READ_FIFO: begin
                
                    // REad fifo is preceded by status read
                    // If status shows no data, don't read and go back to waiting
                    if (uart_status.rx_fifo_valid_data)
                    begin
                        if (!uart_axi_if.ar_valid) begin
                            uart_axi_if.master_read(4'h0);
                        end
                        else if (uart_axi_if.ar_ready) begin
                            uart_axi_if.master_read_done(); 
                            uart_fifo_readout_state         <= UFR_AXI_DATA; 
                            uart_fifo_readout_state_next    <= UFR_READ_STATUS;
                        end
                        
                    end
                    else begin
                        uart_fifo_readout_state <= interrupt_uart ? UFR_READ_STATUS : UFR_IDLE;
                    end
                    
                
                    
                end
                
                // GET Axi Data and go to next provided state
                // If reading from FIFO, save to byte register
                //----------------
                UFR_AXI_DATA: begin
                    if (uart_axi_if.r_valid) begin
                        uart_fifo_readout_state <= uart_fifo_readout_state_next; 
                    end
                end
            
            endcase;
            
            // Data Path: Receiving UART byte
            // When AXI_DATA state reached and the read address was the RX fifo, we got a byte
            //------------------
            case (uart_fifo_readout_state)
                
                UFR_AXI_DATA: begin
                    if (uart_axi_if.r_valid) begin
                        //uart_axi_data <= uart_axi_if.r_data[7:0];

                        // Was reading byte
                        if (uart_axi_if.ar_addr==4'h0) begin
                            uart_rcv_byte       <= uart_axi_if.r_data[7:0];
                            uart_rcv_byte_valid <= 1'b1;
                            uart_got_byte       <= !uart_got_byte;
                        end
                        // Was reading status
                        else if (uart_axi_if.ar_addr==4'h8) begin
                            uart_status_updated <= 1'b1;
                            uart_status         <= uart_axi_if.r_data[7:0];
                        end
                    end
                end
                
                default: begin
                    uart_status_updated <= 1'b0;
                    uart_rcv_byte_valid <= 1'b0;
                end
                
            endcase;
        
        
        end     
    end

    // AXI Stream Master output (UART RX -> RFG)
    //----------------------

    always @(posedge aclk)
    begin

        // Reset or wait for initialisation
        if (!aresetn || !uart_init_done)
        begin
            //s_axis_tready <= 1'b0;
            //m_axis_tvalid <= 1'b0;
            uart_m_axis_if.reset_master();
        end
        else begin
            
            if (uart_rcv_byte_valid && !uart_m_axis_if.tvalid)
            begin
                uart_m_axis_if.m_write_single(AXIS_DEST,8'h00,uart_rcv_byte);
            end
            else if (uart_m_axis_if.tvalid && uart_m_axis_if.tready)
                uart_m_axis_if.reset_master();
            
            
        end
    
    end

    
    always @(posedge aclk)
    begin

        // Reset or wait for initialisation
        if (!aresetn || !uart_init_done)
        begin
            //s_axis_tready <= 1'b0;
            //m_axis_tvalid <= 1'b0;
            uart_m_axis_if.reset_master();
        end
        else begin
            
            if (uart_rcv_byte_valid && !uart_m_axis_if.tvalid)
            begin
                uart_m_axis_if.m_write_single(AXIS_DEST,8'h00,uart_rcv_byte);
            end
            else if (uart_m_axis_if.tvalid && uart_m_axis_if.tready)
                uart_m_axis_if.reset_master();
            
            
        end
    
    end
    
    
endmodule
