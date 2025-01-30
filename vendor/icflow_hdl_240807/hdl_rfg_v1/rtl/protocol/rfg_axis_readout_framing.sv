module rfg_axis_readout_framing #(
    parameter MTU_SIZE      = 16,
    parameter IDLE_BYTE     = 8'hBC,
    parameter START_BYTE    = 8'hEF
) (

    input wire          clk,
    input wire          resn, 

    // Slave Receives Data and transfers the size
    //------------
    input  wire [7:0]           s_axis_tdata,
    input  wire                 s_axis_tvalid,
    input  wire                 s_axis_tlast,
    output reg                  s_axis_tready,
    // TUser Byte is used as placeholder if no data is available to be send
    //nput  wire [MTU_SIZE-1:0]  s_axis_tuser,
    input  wire [7:0]           s_axis_tid, // Used as Frame delimiter to indicate the vchannel

    // Master interface transfers to Egress
    output reg  [7:0]           m_axis_tdata,
    output reg                  m_axis_tvalid,
    input  wire                 m_axis_tready,
    output wire  [7:0]          m_axis_tuser
);

    assign m_axis_tuser = IDLE_BYTE; 

    enum {IDLE,START,DATA} state;

    wire slave_byte_valid   = s_axis_tready && s_axis_tvalid;
    wire master_byte_valid  = m_axis_tvalid && m_axis_tready;

    reg [7:0] buffer;
    reg       end_of_frame;

    always@(posedge clk or negedge resn) begin 
        if (!resn) begin
            s_axis_tready <= 1'b0;
            m_axis_tvalid <= 1'b0;
            state         <= IDLE;
            end_of_frame  <= 1'b0;
        end
        else begin 

            

            // Wait for data, once a frame is coming, it should be continuous
            case(state)
                IDLE: begin
                    
                    if (slave_byte_valid) begin 
                        state           <= START;

                        m_axis_tvalid   <= 1'b1;
                        m_axis_tdata    <= s_axis_tid;
                        buffer          <= s_axis_tdata;

                        end_of_frame    <= s_axis_tlast;
                        s_axis_tready   <= 1'b0;
                        
                    end
                    else begin
                        s_axis_tready   <= 1'b1;  
                        end_of_frame    <= 0;
                    end
                end
                START: begin 
                    

                    m_axis_tvalid   <= 1'b1;
                    s_axis_tready   <= 1'b0;

                    if (master_byte_valid) begin 
                        state           <= DATA;
                        m_axis_tdata    <= buffer;
                        s_axis_tready   <= 1'b0;
                    end
                end
                DATA: begin 

                    m_axis_tvalid   <= 1'b1; 
                    
                    if (master_byte_valid) begin 
                        m_axis_tdata    <= s_axis_tdata;
                        s_axis_tready   <= 1'b1;
                        end_of_frame    <= s_axis_tlast;

                        if (end_of_frame) begin 
                            s_axis_tready   <= 1'b0;
                            m_axis_tvalid   <= 1'b0;
                            end_of_frame    <= 1'b0;
                            state           <= IDLE;
                        end

                    end
                    else begin 
                        s_axis_tready   <= 1'b0;
                    end

                    
                end
            endcase
        end
    end

endmodule