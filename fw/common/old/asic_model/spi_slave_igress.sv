
/**
    header command: 7:5
    header data: 4:0

    This module receices LSB First

*/
module spi_slave_igress (

        input  wire        resn,
        input  wire        spi_clk, 
        input  wire        spi_csn,
        input  wire        spi_mosi,
        

        // reset state to header
        input wire reset_to_header,

        // IGress Interface for received data
        output reg  [7:0] out_rcv_byte,
        output reg        out_header,
        output reg        out_data,
        output wire [2:0] out_header_cmd,
        output wire [4:0] out_header_parameters
    );

    // IGRESS
    //-------------------------------
    enum {HEADER,DATA} state;
    reg [2:0] counter;


    assign out_header_cmd = out_rcv_byte [7:5];
    assign out_header_parameters = out_rcv_byte [4:0];

    // MOSI in
    //-------------
    always @(negedge spi_clk or posedge spi_csn or negedge resn)
        if (!resn || spi_csn) begin


            out_rcv_byte <= 8'h00;
            out_header   <= 1'b0;
            out_data     <= 1'b0;
            counter      <= 3'b000;
            state        <= HEADER;

        end
        else
        begin

            // Shift MOSI in SPI Byte LSB First
            //---------------
            out_rcv_byte <= {spi_mosi,out_rcv_byte[7:1]};
            counter      <= counter + 1;


            // When counter is 7, byte done is 1 (overflow), otherwise byte done is 0
            if(counter ==3'b111)
            begin

                if (state==HEADER)
                begin
                    state      <= DATA ;
                    out_header <= 1'b1;
                end
                else begin
                    out_data <= 1'b1;
                end

            end else begin
                if (reset_to_header)
                begin
                    state <= HEADER; 
                end
                out_header <= 1'b0;
                out_data   <= 1'b0;
            end

        end



endmodule
