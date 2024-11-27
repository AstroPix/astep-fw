
/**

    This module allows writing as Master to another clock domain which should be faster

    @require  ${HDLBUILDV1_HOME}/svlib/sync/edge_detect.sv
     
*/
module spi_slave_axis_igress_to_clk #( 
    parameter DEST_WIDTH    = 8,
    parameter ID_WIDTH      = 8
   ) (

  
    input wire                          clk,
    input wire                          resn,

    // AXIS Slave
    input  wire [7:0]                   s_axis_tdata,
    input  wire                         s_axis_tvalid,
    output reg                          s_axis_tready,
    input  wire [DEST_WIDTH-1:0]        s_axis_tdest,
    input  wire [ID_WIDTH-1:0]          s_axis_tid,

    // AXIS Master
    output reg  [7:0]                   m_axis_tdata,
    output reg                          m_axis_tvalid,
    input  wire                         m_axis_tready,
    output reg [DEST_WIDTH-1:0]         m_axis_tdest,
    output reg [ID_WIDTH-1:0]           m_axis_tid


);

    // Detect edge of slave tvalid
    wire slave_valid_rising;
    wire slave_valid_falling;
    edge_detect slave_valid_edge(
        .clk(clk),
        .resn(resn),
        .in(s_axis_tvalid),
        .rising_edge(slave_valid_rising),
        .falling_edge(slave_valid_falling)
    );

    always@(posedge clk) begin 
        if (!resn) begin 
            s_axis_tready     <= 1'b1;
            m_axis_tvalid     <= 1'b0;
        end else begin 

            if (slave_valid_rising) begin
                m_axis_tvalid <= 1'b1;
                m_axis_tdata  <= s_axis_tdata;
                m_axis_tdest  <= s_axis_tdest;
                m_axis_tid    <= s_axis_tid;
            end
            else begin 
                m_axis_tvalid <= 1'b0;
            end
            
        end

    end


endmodule