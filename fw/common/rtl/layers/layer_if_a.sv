

module layer_if_a  #(LAYER_ID = 0)(
   
    input  wire				clk_core,
    input  wire				clk_core_resn,
    input  wire				clk_spi,
    input  wire				clk_spi_resn,

    output wire [7:0]		frames_m_axis_tdata,
    output wire [7:0]		frames_m_axis_tdest,
    output wire				frames_m_axis_tlast,
    input  wire				frames_m_axis_tready,
    output wire				frames_m_axis_tvalid,
    input  wire				interruptn, // Should be synced in core clock domain at a higher level

    input  wire [7:0]		mosi_s_axis_tdata,
    input  wire				mosi_s_axis_tlast,
    output wire				mosi_s_axis_tready,
    input  wire				mosi_s_axis_tvalid,
    output wire [31:0]      mosi_s_write_size,

    output wire				spi_clk,
    output wire				spi_csn,
    input  wire [1:0]		spi_miso,
    output wire				spi_mosi,

    input  wire             cfg_disable_autoread,
    input  wire [31:0]		cfg_frame_tag_counter,
    input  wire [7:0]		cfg_nodata_continue,
    input  wire             cfg_layer_reset,
    input  wire             cfg_disable_miso,

    output wire             status_frame_decoding,

    output wire				stat_frame_detected,
    output wire				stat_idle_detected,
    output wire             stat_wronglength_detected
);


    // Connections
    //----------------
    wire cfg_layer_resetn = !cfg_layer_reset;

    wire spi_io_enable; // size=1
    wire mosi_fifo_m_axis_tvalid; // size=1
    wire mosi_fifo_m_axis_tready; // size=1
    wire [7:0] mosi_fifo_m_axis_tdata; // size=8
    wire [7:0] spi_io_m_axis_tdata; // size=8
    wire spi_io_m_axis_tvalid; // size=1
    wire spi_io_m_axis_tready; // size=1
    wire miso_fifo_m_axis_tvalid; // size=1
    wire miso_fifo_m_axis_tready; // size=1
    wire [7:0] miso_fifo_m_axis_tdata; // size=8 

    // Sections
    //---------------


    // Instances
    //------------
        

    fifo_axis_2clk_spi_layer  mosi_fifo(
        .m_axis_aclk(clk_spi),
        .m_axis_tdata(mosi_fifo_m_axis_tdata),
        .m_axis_tlast(/* WAIVED: Last not used by SPI Output */),
        .m_axis_tready(mosi_fifo_m_axis_tready),
        .m_axis_tvalid(mosi_fifo_m_axis_tvalid),
        .axis_rd_data_count(/* unused */),
        .s_axis_aclk(clk_core),
        .s_axis_aresetn(clk_core_resn),
        .axis_wr_data_count(mosi_s_write_size),
        .s_axis_tdata(mosi_s_axis_tdata),
        .s_axis_tlast(mosi_s_axis_tlast),
        .s_axis_tready(mosi_s_axis_tready),
        .s_axis_tvalid(mosi_s_axis_tvalid)
    );
            
    spi_axis_if_v1 #(.QSPI(1),.MSB_FIRST(0),.CLOCK_OUT_CG(1)) spi_io(
        .clk(clk_spi),
        .enable(spi_io_enable),
        .m_axis_tdata(spi_io_m_axis_tdata),
        .m_axis_tready(spi_io_m_axis_tready | cfg_disable_miso),
        .m_axis_tvalid(spi_io_m_axis_tvalid),
        .resn(clk_spi_resn && cfg_layer_resetn),
        .s_axis_tdata(mosi_fifo_m_axis_tdata),
        .s_axis_tready(mosi_fifo_m_axis_tready),
        .s_axis_tvalid(mosi_fifo_m_axis_tvalid),
        .spi_clk(spi_clk),
        .spi_csn(spi_csn),
        .spi_miso(spi_miso),
        .spi_mosi(spi_mosi)
    );
            
    fifo_axis_2clk_spi_layer  miso_fifo(
        .m_axis_aclk(clk_core),
        .m_axis_tdata(miso_fifo_m_axis_tdata),
        .m_axis_tready(miso_fifo_m_axis_tready),
        .m_axis_tvalid(miso_fifo_m_axis_tvalid),
        .m_axis_tlast(/* WAIVED: Last not used by SPI Output */),
        .axis_rd_data_count(/* unused */),
        .s_axis_aclk(clk_spi),
        .s_axis_aresetn(clk_spi_resn && cfg_layer_resetn),
        .s_axis_tdata(spi_io_m_axis_tdata),
        .s_axis_tready(spi_io_m_axis_tready),
        .s_axis_tvalid(spi_io_m_axis_tvalid & !cfg_disable_miso),
        .s_axis_tlast(1'b1),
        .axis_wr_data_count(/*unused*/)
    );
            
    astropix_spi_protocol_av1 #(.LAYER_ID(LAYER_ID)) protocol(
        .clk(clk_core),
        .resn(clk_core_resn),

        .enable(/* WAIVED: Not implemented yet */),
        .interruptn(interruptn),
        
        .m_axis_tdata(frames_m_axis_tdata),
        .m_axis_tdest(frames_m_axis_tdest),
        .m_axis_tlast(frames_m_axis_tlast),
        .m_axis_tready(frames_m_axis_tready),
        .m_axis_tvalid(frames_m_axis_tvalid),

        .readout_active(spi_io_enable),
        
        .s_axis_tdata(miso_fifo_m_axis_tdata),
        .s_axis_tready(miso_fifo_m_axis_tready),
        .s_axis_tvalid(miso_fifo_m_axis_tvalid),
        
        .cfg_frame_tag_counter(cfg_frame_tag_counter),
        .cfg_nodata_continue(cfg_nodata_continue),
        .cfg_disable_autoread(cfg_disable_autoread),
        .cfg_layer_reset(cfg_layer_reset),
        .status_frame_decoding(status_frame_decoding),
        .stat_frame_detected(stat_frame_detected),
        .stat_idle_detected(stat_idle_detected),
        .stat_wronglength_detected(stat_wronglength_detected)
    );


endmodule