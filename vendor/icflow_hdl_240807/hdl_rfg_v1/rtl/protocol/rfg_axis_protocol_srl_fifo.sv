module rfg_axis_protocol_srl_fifo #(parameter AWIDTH = 2) (
    input wire clk, 
    input wire resn,

    output reg full, 
    output reg almost_full,
    output reg empty, 
    output reg almost_empty,

    input wire write,
    input wire read,

    input  wire [7:0] write_value,
    output wire [7:0] read_value

);


    reg [AWIDTH-1:0] wptr;
    reg [AWIDTH-1:0] rptr;
    
    reg [7:0] mem [AWIDTH**2];

    assign read_value = mem[rptr];
    
    wire [AWIDTH-1:0] rptr_next = (rptr + 1);
    wire [AWIDTH-1:0] rptr_next_2 = (rptr + 2);
    wire [AWIDTH-1:0] wptr_next = (wptr + 1);
    wire [AWIDTH-1:0] wptr_next_2 = (wptr + 2);
    wire wptr_next_is_read = wptr_next == (rptr);
    wire wptr_next2_is_read = wptr_next_2 == (rptr);
    always@(posedge clk) begin 
        if (!resn) begin 
            wptr <= {AWIDTH{1'b0}};
            rptr <= {AWIDTH{1'b0}};
            empty <= 1'b1;
            full  <= 1'b0;
            almost_full <= 1'b0;
            almost_empty <= 1'b1;
        end
        else begin

            // Write
            if (write && !full) begin 
                mem[wptr] = write_value;
                wptr <= wptr + 1;
            end

            // Read 
            if (read && !empty) begin 
                rptr <= rptr+1;
            end

            // Full
            if (write && !full && !read && wptr_next_is_read ) begin 
                full <= 1'b1;
            end
            else if (read) begin 
                full <= 1'b0;
            end

            // AFull
            if (write && !full && wptr_next2_is_read && !read ) begin 
                almost_full <= 1'b1;
            end
            else if (read && !write &&  wptr_next_is_read ) begin 
                almost_full <= 1'b0;
            end

            // Empty 
            if (read && !empty && rptr_next==wptr && !write) begin 
                empty <= 1'b1;
            end
            else if (write) begin 
                empty <= 1'b0;
            end

            // A Empty
            if (read && !empty && rptr_next_2==wptr && !write) begin 
                almost_empty <= 1'b1;
            end
            else if (write && !read && rptr_next==wptr) begin 
                almost_empty <= 1'b0;
            end
            


        end
    end


endmodule