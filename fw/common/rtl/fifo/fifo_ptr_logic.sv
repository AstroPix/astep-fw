module fifo_ptr_logic #(parameter AWIDTH=8) (

    input wire      clk,
    input wire      resn,

    input   wire    shift_in,
    input   wire    shift_out,

    output  reg     full,
    output  reg     almost_full,
    output  reg     empty,
    output  reg     almost_empty,

    output reg [AWIDTH-1:0] write_pointer,
    output reg [AWIDTH-1:0] read_pointer,

    // Helpers for datapath
    output wire     reading,
    output wire     writing
);

    // Pointers
    //------------

    //reg [AWIDTH-1:0] write_pointer;
    //reg [AWIDTH-1:0] read_pointer;
    //reg [AWIDTH-1:0] read_pointer_next;

    wire [AWIDTH-1:0] read_pointer_plus_one = (read_pointer + 1'd1);
    wire [AWIDTH-1:0] read_pointer_plus_two = (read_pointer + 2'd2);

    wire [AWIDTH-1:0] write_pointer_plus_one = (write_pointer + 1'd1);
    wire [AWIDTH-1:0] write_pointer_plus_two = (write_pointer + 2'd2);

    // Helper Signals
    //-----------
    assign reading = shift_out && !empty;
	assign writing = shift_in && !full;

    always @(posedge clk) begin
        if (!resn) begin
            // reset
			full <= 0;
			almost_full <= 0;
			empty <= 1;
			almost_empty <= 1;
			//data_out <= {DWIDTH{1'b0}};
			write_pointer <= {AWIDTH{1'b0}};
			read_pointer <= {AWIDTH{1'b0}}; 
        end
        else begin
            
			// Read
			//-------
            
            // Increment if reading and not on last word, otherwise read might overtake write && !(almost_empty && !writing)
            if (reading) begin
				read_pointer <= read_pointer + 1'b1;
			end

			// Write
			//--------
			if (writing) begin
				write_pointer <= write_pointer+ 1'b1;
			end

			// Full
			//---------
			if (writing && !reading &&    write_pointer_plus_one == read_pointer) begin
				full <= 1'b1;
			end
			else if (reading && full) begin 
				full <= 1'b0;
			end 

			// Almost Full
			//---------
			if (writing && !reading &&  write_pointer_plus_two == read_pointer) begin
				almost_full <= 1'b1;
			end
			else if (reading && !writing && !full) begin 
				almost_full <= 1'b0;
			end 

			// Empty
			//---------
			if (reading && !writing && read_pointer_plus_one ==write_pointer) begin 
				empty <= 1'b1;
			end
			else if (writing && empty) begin 
				empty <= 1'b0;
			end

			// Almost Empty
			//---------
			if (reading && !writing &&  read_pointer_plus_two == write_pointer) begin
				almost_empty <= 1'b1;
			end
			else if (writing && !reading && !empty) begin 
				almost_empty <= 1'b0;
			end 

        end
    end


endmodule