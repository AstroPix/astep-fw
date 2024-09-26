
/**
 * This Egress just sequentially loads a wide register to 8bit Egress Fifo interface
 * The data is made available through a simple FIFO Interface
 *
 * This module is compliant with 1 Byte Header
 * 
 * ! Warning, this is QSPI with 2 bits on the MISO path, so outputs are done 2 bits at a time
 *  This module send LSB first
 */
 module spi_slave_egress #(
         parameter IDLE_VALUE   = 8'h3D // This is the command for Stream Receive
        ) (
 
        input  wire        resn,
         
        input  wire        spi_clk, 
        output wire [1:0]  spi_miso,
        input  wire        spi_csn,
        

        input   wire        fifo_empty,
        output reg          fifo_shift_out,
        input  wire [7:0]   fifo_data
     );
 
 
     // State
 
     // Byte Output
     //----------
     reg  [7:0] egress_byte_buffer;
     reg  [2:0] egress_bit_counter;
     wire       egress_bit_counter_last = egress_bit_counter==7;
 
     reg [7:0] egress_byte;
     reg       egress_byte_external;
 
 
  
    assign spi_miso = !spi_csn ? {egress_byte[1],egress_byte[0]} : 2'b00;
    
 
     // State
     //-----------
     enum {WAIT,IDLE , DATA} state;
 
     // MTU Reach

 
 
     // MISO Out
     always @(posedge spi_clk or posedge spi_csn or negedge resn)
     begin
         if (!resn || spi_csn )
         begin
             state              <= WAIT;
             egress_byte        <= {IDLE_VALUE};
             egress_byte_buffer <= {IDLE_VALUE};
             egress_bit_counter <= 3'b000;
 
             fifo_shift_out       <= 1'b0;
             egress_byte_external <= 1'b0;

         end
         else begin
 
             // State
             // - Send IDLE, if data availabe send first header then stream
             //--------------
             case ({egress_bit_counter,state})
                 {8'd0,WAIT}:
                 begin
                     state <= IDLE;
                 end
                 {8'd6,IDLE}:
                 begin
                     if (!fifo_empty)
                     begin
                         state <= DATA;
                         fifo_shift_out <= 1'b1;
                     end
                 end
                 // Load next byte
                 // Bit 5 -> shift out during bit 6
                 // Bit 6 -> wait
                 // Bit 7 ( last) -> save fifo data to egress byte
                 //-------------
                 {8'd6,DATA}:
                 begin
                      if (!fifo_empty)
                     begin
                         fifo_shift_out <= 1'b1;
                         state <= DATA;
                     end
                     else
                     begin
                          state <= IDLE;
                     end
                    
                 end
                 //-------------//
                 default:
                 begin
                     fifo_shift_out <= 1'b0;
                 end
             endcase
 
             // Egress Byte Datapath
             //------------
             //egress_bit_counter <= egress_bit_counter + 2 ;
             if (state!=WAIT )
             begin
                 egress_bit_counter <= egress_bit_counter + 2 ;
             end
 
             casex ({egress_bit_counter,state})
                 // If CPOL = 1, the first valid clock is negedge, then this first posedge is valid
                 // If CPOL = 0, the first valid clock is posedge, then we need a wait state to let our counterpart sample on negedge
                 {8'd0,WAIT}:
                 begin
                     egress_byte <= IDLE_VALUE;
                 end
                 {8'd6,IDLE}:
                 begin
            
 
                     if (fifo_empty)
                     begin
                         egress_byte <= IDLE_VALUE;
                     end
                     else
                     begin
                         egress_byte <= fifo_data;
                     end
                 end
                 {8'd6,DATA}:
                 begin
                     if (!fifo_empty)
                     begin
                        egress_byte        <= fifo_data;
                     end
                     else
                     begin
                         egress_byte        <= IDLE_VALUE;
                     end
 
 
 
                 end
                 //-------------//
                 default:
                 begin
                     egress_byte <= {2'b0,egress_byte[7:2]};
                 end
             endcase
 
 
 
         end
 
     end
 endmodule