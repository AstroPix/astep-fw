


/*
    Generated by HDL Build
*/
module ext_dac_driver(
    input  wire				clk_core,
    input  wire				clk_core_resn,
    input  wire				clk_spi,
    input  wire				clk_spi_resn,
    input  wire [7:0]		ext_dac_mosi_s_axis_tdata,
    input  wire				ext_dac_mosi_s_axis_tlast,
    output wire				ext_dac_mosi_s_axis_tready,
    input  wire				ext_dac_mosi_s_axis_tvalid,
    output wire				ext_dac_spi_clk,
    output wire				ext_dac_spi_csn,
    output wire				ext_dac_spi_mosi
);

    // Connections
    //----------------
    wire mosi_fifo_m_axis_tvalid; // size=1
    wire mosi_fifo_m_axis_tready; // size=1
    wire [7:0] mosi_fifo_m_axis_tdata; // size=8 

    // Sections
    //---------------


    // Instances
    //------------
        
    // Module Instance
    fifo_axis_2clk_spi_hk  mosi_fifo(
        .axis_rd_data_count(/*No Connection*/),
        .m_axis_aclk(clk_spi),
        .m_axis_tdata(mosi_fifo_m_axis_tdata),
        .m_axis_tlast(/*unused*/),
        .m_axis_tready(mosi_fifo_m_axis_tready),
        .m_axis_tvalid(mosi_fifo_m_axis_tvalid),
        .s_axis_aclk(clk_core),
        .s_axis_aresetn(clk_core_resn),
        .axis_wr_data_count(),
        .s_axis_tdata(ext_dac_mosi_s_axis_tdata),
        .s_axis_tlast(ext_dac_mosi_s_axis_tlast),
        .s_axis_tready(ext_dac_mosi_s_axis_tready),
        .s_axis_tvalid(ext_dac_mosi_s_axis_tvalid)
    );
            
    
    // Module Instance
    spi_axis_if_v1 #(.QSPI(0),.MSB_FIRST(0),.CLOCK_OUT_CG(1'b1)) spi_io(
        .clk(clk_spi),
        .enable(1'd0),
        .m_axis_tdata(/* WAIVED: Master Input not used, no readout from DAC */),
        .m_axis_tready(1'd0),
        .m_axis_tvalid(/* WAIVED: Master Input not used, no readout from DAC */),
        .resn(clk_spi_resn),
        .s_axis_tdata(mosi_fifo_m_axis_tdata),
        .s_axis_tready(mosi_fifo_m_axis_tready),
        .s_axis_tvalid(mosi_fifo_m_axis_tvalid),
        .spi_clk(ext_dac_spi_clk),
        .spi_csn(ext_dac_spi_csn),
        .spi_miso(/* WAIVED: Master Input not used, no readout from DAC */),
        .spi_mosi(ext_dac_spi_mosi)
    );
                

endmodule

        
