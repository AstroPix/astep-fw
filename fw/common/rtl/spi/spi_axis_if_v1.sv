`include "axi_ifs.sv"

module spi_axis_if_v1 #(
    parameter QSPI = 0,
    parameter MSB_FIRST = 0,
    parameter CLOCK_OUT_CG = 1'b0 ) (

    // System clock
    input wire                    clk,
    input wire                    resn,
    input wire                    enable,


    // AXIS slave to receive bytes for SPI out
    //input  wire [31:0]            s_axis_count,
    input  wire [7:0]             s_axis_tdata,
    input  wire                   s_axis_tvalid,
    output reg                    s_axis_tready,
    //input  wire                   s_axis_tlast,


    // AXIS master to write received bytes
    output reg [7:0]              m_axis_tdata,
    output reg                    m_axis_tvalid,
    input  wire                   m_axis_tready,
    //output wire                   m_axis_tlast,
    

    // SPI Master
    output wire                      spi_csn,
    output wire                     spi_clk,
    output wire                     spi_mosi,
    input  wire [QSPI:0]            spi_miso             
);

    reg enable_synced; // Forced enable, synced in this Clock domain
    //wire enable_synced  =enable;
    reg spi_csn_reg;
    assign spi_csn = !resn ? 1'b1 : spi_csn_reg;

    //assign m_axis_tlast = 0 ;
    assign m_axis_tid   = 0 ;
    assign m_axis_tdest = 0 ;
    assign m_axis_tuser = 0 ;

    wire s_axis_empty = !s_axis_tvalid;
    wire s_axis_byte_valid = s_axis_tready && s_axis_tvalid;

    // Signals: MISO + AXIS Master Write 
    byte_t master_stage_byte;
    reg    master_stage_byte_valid;
    reg    master_stage_ignore_first;
    byte_t miso_byte;
    reg [3:0] miso_bit_counter;

    // AXIS Master Write
    wire    m_axis_byte_valid = m_axis_tready & m_axis_tvalid;
    wire    m_axis_byte_waiting = !m_axis_tready & m_axis_tvalid;

    // Signals: Clock
    // SPI Output clock is the same as the main clock 
    reg     spi_clk_enable;
    reg     spi_clk_enable_negedge;
    wire    spi_clk_running = (spi_clk_enable == 1 && spi_csn_reg==0);
    reg     spi_clk_pause;

    // MOSI (* IOB = "TRUE" *) 
    byte_t mosi_byte;
    assign spi_mosi = MSB_FIRST ?  mosi_byte[7] :mosi_byte[0] ;
    reg [3:0] mosi_bit_remaining;
    
    wire    spi_csn_reg_should_be_low = !s_axis_empty || enable_synced || mosi_bit_remaining>0;


    generate
        if (CLOCK_OUT_CG==1'b1) begin 
            /*BUFGCE spi_clk_buf BUFGMUX (
                .I(clk),
                .O(spi_clk),
                .CE((spi_clk_running && !spi_clk_pause))
            );*/
            wire clock_selected = (spi_clk_running && !spi_clk_pause && spi_clk_enable_negedge);
            BUFGCTRL  spi_clk_buf  (
                .I0(1'b0),
                .I1(clk),
                .O(spi_clk),
                .CE0(1'b1),
                .CE1(1'b1),
                .IGNORE0(1'b1),
                .IGNORE1(1'b1),
                .S0(!clock_selected ), //|| !resn
                .S1(clock_selected) // && resn
            );
            //assign  spi_clk = (spi_clk_running && !spi_clk_pause) ?  clk : 1'b0 ;
        end else begin
            assign  spi_clk = (spi_clk_running && !spi_clk_pause) ?  clk : 1'b0 ;
        end
    endgenerate
   

    // MISO Stage, runs on negedge and sends data to posedge master stage
    //--------------------
    always@(negedge clk) begin 
        if (!resn || !spi_clk_running) begin 
            miso_bit_counter            <= 0;
            
            master_stage_ignore_first   <= 1'b1;
            spi_clk_pause               <= 1'b0; 
            spi_clk_enable_negedge      <= 1'b1;
        end
        else begin 
            
            // Only Sample bits if spi clock is running
            if (spi_clk_running) begin 

                if (!spi_csn_reg_should_be_low) begin 
                    spi_clk_enable_negedge      <= 1'b0;
                end
                else 
                    spi_clk_enable_negedge      <= 1'b1;

                // Pause CLK if waiting to get the byte
                //RL: Changed on 02/10/23, fixed otherwise pausing first started after a bytes was lost at the interface if (master_stage_byte_valid && m_axis_byte_waiting)
                if (m_axis_byte_waiting)
                    spi_clk_pause <= 1'b1;
                else if (spi_clk_pause && m_axis_byte_valid)
                    spi_clk_pause <= 1'b0;

                if (!spi_clk_pause) begin 
                    // Data
                    if (QSPI) begin 

                        if (MSB_FIRST) begin 
                            miso_byte           <= {miso_byte[5:0],spi_miso[1],spi_miso[0]};
                        end else begin 
                            miso_byte           <= {spi_miso[1],spi_miso[0],miso_byte[7:2]};
                        end

                        miso_bit_counter    <= miso_bit_counter + 2;
                        
                    end
                    else begin 

                        if (MSB_FIRST) begin 
                            miso_byte           <= {miso_byte[6:0],spi_miso[0]};
                        end else begin 
                            miso_byte           <= {spi_miso[0],miso_byte[7:1]};
                        end
                        miso_bit_counter    <= miso_bit_counter + 1;

                    end

                end
                
                // Remove ignore first byte
                if (miso_bit_counter == 8 && master_stage_ignore_first) begin
                    master_stage_ignore_first   <= 1'b0;
                end

            end

            // Forwared Received Byte to axis master on posedge
            // This is done even if the spi clock is not running, otherwise the last byte after a MOSI driven sequence is never forwarded
            /*if (miso_bit_counter == 8 || (miso_bit_counter == 0 && !master_stage_ignore_first) ) begin
                master_stage_byte           <= miso_byte;
                master_stage_byte_valid     <= 1;
                master_stage_ignore_first   <= 1'b0;
            end
            else begin 
                master_stage_byte_valid <= 0;
            end*/
            
        end
    end

    // AXIS Master write byte stage from MISO
    //--------------
    always@(posedge clk ) begin
        if (!resn) begin 
            m_axis_tvalid <= 1'b0;
            master_stage_byte           <= 0;
            master_stage_byte_valid     <= 0;
            enable_synced <= 1'b0;
            //spi_clk_pause <= 1'b0;
        end
        else begin 

            // Sync enable in this CK
            enable_synced <= enable;
           
            // Forwared Received Byte to axis master buffer on posedge
            // This is done even if the spi clock is not running, otherwise the last byte after a MOSI driven sequence is never forwarded
            if (miso_bit_counter == 8 || (miso_bit_counter == 0 && !master_stage_ignore_first) ) begin
                master_stage_byte           <= miso_byte;
                master_stage_byte_valid     <= 1;
                //master_stage_ignore_first   <= 1'b0;
            end
            else begin 
                master_stage_byte_valid <= 0;
            end

            // Forward SPI byte to Axis master - This allows for the master to be ready while getting the next byte
            if (m_axis_byte_valid) begin 
                m_axis_tvalid <= 1'b0; 
            end
            else if (!m_axis_byte_waiting && master_stage_byte_valid) begin 
                m_axis_tvalid <= 1'b1; 
                m_axis_tdata  <= master_stage_byte;
            end
        end
    end

    
    // MOSI Stage
    //-----------------
   
    always@(posedge clk) begin 
        if (!resn) begin 
            s_axis_tready       <= 1'b0;
            spi_csn_reg         <= 1'b1;
            mosi_bit_remaining  <= 4'h0;
            spi_clk_enable      <= 1'b0;
            mosi_byte           <= 8'h00; // Reset Data Byte because it drives an output, helps makes simulation clearer too
        end
        else begin 

            // CS
            //--------
            if (/*s_axis_byte_valid*/!s_axis_empty || enable_synced || mosi_bit_remaining>0) begin 
                spi_csn_reg <= 1'b0;
            end
            else begin 
                spi_csn_reg <= 1'b1;
            end

            // Ready
            //--------
            if (!s_axis_empty && !s_axis_byte_valid && (mosi_bit_remaining==0 || mosi_bit_remaining==1) ) begin 
                s_axis_tready <= 1'b1;
            end
            else begin
                s_axis_tready <= 1'b0;
            end

            // Run stage only if not pausing the clock
            if (spi_csn_reg==0)
            begin 

                spi_clk_enable <= 1'b1;

                // Run stage only if not pausing the clock
                if (!spi_clk_pause) begin 

                    // Data
                    //----------

                    // Forward bytes
                    if (s_axis_byte_valid) begin 
                        mosi_byte           <= s_axis_tdata;
                        mosi_bit_remaining  <= 4'h7;
                    end
                    else if (mosi_bit_remaining == 0 && enable_synced)
                    begin
                        mosi_byte           <= 8'h00;
                        mosi_bit_remaining  <= 4'h7;
                    end
                    else  if (mosi_bit_remaining>0) begin 
                        if (MSB_FIRST) begin 
                            mosi_byte           <= {mosi_byte[6:0],1'b0};
                        end
                        else begin 
                            mosi_byte           <= {1'b0,mosi_byte[7:1]};
                        end
                        
                        mosi_bit_remaining  <= mosi_bit_remaining -1;
                    end
                end

            end
            else begin 
                spi_clk_enable <= 1'b0;
            end

           
            
        end
    end


endmodule