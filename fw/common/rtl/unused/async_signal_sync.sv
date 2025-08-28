
module async_signal_sync #(
    parameter RESET_VALUE = 1'b0, 
    parameter DEBOUNCE_DELAY = 2) (
    input wire clk, 
    input wire async_input,
    output reg sync_out
);


    reg [DEBOUNCE_DELAY-1:0] delay_debounce;
    always@(posedge clk) begin 
        
        delay_debounce <= {delay_debounce[DEBOUNCE_DELAY-2:0],async_input};
        if ((&delay_debounce == 1) || (|delay_debounce==0) )
            sync_out <= delay_debounce[DEBOUNCE_DELAY-1];
     
    end

endmodule 