/**
    
    This module receices MSB First

*/
module spi_slave_axis_igress #( 
    parameter DEST_WIDTH    = 8,
    parameter ID_WIDTH      = 8,
    parameter AXIS_DEST     = 0,
    parameter AXIS_SOURCE   = 0,
    parameter ASYNC_RES     = 0, 
    parameter MSB_FIRST     = 1  ) (

        // Async reset
        input  wire                         spi_clk, 
        input  wire                         spi_csn,
        input  wire                         spi_mosi,
        

        // AXIS Output
        output reg  [7:0]                   m_axis_tdata,
        output reg                          m_axis_tvalid,
        input  wire                         m_axis_tready,
        output wire [DEST_WIDTH-1:0]        m_axis_tdest,
        output wire [ID_WIDTH-1:0]          m_axis_tid,

        output reg                          err_overrun
       
    );

    // State
    //-------------------------------
    enum reg {DATA,WRITE} state;
    reg [2:0] counter;
    reg [7:0] rcv_byte;

    // AXIS
    //------------
    assign m_axis_tdest = AXIS_DEST;
    assign m_axis_tid   = AXIS_SOURCE;

    // MOSI in
    //-------------
    task reset();
        m_axis_tvalid   <= 1'b0;
        counter         <= 3'b000;
        state           <= DATA;
        err_overrun     <= 1'b0;
    endtask
    task receive();

        // Shift MOSI in SPI Byte LSB First
        //---------------
        if (MSB_FIRST == 1)
            rcv_byte <= {rcv_byte[6:0],spi_mosi};
        else 
            rcv_byte <= {spi_mosi,rcv_byte[7:1]};

        counter      <= counter + 1'b1;


        // When counter is 7, byte done is 1 (overflow), otherwise byte done is 0
        if(counter ==3'b111)
        begin
            state <= WRITE;
        end else begin
            state <= DATA;
        end

        if (state==WRITE) begin 
            if (m_axis_tready!=1'b1) begin 
                err_overrun <= 1'b1;
            end
            m_axis_tvalid <= 1'b1;
            m_axis_tdata  <= rcv_byte;
        end
        else 
            m_axis_tvalid <= 1'b0;

    endtask
    generate


    always @(negedge spi_clk or posedge spi_csn) begin 
        if ( spi_csn) begin
            reset();
        end else begin 
            receive();
        end
    end
      
        
        

    endgenerate
    


endmodule