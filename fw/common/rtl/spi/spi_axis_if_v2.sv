`include "axi_ifs.sv"

module spi_axis_if_v2 #( parameter QSPI = 0) (

    // System clock
    input wire                    clk,
    input wire                    resn,
    input wire                    enable,

    /*

    Clock Polarity (CPOL):

        CPOL = 0:
        The clock signal idles low, meaning the clock line is at a logic low level when the SPI is inactive.
        CPOL = 1:
        The clock signal idles high, meaning the clock line is at a logic high level when the SPI is inactive.

    Clock Phase (CPHA):

        CPHA = 0:
        Data is captured on the rising edge of the clock (when CPOL is 0) or on the falling edge (when CPOL is 1). Data is also shifted out on the opposite edge.
        CPHA = 1:
        Data is captured on the falling edge of the clock (when CPOL is 0) or on the rising edge (when CPOL is 1). Data is also shifted out on the opposite edge.


    */
    input wire                    cpol,
    input wire                    cpha,
    input wire                    msb_first,

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
    byte_t      master_stage_byte;
    reg         master_stage_byte_valid;
    reg         master_stage_ignore_first;

    byte_t      miso_byte;
    logic       miso_byte_valid;
    reg [2:0]   miso_bit_counter;
    wire        miso_last_sample = QSPI ? miso_bit_counter == 6 : miso_bit_counter == 7;

    // AXIS Master Write
    wire        m_axis_byte_valid = m_axis_tready & m_axis_tvalid;
    wire        m_axis_byte_waiting = !m_axis_tready & m_axis_tvalid;

    // Signals: Clock
    // SPI Output clock is the same as the main clock
    //--------------
    enum {IDLE,POSEDGE,NEGEDGE,A,B} spi_clock_state;
    logic   spi_clk_reg;
    assign  spi_clk = spi_clk_reg;

    reg     spi_clk_enable;
    reg     spi_clk_enable_negedge;
    wire    spi_clk_running = (spi_clk_enable == 1 && spi_csn_reg==0);
    reg     spi_clk_pause;



    //wire        stall_module = (miso_byte_valid && !m_axis_tready) || m_axis_byte_waiting;
     wire        stall_module =   m_axis_byte_waiting;

    // MOSI
    // //-----------
    byte_t      mosi_byte;
    assign      spi_mosi = msb_first ?  mosi_byte[7] :mosi_byte[0] ;
    reg [2:0]   mosi_bit;


    // This is a bit confusing, to output on posedge the logic runs during the negedge state
    wire        mosi_output = !stall_module && ( (cpha == 0 && cpol ==0  && spi_clock_state == A) ||
                                (cpha == 0 && cpol == 1  && spi_clock_state == B) ||
                               (cpha == 1 && cpol ==0  && spi_clock_state == B) ||
                               (cpha == 1 && cpol ==1  && spi_clock_state == A) );
    wire        miso_sample = !stall_module && spi_clock_state != IDLE && !mosi_output;

    wire        mosi_can_take_next = (mosi_bit == 'd7 && spi_clock_state == B) ||spi_clock_state == IDLE ;
    wire        mosi_next_is_ready = (mosi_can_take_next && spi_clock_state == B) ||spi_clock_state == IDLE ;
    wire        mosi_has_data = (s_axis_tvalid || enable_synced) && m_axis_tready;

    assign s_axis_tready = mosi_can_take_next;

    // SPI Clock State
    // ------------------


    always_ff @(posedge clk) begin
        if (!resn) begin
            spi_clock_state <= IDLE;
            spi_clk_reg     <= cpol;
        end else begin

            case({stall_module,spi_clock_state})
                {1'b0,IDLE}: begin
                    if (mosi_has_data) begin
                        spi_clock_state <= A;
                        spi_clk_reg     <= !spi_clk_reg;
                    end
                    else begin
                        spi_clk_reg     <= cpol;
                    end
                end
                {1'b0,A}: begin
                    //spi_clock_state <= mosi_can_take_next && !mosi_has_data ? IDLE :  B;
                    spi_clk_reg     <= !spi_clk_reg;
                    spi_clock_state <= mosi_can_take_next && !mosi_has_data ? IDLE :  B;

                end
                {1'b0,B}: begin
                    spi_clock_state <=  mosi_can_take_next && !mosi_has_data ? IDLE : A;
                    spi_clk_reg     <=  mosi_can_take_next && !mosi_has_data ? cpol : !spi_clk_reg;
                end

                default: begin

                end

            endcase

        end
    end

    // MOSI Stage
    // ---------------
    always_ff @(posedge clk) begin
        if (!resn) begin
            mosi_bit        <= 'd0;
            enable_synced   <= 1'b0;
            //s_axis_tready   <= 'b1;
        end
        else begin

            // Sync enable in this CK
            //-----------
            if (mosi_can_take_next) begin
                enable_synced       <= enable;
            end


            // Byte to send: Either take from AXIS or force from enable
            // ---------
            //s_axis_tready <= mosi_next_is_ready && !s_axis_byte_valid && m_axis_tready; // always ready, only not if the read stage is stalling
            if (mosi_can_take_next && s_axis_byte_valid  ) begin
                mosi_byte           <= s_axis_tdata;
                mosi_bit            <= 4'h0;
            end
            else if (mosi_can_take_next && enable_synced) begin
                mosi_byte           <= 'd0;
                mosi_bit            <= 4'h0;
            end

            // MOSI Change data on clock state
            // --------------
            else if (mosi_output) begin
                if (msb_first) begin
                    mosi_byte           <= {mosi_byte[6:0],1'b0};
                end
                else begin
                    mosi_byte           <= {1'b0,mosi_byte[7:1]};
                end
                if (!stall_module)
                    mosi_bit  <= mosi_bit + 'b1;
            end
        end
    end

    // MISO Stage
    // -------------------
    always_ff @(posedge clk) begin
        if (!resn) begin
            miso_bit_counter    <= 'b0;
            miso_byte_valid     <= 'b0;
            m_axis_tvalid       <= 1'b0;
        end
        else begin

            // Sample Bits
            // ----------------
            if (miso_sample ) begin

                // Data
                // -----------
                if (QSPI) begin

                    if (msb_first) begin
                        miso_byte           <= {miso_byte[5:0],spi_miso[1],spi_miso[0]};
                    end else begin
                        miso_byte           <= {spi_miso[1],spi_miso[0],miso_byte[7:2]};
                    end

                    miso_bit_counter        <= miso_bit_counter + 2;

                    miso_byte_valid <= miso_bit_counter == 6;


                end
                else begin

                    if (msb_first) begin
                        miso_byte           <= {miso_byte[6:0],spi_miso[0]};
                    end else begin
                        miso_byte           <= {spi_miso[0],miso_byte[7:1]};
                    end
                    miso_bit_counter        <= miso_bit_counter + 1;

                    miso_byte_valid <= miso_bit_counter == 7;

                end

            end
            else if (miso_byte_valid && !miso_sample && !m_axis_byte_waiting) begin
                miso_byte_valid <= 'b0;
            end

            // Output to axis
            // ------------
            if (miso_byte_valid && !miso_sample && !m_axis_byte_waiting) begin
                m_axis_tdata    <= miso_byte;
                m_axis_tvalid   <= 1'b1;
            end
            else if (m_axis_byte_valid) begin
                m_axis_tvalid   <= 1'b0;
            end

        end



    end



endmodule
