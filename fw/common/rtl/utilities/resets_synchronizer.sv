
/**
This module synchronises input resets request into clock domains and produces long enough reset strain for all modules to initialise
The long reset sequence is useful when using FIFO blocks which sometimes need a while to properly reset

The Module's master clock is a managing always running clock that can monitor the state of the resets
This is used for example if one wants to implement a shutdown resets which will first reset all clock domains, then shutdown clocks

*/
module resets_synchronizer #(parameter CLOCKS = 2 , parameter RESET_DELAY = 5  )(



    input wire                  async_resn_in,
    input wire [CLOCKS-1:0]     input_clocks,

    output wire [CLOCKS-1:0]    output_resn,
    output reg                  master_all_reset

);

    // Synchronise and generate all resets
    wire master_clk = input_clocks[0];

    wire [CLOCKS-1:0] synced_resn_in;
    wire [CLOCKS-2:0] master_synced_resn_out;

    genvar i;
    generate
        for (i = 0 ; i < CLOCKS ; i++) begin

            // First Synchronise asynchronous reset in the clock domain
            // This helps avoiding methodology warnings on FGPA
            //async_signal_sync  reset_signal_sync(.clk(input_clocks[i]),.async_input(async_resn_in),.sync_out(synced_resn_in[i]));

            // Now Generate reset in clock domain
            //reset_sync
            // #(.RESET_DELAY(RESET_DELAY))  reset_generator (.clk(input_clocks[i]),.resn_in(synced_resn_in[i]),.resn_out(output_resn[i]));
            //


            reset_sync #(.RESET_DELAY(RESET_DELAY))  reset_generator (.clk(input_clocks[i]),.resn_in(async_resn_in),.resn_out(output_resn[i]));


            /*if (i>0) begin
                async_signal_sync  master_reset_output_synchroniser(.clk(master_clk),.async_input(output_resn[i-1]),.sync_out(master_synced_resn_out[i-1]));
            end*/


        end

    endgenerate

    always @(posedge master_clk /*or negedge async_resn_in*/) begin
        /*if (!async_resn_in) begin
            master_all_reset <= 'b1;
        end
        else begin*/
            master_all_reset <= (|{master_synced_resn_out,output_resn[0]} == 0);
            //end

    end


endmodule
