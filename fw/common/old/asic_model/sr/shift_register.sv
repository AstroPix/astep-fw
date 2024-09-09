
/**
 * Simple Model for Dual Latch Config Bit
 *
 * SIN -> LATCH.CK1 -> LATCH.CK2 -> LATCH.LOAD -> q
 *                               -> SOUT
 */
 module SRBit(

    input   wire    res_n,
   
    input   wire    ck1,
    input   wire    ck2,
    input   wire    sin,
    input   wire    load,
    output  wire    sout,
    output  reg     q,
    output  reg     qn

);

    reg latchCK1;
    reg latchCK2;

    assign SOUT = latchCK2;

    // LATCH on CK1
    always @(posedge ck1 or negedge res_n) begin
        if (!res_n) begin
            latchCK1 <= 1'b0;
        end else begin
            latchCK1 <= sin;
        end
    end

    // LATCH on CK2
    always @(posedge ck2 or negedge res_n) begin
        if (!res_n) begin
            latchCK2 <= 1'b0;
        end else begin
            latchCK2 <= latchCK1;
        end

    end

    // LATCH on LOAD
    always @(posedge load or negedge res_n) begin
        if (!res_n) begin
            q  <= 1'b0;
            qn <= 1'b1;
        end else begin
            q  <= latchCK2;
            qn <= ! latchCK2;
        end

    end
endmodule

module shift_register #(parameter BITS=2)(

        input   wire            res_n,
        
        input   wire            ck1,
        input   wire            ck2,
        input   wire            sin,
        input   wire            ld,
        output  wire            sout,
        output  wire [BITS-1:0] q,
        output  wire [BITS-1:0] qn

    );

    wire [BITS:0] Sin_Sout;

    assign Sin_Sout[0] = sin;

    generate
        genvar i;

        for (i=1;i<=(BITS);i++)
        begin

            SRBit bit_I (
                .res_n (res_n),
                .ck1   (ck1           ),
                .ck2   (ck2           ),
                .sin   (Sin_Sout[i-1]),
                .ld    (ld),
                .sout  (Sin_Sout[i]  ),
                .q     (Q[i-1]       ),
                .qn    (QN[i-1]      )
            );
        end
    endgenerate



endmodule