
/**
    @require spi_slave_egress.sv
    @require spi_slave_igress.sv
    @require astropix3_asic_model_frame_generator.sv
    @require ../../ipsrc/definitions/asic_model_frame_fifo/asic_model_frame_fifo.xci
    @require ${HDLBUILDV1_HOME}/svlib/sync/edge_detect.sv
*/
module astropix3_asic_model(

    // Model Control
    input  wire [15:0]  gen_ctrl_frame_count,
    input  wire         gen_ctrl_frame_enable, 
    
    input wire          clk,
    input wire          resn,

    // SPI
    input  wire         spi_csn, 
    input  wire         spi_clk,
    input  wire         spi_mosi,
    output wire [1:0]   spi_miso,
    output reg          interruptn,

    // SR
    input  wire         sr_ck1,
    input  wire         sr_ck2,
    input  wire         sr_ld,
    input  wire         sr_rb,
    input  wire         sr_sin,
    output wire         sr_sout


);


    // SPI Igress
    //-------------
    wire        igress_header;
    wire        igress_data;
    wire [7:0]  igress_byte;
    spi_slave_igress spi_igress(
        .resn(resn),
        .spi_csn(spi_csn), 
        .spi_clk(spi_clk),
        .spi_mosi(spi_mosi),
        .reset_to_header(1'b0),
        .out_rcv_byte(igress_byte),
        .out_header(igress_header),
        .out_data(igress_data),
        .out_header_cmd(),
        .out_header_parameters()
    ); 

    // SPI Egress
    //----------------
    wire        egress_spi_empty;
    wire        egress_spi_read;
    wire [7:0]  egress_spi_data;

    wire         egress_frame_write;
    wire [7:0]   egress_frame_data;
    wire        egress_frame_full;

    // Interrupt -> Trigger on Frame Fifo write
    //           -> Reset on empty signal
    wire egress_spi_empty_rising;
    edge_detect egress_empty_edge(
        .clk(clk),
        .resn(resn),
        .in(egress_spi_empty),
        .rising_edge(egress_spi_empty_rising),
        .falling_edge()
    );

    always @(posedge clk /*or posedge egress_spi_empty or negedge resn*/) begin 
        if ( !resn || egress_spi_empty_rising) begin 
            interruptn <= 1'b1;
        end else if (egress_frame_write && interruptn ) begin 
            interruptn <= 1'b0;
        end
    end

    /*reg readreset;
    always @(posedge clk or  negedge resn) begin 
        if ( !resn ) begin 
            readreset <= 1'b0;
        end else begin 
            readreset <= !resn;
        end
    end*/

    asic_model_frame_fifo egress_frame_fifo (
        .wr_clk(clk),      // 
        .wr_rst(!resn),    //
        .din(egress_frame_data),      // 
        .wr_en(egress_frame_write),  //
        .full(egress_frame_full),    // 
        .rd_clk(spi_clk),
        .rd_rst(!resn),
        .rd_en(egress_spi_read),  // 
        .dout(egress_spi_data),    // 
        .empty(egress_spi_empty)  //
    );

    //reg fifo_out
    spi_slave_egress spi_egress(
        .resn(resn),
        .spi_csn(spi_csn), 
        .spi_clk(spi_clk),
        .spi_miso(spi_miso),
        .fifo_empty(egress_spi_empty),
        .fifo_shift_out(egress_spi_read),
        .fifo_data(egress_spi_data)
    ); 

    // Handle Protocol
    //-------------------
    astropix3_asic_model_frame_generator  frame_generator (
        .clk(clk),
        .resn(resn),
        .igress_byte(igress_byte),
        .igress_header(igress_header),
        .igress_data(igress_data),
        .egress_frame_write(egress_frame_write),
        .egress_frame_data(egress_frame_data),
        .egress_frame_full(egress_frame_full),
        .config_generate_interrupt(1'b0),
        .gen_ctrl_frame_count(gen_ctrl_frame_count),
        .gen_ctrl_frame_enable(gen_ctrl_frame_enable)
  );
   
endmodule 