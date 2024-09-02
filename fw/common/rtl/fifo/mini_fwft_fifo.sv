module mini_fwft_fifo #(parameter AWIDTH = 2,parameter DWIDTH=8) (
    input wire clk, 
    input wire resn,

    output reg full, 
    output reg almost_full,
    output reg empty, 
    output reg almost_empty,

    input wire write,
    input wire read,

    input  wire [DWIDTH-1:0] data_in,
    output reg [DWIDTH-1:0] data_out

);


     // Pointer Logic
    //----------
    wire reading,writing;
    wire [AWIDTH-1:0] write_pointer, read_pointer;

    fifo_ptr_logic # (
        .AWIDTH(AWIDTH)
    )
    fifo_ptr_logic_inst (
        .clk(clk),
        .resn(resn),
        .shift_in(write),
        .shift_out(read),
        .full(full),
        .almost_full(almost_full),
        .empty(empty),
        .almost_empty(almost_empty),
        .reading(reading),
        .writing(writing),
        .write_pointer(write_pointer),
        .read_pointer(read_pointer)
    );

    // Data Path
    //-------------
    reg [DWIDTH-1:0] mem [2**AWIDTH];

    wire write_in_to_out = (writing && empty) || (writing && reading && almost_empty);

    always @(posedge clk) begin
        if (!resn) begin
            
        end else begin
            
            // Mem write
            //---------------
            if (writing && !write_in_to_out) begin
                mem[write_pointer - 1'b1] <= data_in;
            end

            // Data out
            //-----------------
            if (write_in_to_out) begin
                data_out            <= data_in;
            end
            else if (reading && !write_in_to_out) begin
                data_out <= mem[read_pointer];
            end
            
        end
    end


endmodule