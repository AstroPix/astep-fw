module loopback_spi_if(

    input wire clk_core,
    input wire clk_core_resn,

    input wire spi_clk,
    input wire spi_clk_resn,

    input  wire          spi_io_clk,
    input  wire          spi_mosi,
    output wire [1:0]    spi_miso,
    input  wire          spi_csn,

    // AXIS Slave is for MISO path
    input  wire [7:0]		miso_s_axis_tdata,
    output wire				miso_s_axis_tready,
    input  wire				miso_s_axis_tvalid,
    output wire [31:0]      miso_s_write_size,


    // AXIS Master is the receive path, MOSI
    output  wire [7:0]      mosi_m_axis_tdata,
    input   wire            mosi_m_axis_tready,
    output  wire            mosi_m_axis_tvalid,
    output  wire [31:0]     mosi_m_read_size
);



    // IGRESS
    //-------------------
    wire [7:0]  igress_m_tdata;
    wire        igress_m_tready;
    wire        igress_m_tvalid;

    //-- SPI
    spi_slave_axis_igress #(.MSB_FIRST(0)) spi_igress(
            .spi_clk(spi_io_clk),
            .spi_csn(spi_csn),
            .spi_mosi(spi_mosi),

            .m_axis_tdata(igress_m_tdata),
            .m_axis_tdest(),
            .m_axis_tid(),
            .m_axis_tready(igress_m_tready),
            .m_axis_tvalid(igress_m_tvalid),

            .err_overrun(/* WAIVED: Overrun not relevant when CS not used */)
        );    

    //-- FIFO 
    fifo_axis_2clk_spi_loopback  spi_igress_fifo(
        
        .s_axis_aclk(spi_clk),
        .s_axis_aresetn(spi_clk_resn),

        .s_axis_tdata(igress_m_tdata),
        .s_axis_tready(igress_m_tready),
        .s_axis_tvalid(igress_m_tvalid),

        .m_axis_aclk(clk_core),
        .m_axis_tready (mosi_m_axis_tready),
        .m_axis_tvalid (mosi_m_axis_tvalid),
        .m_axis_tdata (mosi_m_axis_tdata),
  
        .axis_wr_data_count(),
        .axis_rd_data_count(mosi_m_read_size)
    );

    // EGRESS (MISO)
    //-------------------
    wire [7:0] egress_m_data;
    wire egress_m_tready;
    wire egress_m_tvalid;

    //-- FIFO
    fifo_axis_2clk_spi_loopback  miso_fifo (
        .s_axis_aclk(clk_core),
        .s_axis_aresetn(clk_core_resn),

        .s_axis_tdata(miso_s_axis_tdata),
        .s_axis_tready(miso_s_axis_tready),
        .s_axis_tvalid(miso_s_axis_tvalid),


        .m_axis_aclk(spi_clk),

        .m_axis_tdata(egress_m_data),
        .m_axis_tready(egress_m_tready),
        .m_axis_tvalid(egress_m_tvalid),


        .axis_wr_data_count(miso_s_write_size),
        .axis_rd_data_count(/* unused */)
        
    );

    //-- SPI
    spi_slave_axis_egress #(.ASYNC_RES(1),.MSB_FIRST(0),.MISO_SIZE(2)) spi_egress(
       
        .spi_clk(spi_io_clk),
        .spi_csn(spi_csn),
        .spi_miso(spi_miso),

        .s_axis_tdata(egress_m_data),
        .s_axis_tready(egress_m_tready),
        .s_axis_tuser(8'h3D),
        .s_axis_tvalid(egress_m_tvalid)

    );



endmodule 