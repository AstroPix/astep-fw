`include "axi_ifs.sv"
module astropix3_asic_model_frame_generator(

    input wire          clk,
    input wire          resn,

    input wire          config_generate_interrupt,

     // Model Control
    input  wire [15:0]  gen_ctrl_frame_count,
    input  wire         gen_ctrl_frame_enable, 

    input wire  [7:0]   igress_byte,
    input wire          igress_header,
    input wire          igress_data,

    output reg          egress_frame_write,
    output reg [7:0]    egress_frame_data,
    input  wire         egress_frame_full


);

    localparam CHIP_ID = 5'h1;
    enum reg [7:0]  {
        CMD_FRAME_COUNTER = 8'hAB
    } commands;

    enum {FG_IDLE,  FG_HEADER,  FG_DATA }   state;
    enum {FT_NONE,  FT_COUNTER }            frame_type;

    // Frame out signals
    wire egress_byte_valid = !egress_frame_full && egress_frame_write;

    // Detect Edges to trigger events
    //------------------
    wire gen_ctrl_frame_enable_rising;
    edge_detect gen_enable_edge(
        .clk(clk),
        .resn(resn),
        .in(gen_ctrl_frame_enable),
        .rising_edge(gen_ctrl_frame_enable_rising),
        .falling_edge()
    );

    // Frame Control
    //-------------
    byte_t frame_current_byte;
  

    // Frame: Counter
    //--------------------
    byte_t frame_counter_cnt; // Counter for the Counter frame handler
    word_t frame_counter_limit;

  

    // Process
    //---------------
    always @(posedge clk  or negedge resn) begin
        if (!resn) begin
            state               <= FG_IDLE;
            frame_type          <= FT_NONE;

            egress_frame_write  <= 1'b0;

            frame_current_byte  <= 0;

            frame_counter_cnt   <= 0;
            frame_counter_limit <= 0;

            //interruptn          <= 1'b1;

            
        end
        else begin 


            // State
            case (state)
                FG_IDLE: begin 
                    frame_current_byte <= 0;
                    if (gen_ctrl_frame_enable_rising) begin 
                        state               <= FG_HEADER;
                        frame_type          <= FT_COUNTER;

                        frame_counter_limit <= gen_ctrl_frame_count;

                    end else if ((igress_header && igress_byte==CMD_FRAME_COUNTER)) begin 
                        state               <= FG_HEADER;
                        frame_type          <= FT_COUNTER;

                        frame_counter_limit <= gen_ctrl_frame_count;
                    end
                    

                end
                FG_HEADER: begin 
                    egress_frame_write <= 1'b1;
                    if (egress_byte_valid) begin 
                        state <= FG_DATA;
                        frame_current_byte <= frame_current_byte+1;
                    end
                end
                FG_DATA: begin 
                    if (egress_byte_valid) begin 
                        frame_current_byte <= frame_current_byte+1;
                    end

                    // Finalize frame
                    if (frame_type==FT_COUNTER && egress_byte_valid && frame_current_byte==(frame_counter_limit-1)) begin 
                        state       <= FG_IDLE;
                        egress_frame_write <= 1'b0;
                    end
                end
                
            endcase

            // Data
            case ({frame_type,state})
                
                {FT_COUNTER,FG_HEADER}: begin 
                    
                    egress_frame_data  <= {CHIP_ID,frame_counter_limit[2:0]};
                    if (egress_byte_valid) begin 
                        egress_frame_data <= frame_counter_cnt;
                        frame_counter_cnt <= frame_counter_cnt+1;
                    end
                end
                {FT_COUNTER,FG_DATA}: begin 
                   
                    if (egress_byte_valid) begin 
                        
                        egress_frame_data <= frame_counter_cnt;
                    end

                    if (egress_byte_valid && frame_current_byte<=frame_counter_limit)begin 
                        frame_counter_cnt <= frame_counter_cnt +1;
                    end
                    

                end
                default: begin 
                    egress_frame_write <= 1'b0;
                end
            endcase

        end
    end



endmodule 