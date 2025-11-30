/*
This module calculates a CRC for a configuration by fetching the SIN after each CLK1 negedge into a byte,
when a byte is complete, pass it to CRC.

The SIN input should then be connected to the SOUT of a shift register CLK1.

The idea for this module is that external SR driver can set the readback for 1 clock cycle, then use a write command without any load to shift the bits out.
*/
module sr_readback_crc(

    input clk,
    input resn,

    input enable,

    input clk1,
    input clk2,
    input sin,

    output logic [31:0] crc,
    output logic [15:0] parities,
    output logic       crc_valid,
    
    output logic [7:0] bits_byte,
    output logic       bits_byte_valid
);
    localparam SYNC_SIZE =2;

    logic [SYNC_SIZE-1:0] clk1_posedge_reg;
    wire clk1_posedge = (|clk1_posedge_reg[SYNC_SIZE-1:1]) == 'b0 & clk1_posedge_reg[0]=='b1;

    logic [2:0] bitCount;
    logic [7:0] sinByte;
    logic       crc_enable;

    logic [7:0] even_bits_counter;
    logic [7:0] odd_bits_counter;

    assign bits_byte = sinByte;
    assign bits_byte_valid = crc_enable;


    assign parities = {odd_bits_counter,even_bits_counter};

    always_ff@(posedge clk) begin
        if (!resn || !enable ) begin
            crc_valid           <= 1'b0;
            clk1_posedge_reg    <= {SYNC_SIZE{1'b0}};
            bitCount            <= 'd0;
            even_bits_counter   <= 'd0;
            odd_bits_counter    <= 'd0;
            crc_enable          <= 'd0;

        end
        else begin

            // Sync in clk1
            clk1_posedge_reg <= {clk1_posedge_reg[SYNC_SIZE-2:0],clk1};

            // On Negedge, sample sin
            if (clk1_posedge) begin

                bitCount <= bitCount + 1'd1;
                sinByte <= {sinByte[6:0],sin};

                // Add even/odd bit sin value to the matching byte
                if (bitCount[0]==1'b1) begin
                    odd_bits_counter  <= odd_bits_counter + sin;
                end
                else begin
                    even_bits_counter <= even_bits_counter + sin;
                end

            end

            // CRC Enable
            if (bitCount==3'd7 && clk1_posedge) begin
                crc_enable <= 1'b1;
            end
            else begin
                crc_enable <= 1'b0;
            end

            // CRC Valid is one cycle after CRC was enabled
            crc_valid <= crc_enable;


        end

    end



    // CRC-32
    crc_calc #(
        .POLY         ( 32'h04C11DB7 ), // This is the most standard polynomial
        .CRC_SIZE     ( 32           ),
        .DATA_WIDTH   ( 8            ),
        .INIT         ( 32'hFFFFFFFF ),
        .XOR_OUT      ( 32'hFFFFFFFF )
      )  crc_inst (

        .clk_i        ( clk        ),
        .rst_i        ( !resn      ),
        .soft_reset_i ( !enable    ),
        .valid_i      ( crc_enable ),
        .data_i       ( sinByte    ),
        .crc_o        ( crc        )
    );


endmodule
