

module edge_detect #(
    DELAY_LENGTH = 4
) (

    input wire clk,
    input wire resn,
    input wire in,
    output logic rising_edge,
    output logic falling_edge
);

    reg [DELAY_LENGTH-1:0] in_del;

    assign rising_edge = in_del[DELAY_LENGTH-1] == 'd0 && in_del[DELAY_LENGTH-2] == 'd1;
    assign falling_edge = in_del[DELAY_LENGTH-1] == 'd1 && in_del[DELAY_LENGTH-2] == 'd0;
    
    always@(posedge clk) begin
        if (!resn) begin 
            in_del <= {DELAY_LENGTH{1'b0}};
            //rising_edge <= 'b0;
           // falling_edge <= 'b0;
        end else begin 
            in_del <= {in_del[DELAY_LENGTH-2:0],in};
            
           // rising_edge <= in_del[DELAY_LENGTH-1] == 0 && in_del[DELAY_LENGTH-2] == 1 ;
            //falling_edge <= in_del[DELAY_LENGTH-1] == 1 && in_del[DELAY_LENGTH-2] == 0 ;

        end
        
    end

endmodule