


/*
ASTEP 3Layers Top level
*/
module astep24_3l_top(

    input  wire				sysclk,
    input  wire             clk_ext,
    input  wire				resn,

    output wire             clk_ext_selected,
    output wire				clk_sample,
    output wire				clk_sample_ap4,
    output wire				clk_timestamp,
    output wire				clk_timestamp_ap4,
    
    output wire             sysclk_40M, // 40M clock derived from Board Clock

    output wire             clk_core,
    output wire             clk_core_resn,


    output wire				ext_adc_spi_csn,
    input  wire				ext_adc_spi_miso,
    output wire				ext_dac_spi_csn,
    output wire				ext_spi_clk,
    output wire				ext_spi_mosi,
    output wire				io_aresn,

    output wire				layer_0_hold,
    input  wire				layer_0_interruptn,
    output wire				layer_0_resn,
    output wire				layer_0_spi_clk,
    output wire				layer_0_spi_csn,
    input  wire [1:0]		layer_0_spi_miso,
    output wire				layer_0_spi_mosi,

    output wire				layer_1_hold,
    input  wire				layer_1_interruptn,
    output wire				layer_1_resn,
    output wire				layer_1_spi_clk,
    output wire				layer_1_spi_csn,
    input  wire [1:0]		layer_1_spi_miso,
    output wire				layer_1_spi_mosi,

    output wire				layer_2_hold,
    input  wire				layer_2_interruptn,
    output wire				layer_2_resn,
    output wire				layer_2_spi_clk,
    output wire				layer_2_spi_csn,
    input  wire [1:0]		layer_2_spi_miso,
    output wire				layer_2_spi_mosi,

    output wire             layers_inj,
    output wire             layers_spi_csn, // This is a merged CS for all layers
    output wire				layers_sr_in_rb,
    input  wire				layers_sr_in_sout0,
    input  wire				layers_sr_in_sout1,
    input  wire				layers_sr_in_sout2,
    output wire				layers_sr_out_ck1,
    output wire				layers_sr_out_ck2,
    output wire				layers_sr_out_ld0,
    output wire				layers_sr_out_ld1,
    output wire				layers_sr_out_ld2,
    output wire				layers_sr_out_ldtdac0,
    output wire				layers_sr_out_ldtdac1,
    output wire				layers_sr_out_ldtdac2,
    output wire				layers_sr_out_sin,

    output wire [7:0]		rfg_io_led,
    input  wire				spi_clk,
    input  wire				spi_csn,
    output wire				spi_miso,
    input  wire				spi_mosi,

    input  wire				uart_rx,
    output wire				uart_tx,


    input  wire             ftdi_clko,
    inout  [7:0]            ftdi_data,
    input  wire             ftdi_rxf_n,
    input  wire             ftdi_txe_n,
    output wire             ftdi_rd_n,
    output wire             ftdi_wr_n,
    output wire             ftdi_oe_n,


    output wire [7:0]       chip_version,


    // Target Specific
    //---------------
    output wire             gecco_sr_ctrl_ck,
    output wire             gecco_sr_ctrl_sin,
    output wire             gecco_sr_ctrl_ld,

    // IO Control
    //-----------
    output wire io_ctrl_sample_clock_enable,
    output wire io_ctrl_timestamp_clock_enable,
    output wire io_ctrl_gecco_sample_clock_se,
    output wire io_ctrl_gecco_inj_enable,
    output wire io_ctrl_fpga_ts_clock_diff,

    // External Clock for FPGA Timestamp clock
    //-------
    input  wire ext_timestamp_clk,

    // External trigger event inputs
    // ---------------------
    input  wire tlu_t0,
    input  wire tlu_trigger,
    output wire tlu_busy,
    output logic tlu_trigger_synced
);

    // Wires needed in multiple places below
    // ------------
    wire layer_2_cfg_ctrl_loopback,layer_1_cfg_ctrl_loopback,layer_0_cfg_ctrl_loopback;


    // Clocking
    //-------------------
    wire clk_100; // size=1
    wire clk_100_resn; // size=1
    wire clk_uart; // size=1
    wire clk_uart_resn; // size=1
    //wire clk_core; // size=1
    //wire clk_core_resn; // size=1
    wire clk_ftdi_resn;

    wire global_resn_o;

    assign clk_sample = clk_100;
    
    wire layers_fpga_timestamp_ctrl_use_tlu,clock_ctrl_ext_clk_enable;
    
    astep24_3l_top_clocking  clocking_reset_I (

        .sysclk_in(sysclk),
        .clk_ext(clk_ext),
        .resn(resn),
        .ext_clk_allowed(clock_ctrl_ext_clk_enable),
        .global_resn_o(global_resn_o),


        .clk_80(clk_core),
        .clk_80_resn(clk_core_resn),


        .clk_100(clk_100),
        .clk_100_resn(clk_100_resn),

        .clk_10(clk_timestamp),
        .clk_10_resn(),

        .clk_20(clk_sample_ap4),
        .clk_20_resn(),

        .clk_2_5(clk_timestamp_ap4),
        .clk_2_5_resn(),

        .clk_ext_selected(clk_ext_selected),

        .sysclk_40M(sysclk_40M)

    );

    // Interrupt Input Sychronisation
    // Sync the external interrut signal, or the loopback interrupt signal only if loopback is enabled
    //-----------
    //

    wire [2:0] layers_loopback_interruptn;
    wire [2:0] layers_interruptn = {layer_2_interruptn, layer_1_interruptn, layer_0_interruptn };
    wire [2:0] layers_interruptn_synced;

    genvar li;
    generate
        for (li = 0 ; li < 3 ; li++) begin
            async_input_sync #(.RESET_VALUE(1'b1),.DEBOUNCE_DELAY(2)) layer_interrupt_sync (
                .async_input(layers_interruptn[li]),
                .clk(clk_core),
                .resn(clk_core_resn),
                .sync_out(layers_interruptn_synced[li])
            );
        end
    endgenerate


    wire [2:0] layers_interruptn_ext_or_loopback = {
        layers_interruptn_synced[2]  & (layers_loopback_interruptn[2] || !(layer_2_cfg_ctrl_loopback)),
        layers_interruptn_synced[1]  & (layers_loopback_interruptn[1] || !(layer_1_cfg_ctrl_loopback)),
        layers_interruptn_synced[0]  & (layers_loopback_interruptn[0] || !(layer_0_cfg_ctrl_loopback))
    };




    // SW interface
    //-------------
    wire [15:0] sw_if_rfg_address;
    wire [7:0] sw_if_rfg_write_value;
    wire [7:0] sw_if_rfg_read_value;
    wire sw_if_rfg_write;
    wire sw_if_rfg_write_last;
    wire sw_if_rfg_read;
    wire sw_if_rfg_read_valid;

    resets_synchronizer #(
        .CLOCKS(1),
        .RESET_DELAY(15)
    ) reset_sync_ftdi (
        .async_resn_in(global_resn_o),
        .input_clocks({ftdi_clko}),
        .output_resn({clk_ftdi_resn}),
        .master_all_reset( )
    );

    sw_ftdi245_spi_uart  sw_if (
        .clk_core(clk_core),
        .clk_core_resn(clk_core_resn),
        .clk_uart(1'b1),
        .clk_uart_resn(1'b0),
        .rfg_address(sw_if_rfg_address),
        .rfg_read(sw_if_rfg_read),
        .rfg_read_valid(sw_if_rfg_read_valid),
        .rfg_read_value(sw_if_rfg_read_value),
        .rfg_write(sw_if_rfg_write),
        .rfg_write_last(sw_if_rfg_write_last),
        .rfg_write_value(sw_if_rfg_write_value),
        .spi_clk(spi_clk),
        .spi_csn(spi_csn),
        .spi_miso(spi_miso),
        .spi_mosi(spi_mosi),
        .uart_rx(uart_rx),
        .uart_tx(uart_tx),


        .clk_ftdi(ftdi_clko),
        .clk_ftdi_resn(clk_ftdi_resn),
        .ftdi_txe_n(ftdi_txe_n),
        .ftdi_rxf_n(ftdi_rxf_n),
        .ftdi_rd_n(ftdi_rd_n),
        .ftdi_oe_n(ftdi_oe_n),
        .ftdi_wr_n(ftdi_wr_n),
        .ftdi_data(ftdi_data)
    );


    // Register File
    //-----------------

    wire [7:0]  injection_generator_inj_wdata;
    wire [3:0]  injection_generator_inj_waddr;

    wire [7:0]  hk_dac_mosi_fifo_m_axis_tdata;
    wire [7:0]  hk_adcdac_mosi_fifo_m_axis_tdata;
    wire [31:0] hk_adc_miso_fifo_read_size;
    wire [7:0]  hk_adc_miso_fifo_s_axis_tdata;
    wire [15:0] hk_xadc_temperature;
    wire [15:0] hk_xadc_vccint;

    wire [7:0]  layer_0_mosi_tdata;
    wire [7:0]  layer_1_mosi_tdata;
    wire [7:0]  layer_2_mosi_tdata;

    wire [31:0] layer_0_mosi_write_size;
    wire [31:0] layer_1_mosi_write_size;
    wire [31:0] layer_2_mosi_write_size;

    wire layer_0_reset;
    wire layer_1_reset;
    wire layer_2_reset;


    assign layer_0_resn = !layer_0_reset;
    assign layer_1_resn = !layer_1_reset;
    assign layer_2_resn = !layer_2_reset;


    wire [7:0]  layers_readout_s_axis_tdata;
    wire [31:0] layers_readout_read_size;
    wire [7:0]  layers_cfg_nodata_continue;

    // Wires for FPGA TS counter
    wire [63:0] layers_fpga_timestamp_counter_to_layers,tlu_ts_out,layers_fpga_timestamp_forced;
    reg         layers_fpga_timestamp_counter_clear; // Set to 1 upon external trigger negedge or always 0
    
    wire [1:0]  layers_fpga_timestamp_ctrl_timestamp_size;
    wire        layers_fpga_timestamp_ctrl_enable;
    wire        layers_fpga_timestamp_ctrl_use_divider;
    wire        layers_fpga_timestamp_divider_interrupt;

    wire layers_fpga_timestamp_ctrl_count = layers_fpga_timestamp_ctrl_enable &&
        (
            (layers_fpga_timestamp_ctrl_use_divider && layers_fpga_timestamp_divider_interrupt) ||
            !layers_fpga_timestamp_ctrl_use_divider
        );

    wire [15:0] layers_tlu_busy_duration;
    wire [15:0] layers_tlu_trigger_delay;

    wire hk_conversion_trigger_interrupt;
    wire hk_ctrl_select_adc,hk_ctrl_select_dac;

    // external TS clock edge
    wire ext_timestamp_clk_rising;

    wire [7:0]  layer_0_loopback_miso_m_axis_tdata;
    wire [31:0] layer_0_loopback_miso_write_size;
    wire [7:0]  layer_0_loopback_mosi_s_axis_tdata;
    wire [31:0] layer_0_loopback_mosi_read_size;

    wire [7:0]  layer_1_loopback_miso_m_axis_tdata;
    wire [31:0] layer_1_loopback_miso_write_size;
    wire [7:0]  layer_1_loopback_mosi_s_axis_tdata;
    wire [31:0] layer_1_loopback_mosi_read_size;

    wire [7:0]  layer_2_loopback_miso_m_axis_tdata;
    wire [31:0] layer_2_loopback_miso_write_size;
    wire [7:0]  layer_2_loopback_mosi_s_axis_tdata;
    wire [31:0] layer_2_loopback_mosi_read_size;


    wire layer_0_stat_wronglength_counter_enable,layer_1_stat_wronglength_counter_enable,layer_2_stat_wronglength_counter_enable;
    
    // Config Readback CRC and bits packed in bytes
    wire [47:0] layers_sr_crc;
    wire        layers_sr_crc_write;
    wire [7:0]  layers_sr_bytes_s_axis_tdata;
    wire [31:0] layers_sr_bytes_read_size;
    
    wire [4:0]  layers_sr_rb_ctrl_sout_select;
    
   
    
    
    main_rfg  main_rfg_I (

        .clk(clk_core),
        .resn(clk_core_resn),
        .rfg_address(sw_if_rfg_address),
        .rfg_write_value(sw_if_rfg_write_value),
        .rfg_write(sw_if_rfg_write),
        .rfg_write_last(sw_if_rfg_write_last),
        .rfg_read(sw_if_rfg_read),
        .rfg_read_valid(sw_if_rfg_read_valid),
        .rfg_read_value(sw_if_rfg_read_value),

        .io_led(rfg_io_led[7:0]),

        .chip_version(chip_version),
        
        
        .clock_ctrl(),
        .clock_ctrl_ext_clk_enable(clock_ctrl_ext_clk_enable),
        .clock_ctrl_ext_clk_differential(io_ctrl_fpga_ts_clock_diff),
        .clock_ctrl_current_clk(clk_ext_selected),
        .clock_ctrl_sample_clock_enable(io_ctrl_sample_clock_enable),
        .clock_ctrl_timestamp_clock_enable(io_ctrl_timestamp_clock_enable),

        .hk_ctrl(),
        .hk_ctrl_select_adc(hk_ctrl_select_adc),
        .hk_ctrl_select_dac(hk_ctrl_select_dac),
        .hk_ctrl_spi_cpol(hk_ctrl_spi_cpol),
        .hk_ctrl_spi_cpha(hk_ctrl_spi_cpha),
        .hk_xadc_temperature(hk_xadc_temperature),
        .hk_xadc_temperature_write(hk_xadc_temperature_write),
        .hk_xadc_vccint(hk_xadc_vccint),
        .hk_xadc_vccint_write(hk_xadc_vccint_write),
        .hk_conversion_trigger(),
        .hk_conversion_trigger_interrupt(hk_conversion_trigger_interrupt),
        .hk_conversion_trigger_match(),
        .hk_stat_conversions_counter_enable(hk_xadc_temperature_write),

        // ADC+DAC -> MOSI
        .hk_adcdac_mosi_fifo_m_axis_tdata(hk_adcdac_mosi_fifo_m_axis_tdata),
        .hk_adcdac_mosi_fifo_m_axis_tvalid(hk_adcdac_mosi_fifo_m_axis_tvalid),
        .hk_adcdac_mosi_fifo_m_axis_tready(hk_adcdac_mosi_fifo_m_axis_tready),
        .hk_adcdac_mosi_fifo_m_axis_tlast(hk_adcdac_mosi_fifo_m_axis_tlast),

        // ADC <- MISO
        .hk_adc_miso_fifo_s_axis_tdata(hk_adc_miso_fifo_s_axis_tdata),
        .hk_adc_miso_fifo_s_axis_tvalid(hk_adc_miso_fifo_s_axis_tvalid),
        .hk_adc_miso_fifo_s_axis_tready(hk_adc_miso_fifo_s_axis_tready),
        .hk_adc_miso_fifo_read_size(hk_adc_miso_fifo_read_size),
        .hk_adc_miso_fifo_read_size_write(1'b1),

        // SPI Clock Dividers
        .spi_layers_ckdivider_source_clk(clk_core),
        .spi_layers_ckdivider_source_resn(clk_core_resn),
        .spi_layers_ckdivider_divided_clk(spi_layers_ckdivider_divided_clk),
        .spi_layers_ckdivider_divided_resn(spi_layers_ckdivider_divided_resn),

        .spi_hk_ckdivider_source_clk(clk_core),
        .spi_hk_ckdivider_source_resn(clk_core_resn),
        .spi_hk_ckdivider_divided_clk(spi_hk_ckdivider_divided_clk),
        .spi_hk_ckdivider_divided_resn(spi_hk_ckdivider_divided_resn),

        // Layers Controls
        .layer_0_cfg_ctrl(),
        .layer_0_cfg_ctrl_disable_autoread(layer_0_cfg_ctrl_disable_autoread),
        .layer_0_cfg_ctrl_reset(layer_0_reset),
        .layer_0_cfg_ctrl_hold(layer_0_hold),
        .layer_0_cfg_ctrl_cs(layer_0_cfg_ctrl_cs),
        .layer_0_cfg_ctrl_disable_miso(layer_0_cfg_ctrl_disable_miso),
        .layer_0_cfg_ctrl_loopback(layer_0_cfg_ctrl_loopback),

        .layer_1_cfg_ctrl(),
        .layer_1_cfg_ctrl_disable_autoread(layer_1_cfg_ctrl_disable_autoread),
        .layer_1_cfg_ctrl_reset(layer_1_reset),
        .layer_1_cfg_ctrl_hold(layer_1_hold),
        .layer_1_cfg_ctrl_cs(layer_1_cfg_ctrl_cs),
        .layer_1_cfg_ctrl_disable_miso(layer_1_cfg_ctrl_disable_miso),
        .layer_1_cfg_ctrl_loopback(layer_1_cfg_ctrl_loopback),


        .layer_2_cfg_ctrl(),
        .layer_2_cfg_ctrl_disable_autoread(layer_2_cfg_ctrl_disable_autoread),
        .layer_2_cfg_ctrl_reset(layer_2_reset),
        .layer_2_cfg_ctrl_hold(layer_2_hold),
        .layer_2_cfg_ctrl_cs(layer_2_cfg_ctrl_cs),
        .layer_2_cfg_ctrl_disable_miso(layer_2_cfg_ctrl_disable_miso),
        .layer_2_cfg_ctrl_loopback(layer_2_cfg_ctrl_loopback),

        .layer_0_status(),
        .layer_0_status_interruptn(layers_interruptn_synced[0]),
        .layer_0_status_frame_decoding(layer_0_status_frame_decoding),

        .layer_1_status(),
        .layer_1_status_interruptn(layers_interruptn_synced[1]),
        .layer_1_status_frame_decoding(layer_1_status_frame_decoding),

        .layer_2_status(),
        .layer_2_status_interruptn(layers_interruptn_synced[2]),
        .layer_2_status_frame_decoding(layer_2_status_frame_decoding),

        .layer_0_stat_frame_counter_enable(layer_0_stat_frame_counter_enable),
        .layer_1_stat_frame_counter_enable(layer_1_stat_frame_counter_enable),
        .layer_2_stat_frame_counter_enable(layer_2_stat_frame_counter_enable),

        .layer_0_stat_idle_counter_enable(layer_0_stat_idle_counter_enable),
        .layer_1_stat_idle_counter_enable(layer_1_stat_idle_counter_enable),
        .layer_2_stat_idle_counter_enable(layer_2_stat_idle_counter_enable),

        .layer_0_stat_wronglength_counter_enable(layer_0_stat_wronglength_counter_enable),
        .layer_1_stat_wronglength_counter_enable(layer_1_stat_wronglength_counter_enable),
        .layer_2_stat_wronglength_counter_enable(layer_2_stat_wronglength_counter_enable),

        .layer_0_mosi_m_axis_tdata(layer_0_mosi_tdata),
        .layer_0_mosi_m_axis_tvalid(layer_0_mosi_tvalid),
        .layer_0_mosi_m_axis_tready(layer_0_mosi_tready),
        .layer_0_mosi_m_axis_tlast(layer_0_mosi_tlast),
        .layer_0_mosi_write_size(layer_0_mosi_write_size),
        .layer_0_mosi_write_size_write(1'b1),

        .layer_1_mosi_m_axis_tdata(layer_1_mosi_tdata),
        .layer_1_mosi_m_axis_tvalid(layer_1_mosi_tvalid),
        .layer_1_mosi_m_axis_tready(layer_1_mosi_tready),
        .layer_1_mosi_m_axis_tlast(layer_1_mosi_tlast),
        .layer_1_mosi_write_size(layer_1_mosi_write_size),
        .layer_1_mosi_write_size_write(1'b1),

        .layer_2_mosi_m_axis_tdata(layer_2_mosi_tdata),
        .layer_2_mosi_m_axis_tvalid(layer_2_mosi_tvalid),
        .layer_2_mosi_m_axis_tready(layer_2_mosi_tready),
        .layer_2_mosi_m_axis_tlast(layer_2_mosi_tlast),
        .layer_2_mosi_write_size(layer_2_mosi_write_size),
        .layer_2_mosi_write_size_write(1'b1),

        // Loopbacks
        //--------------------

        .layer_0_loopback_miso_m_axis_tdata(layer_0_loopback_miso_m_axis_tdata),
        .layer_0_loopback_miso_m_axis_tvalid(layer_0_loopback_miso_m_axis_tvalid),
        .layer_0_loopback_miso_m_axis_tready(layer_0_loopback_miso_m_axis_tready),
        .layer_0_loopback_miso_write_size(layer_0_loopback_miso_write_size),
        .layer_0_loopback_miso_write_size_write(1'b1),

        .layer_0_loopback_mosi_s_axis_tdata(layer_0_loopback_mosi_s_axis_tdata),
        .layer_0_loopback_mosi_s_axis_tvalid(layer_0_loopback_mosi_s_axis_tvalid),
        .layer_0_loopback_mosi_s_axis_tready(layer_0_loopback_mosi_s_axis_tready),
        .layer_0_loopback_mosi_read_size(layer_0_loopback_mosi_read_size),
        .layer_0_loopback_mosi_read_size_write(1'b1),

        .layer_1_loopback_miso_m_axis_tdata(layer_1_loopback_miso_m_axis_tdata),
        .layer_1_loopback_miso_m_axis_tvalid(layer_1_loopback_miso_m_axis_tvalid),
        .layer_1_loopback_miso_m_axis_tready(layer_1_loopback_miso_m_axis_tready),
        .layer_1_loopback_miso_write_size(layer_1_loopback_miso_write_size),
        .layer_1_loopback_miso_write_size_write(1'b1),

        .layer_1_loopback_mosi_s_axis_tdata(layer_1_loopback_mosi_s_axis_tdata),
        .layer_1_loopback_mosi_s_axis_tvalid(layer_1_loopback_mosi_s_axis_tvalid),
        .layer_1_loopback_mosi_s_axis_tready(layer_1_loopback_mosi_s_axis_tready),
        .layer_1_loopback_mosi_read_size(layer_1_loopback_mosi_read_size),
        .layer_1_loopback_mosi_read_size_write(1'b1),


        .layer_2_loopback_miso_m_axis_tdata(layer_2_loopback_miso_m_axis_tdata),
        .layer_2_loopback_miso_m_axis_tvalid(layer_2_loopback_miso_m_axis_tvalid),
        .layer_2_loopback_miso_m_axis_tready(layer_2_loopback_miso_m_axis_tready),
        .layer_2_loopback_miso_write_size(layer_2_loopback_miso_write_size),
        .layer_2_loopback_miso_write_size_write(1'b1),

        .layer_2_loopback_mosi_s_axis_tdata(layer_2_loopback_mosi_s_axis_tdata),
        .layer_2_loopback_mosi_s_axis_tvalid(layer_2_loopback_mosi_s_axis_tvalid),
        .layer_2_loopback_mosi_s_axis_tready(layer_2_loopback_mosi_s_axis_tready),
        .layer_2_loopback_mosi_read_size(layer_2_loopback_mosi_read_size),
        .layer_2_loopback_mosi_read_size_write(1'b1),



        // Configs
        //---------------

        .layers_fpga_timestamp_ctrl(),
        .layers_fpga_timestamp_ctrl_enable(layers_fpga_timestamp_ctrl_enable),
        .layers_fpga_timestamp_ctrl_use_divider(layers_fpga_timestamp_ctrl_use_divider),
        .layers_fpga_timestamp_ctrl_use_tlu(layers_fpga_timestamp_ctrl_use_tlu),
        .layers_fpga_timestamp_ctrl_tlu_busy_on_t0(layers_fpga_timestamp_ctrl_tlu_busy_on_t0),
        .layers_fpga_timestamp_ctrl_timestamp_size(layers_fpga_timestamp_ctrl_timestamp_size),
        .layers_fpga_timestamp_ctrl_force_value(layers_fpga_timestamp_ctrl_force_value),
        .layers_fpga_timestamp_ctrl_force_lsb_0(layers_fpga_timestamp_ctrl_force_lsb_0),
        
        .layers_fpga_timestamp_divider(),
        .layers_fpga_timestamp_divider_interrupt(layers_fpga_timestamp_divider_interrupt),
        .layers_fpga_timestamp_divider_enable(layers_fpga_timestamp_ctrl_use_divider),
        .layers_fpga_timestamp_divider_match(),

        .layers_fpga_timestamp_counter(tlu_ts_out),
        .layers_fpga_timestamp_forced(layers_fpga_timestamp_forced),
        //.layers_fpga_timestamp_counter_enable(layers_fpga_timestamp_ctrl_count),
        //.layers_fpga_timestamp_counter_clear(layers_fpga_timestamp_counter_clear),
        .layers_tlu_trigger_delay(layers_tlu_trigger_delay),
        .layers_tlu_busy_duration(layers_tlu_busy_duration),


        .layers_cfg_nodata_continue(layers_cfg_nodata_continue),

        .layers_sr_out(),
        .layers_sr_out_ck1(layers_sr_out_ck1),
        .layers_sr_out_ck2(layers_sr_out_ck2),
        .layers_sr_out_sin(layers_sr_out_sin),
        .layers_sr_out_ld0(layers_sr_out_ld0),
        .layers_sr_out_ld1(layers_sr_out_ld1),
        .layers_sr_out_ld2(layers_sr_out_ld2),
        .layers_sr_out_ldtdac0(layers_sr_out_ldtdac0),
        .layers_sr_out_ldtdac1(layers_sr_out_ldtdac1),
        .layers_sr_out_ldtdac2(layers_sr_out_ldtdac2),
        
        
        .layers_sr_in(),
        .layers_sr_in_sout0(layers_sr_in_sout0),
        .layers_sr_in_sout1(layers_sr_in_sout1),
        .layers_sr_in_sout2(layers_sr_in_sout2),
        
        
        .layers_sr_rb_ctrl(),
        .layers_sr_rb_ctrl_rb(layers_sr_in_rb),
        .layers_sr_rb_ctrl_crc_enable(layers_sr_rb_ctrl_crc_enable),
        .layers_sr_rb_ctrl_sout_select(layers_sr_rb_ctrl_sout_select),
        
        .layers_sr_crc(layers_sr_crc),
        .layers_sr_crc_write(layers_sr_crc_write),
        
        // AXIS Slave interface to read from FIFO layers_sr_bytes,
        // --------------------,
        .layers_sr_bytes_s_axis_tdata(layers_sr_bytes_s_axis_tdata),
        .layers_sr_bytes_s_axis_tvalid(layers_sr_bytes_s_axis_tvalid),
        .layers_sr_bytes_s_axis_tready(layers_sr_bytes_s_axis_tready),
        .layers_sr_bytes_read_size(layers_sr_bytes_read_size),
        .layers_sr_bytes_read_size_write(1'b1),

        .layers_inj_ctrl(),
        .layers_inj_ctrl_reset              (injection_generator_inj_ctrl_reset),
        .layers_inj_ctrl_suspend            (injection_generator_inj_ctrl_suspend),
        .layers_inj_ctrl_synced             (injection_generator_inj_ctrl_synced),
        .layers_inj_ctrl_trigger            (injection_generator_inj_ctrl_trigger),
        .layers_inj_ctrl_write              (injection_generator_inj_ctrl_write),
        .layers_inj_ctrl_done               (injection_generator_inj_ctrl_done),
        .layers_inj_ctrl_running            (injection_generator_inj_ctrl_running),

        .layers_inj_waddr                   (injection_generator_inj_waddr),
        .layers_inj_wdata                   (injection_generator_inj_wdata),

      
        .layers_readout_ctrl(),
        .layers_readout_ctrl_packet_mode(layers_readout_ctrl_packet_mode),
        .layers_readout_s_axis_tdata(layers_readout_s_axis_tdata),
        .layers_readout_s_axis_tvalid(layers_readout_s_axis_tvalid),
        .layers_readout_s_axis_tready(layers_readout_s_axis_tready),
        .layers_readout_read_size(layers_readout_read_size),
        .layers_readout_read_size_write(1'b1),

        // Target Specific Registers
        .gecco_sr_ctrl(),
        .gecco_sr_ctrl_ck(gecco_sr_ctrl_ck),
        .gecco_sr_ctrl_sin(gecco_sr_ctrl_sin),
        .gecco_sr_ctrl_ld(gecco_sr_ctrl_ld),

        // I/O Control like clocks
        .io_ctrl(),
        .io_ctrl_reserved0(),
        .io_ctrl_reserved1(),
        .io_ctrl_gecco_sample_clock_se(io_ctrl_gecco_sample_clock_se),
        .io_ctrl_gecco_inj_enable(io_ctrl_gecco_inj_enable),
        .io_ctrl_reserved4(),
        .io_ctrl_reserved5()
  );




    // Layers Readout Module
    // - Contains Each Layer Interface with Protocol management, and the Switched buffer
    //-------------------------------
    wire [1:0] layer_0_spi_miso_internal;
    wire [1:0] layer_1_spi_miso_internal;
    wire [1:0] layer_2_spi_miso_internal;
    wire [7:0] payload_length = chip_version == 8'd3 ? 8'd4 : chip_version == 8'd4 ? 8'd7 : 8'd4;
    
    layers_readout_switched #(.LAYER_COUNT(3)) switched_readout(
        .clk_core(clk_core),
        .clk_core_resn(clk_core_resn),
        .clk_io(spi_layers_ckdivider_divided_clk),
        .clk_io_resn(spi_layers_ckdivider_divided_resn),

        // Layers
        .layers_interruptn({
            layers_interruptn_ext_or_loopback[2],
            layers_interruptn_ext_or_loopback[1],
            layers_interruptn_ext_or_loopback[0]}),
        .layers_spi_clk({
            layer_2_spi_clk,
            layer_1_spi_clk,
            layer_0_spi_clk}),
        .layers_spi_mosi({
            layer_2_spi_mosi,
            layer_1_spi_mosi,
            layer_0_spi_mosi}),
        .layers_spi_miso({
            layer_2_spi_miso_internal,
            layer_1_spi_miso_internal,
            layer_0_spi_miso_internal}),
        .layers_spi_csn(),

        // MOSI
        //-----------
        .layers_mosi_s_axis_tdata({
            layer_2_mosi_tdata,
            layer_1_mosi_tdata,
            layer_0_mosi_tdata}),
        .layers_mosi_s_axis_tlast({
            layer_2_mosi_tlast,
            layer_1_mosi_tlast,
            layer_0_mosi_tlast}),
        .layers_mosi_s_axis_tready({
            layer_2_mosi_tready,
            layer_1_mosi_tready,
            layer_0_mosi_tready}),
        .layers_mosi_s_axis_tvalid({
            layer_2_mosi_tvalid,
            layer_1_mosi_tvalid,
            layer_0_mosi_tvalid}),
        .layers_mosi_write_size({
            layer_2_mosi_write_size,
            layer_1_mosi_write_size,
            layer_0_mosi_write_size
        }),



        // MISO readout
        //-------------------
        .readout_frames_data_count(layers_readout_read_size),
        .readout_frames_m_axis_tdata(layers_readout_s_axis_tdata),
        .readout_frames_m_axis_tready(layers_readout_s_axis_tready),
        .readout_frames_m_axis_tvalid(layers_readout_s_axis_tvalid),

        // Configurations
        //---------------------
        .config_packet_mode(layers_readout_ctrl_packet_mode),
        .config_disable_autoread({
            layer_2_cfg_ctrl_disable_autoread,
            layer_1_cfg_ctrl_disable_autoread,
            layer_0_cfg_ctrl_disable_autoread
        }),
        .config_fpga_timestamp(layers_fpga_timestamp_counter_to_layers),
        .config_fpga_timestamp_size(layers_fpga_timestamp_ctrl_timestamp_size),
        .config_nodata_continue(layers_cfg_nodata_continue),
        .config_layers_reset({
            layer_2_reset,
            layer_1_reset,
            layer_0_reset
        }),
        .config_layers_disable_miso({
            layer_2_cfg_ctrl_disable_miso,
            layer_1_cfg_ctrl_disable_miso,
            layer_0_cfg_ctrl_disable_miso
        }),

        .config_payload_length(payload_length),

        // Statistics
        //----------------------
        .layers_status_frame_decoding({
            layer_2_status_frame_decoding,
            layer_1_status_frame_decoding,
            layer_0_status_frame_decoding
        }),
        .layers_stat_count_frame({
            layer_2_stat_frame_counter_enable,
            layer_1_stat_frame_counter_enable,
            layer_0_stat_frame_counter_enable}),
        .layers_stat_count_idle({
            layer_2_stat_idle_counter_enable,
            layer_1_stat_idle_counter_enable,
            layer_0_stat_idle_counter_enable}),
        .layers_stat_wronglength({
            layer_2_stat_wronglength_counter_enable,
            layer_1_stat_wronglength_counter_enable,
            layer_0_stat_wronglength_counter_enable
        })
    );
    
   

    // Injection Generator
    //-------------------
    sync_async_patgen  injection_generator (
        .clk                (clk_core),
        .rst               (injection_generator_inj_ctrl_reset),

        .out                (layers_inj),

        .rfg_write          (injection_generator_inj_ctrl_write),
        .rfg_write_address  (injection_generator_inj_waddr),
        .rfg_write_data     (injection_generator_inj_wdata),

        .done               (injection_generator_inj_ctrl_done),
        .running            (injection_generator_inj_ctrl_running),
        .suspend            (injection_generator_inj_ctrl_suspend),
        .synced             (injection_generator_inj_ctrl_synced),
        .syncrst            (injection_generator_inj_ctrl_trigger)
    );



    // Housekeeping
    //--------------------
    housekeeping_main  housekeeping(
        .clk_core(clk_core),
        .clk_core_resn(clk_core_resn),

        .clk_spi(spi_hk_ckdivider_divided_clk),
        .clk_spi_resn(spi_hk_ckdivider_divided_resn),

        .select_adc(hk_ctrl_select_adc),

        .ext_adc_miso_m_axis_tdata(hk_adc_miso_fifo_s_axis_tdata),
        .ext_adc_miso_m_axis_tready(hk_adc_miso_fifo_s_axis_tready),
        .ext_adc_miso_m_axis_tvalid(hk_adc_miso_fifo_s_axis_tvalid),
        .ext_adc_miso_read_size(hk_adc_miso_fifo_read_size),

        .ext_adcdac_mosi_s_axis_tdata(hk_adcdac_mosi_fifo_m_axis_tdata),
        .ext_adcdac_mosi_s_axis_tlast(hk_adcdac_mosi_fifo_m_axis_tlast),
        .ext_adcdac_mosi_s_axis_tready(hk_adcdac_mosi_fifo_m_axis_tready),
        .ext_adcdac_mosi_s_axis_tvalid(hk_adcdac_mosi_fifo_m_axis_tvalid),

        .ext_spi_clk(ext_spi_clk),
        .ext_spi_miso(ext_adc_spi_miso),
        .ext_spi_mosi(ext_spi_mosi),
        .spi_cpol(hk_ctrl_spi_cpol),
        .spi_cpha(hk_ctrl_spi_cpha),


        .xadc_conversion_trigger(hk_conversion_trigger_interrupt),
        .xadc_temperature(hk_xadc_temperature),
        .xadc_temperature_write(hk_xadc_temperature_write),
        .xadc_vccint(hk_xadc_vccint),
        .xadc_vccint_write(hk_xadc_vccint_write)
    );


    // SPI Loopbacks
    //-----------------------
    wire layer_0_loopback_csn = layer_0_spi_csn || !(layer_0_cfg_ctrl_loopback);
    wire layer_1_loopback_csn = layer_1_spi_csn || !(layer_1_cfg_ctrl_loopback);
    wire layer_2_loopback_csn = layer_2_spi_csn || !(layer_2_cfg_ctrl_loopback);



    wire [1:0] layer_0_spi_miso_loopback;
    wire [1:0] layer_1_spi_miso_loopback;
    wire [1:0] layer_2_spi_miso_loopback;



    loopback_spi_if  loopback_spi_layer_0 (
        .clk_core(clk_core),
        .clk_core_resn(clk_core_resn),

        .spi_clk(layer_0_spi_clk),

        .spi_mosi(layer_0_spi_mosi),
        .spi_miso(layer_0_spi_miso_loopback),
        .spi_csn(layer_0_loopback_csn),

        .interruptn(layers_loopback_interruptn[0]),

        .miso_s_axis_tdata(layer_0_loopback_miso_m_axis_tdata),
        .miso_s_axis_tready(layer_0_loopback_miso_m_axis_tready),
        .miso_s_axis_tvalid(layer_0_loopback_miso_m_axis_tvalid),
        .miso_s_write_size(layer_0_loopback_miso_write_size),

        .mosi_m_axis_tdata(layer_0_loopback_mosi_s_axis_tdata),
        .mosi_m_axis_tready(layer_0_loopback_mosi_s_axis_tready),
        .mosi_m_axis_tvalid(layer_0_loopback_mosi_s_axis_tvalid),
        .mosi_m_read_size(layer_0_loopback_mosi_read_size)
    );

    loopback_spi_if  loopback_spi_layer_1 (
        .clk_core(clk_core),
        .clk_core_resn(clk_core_resn),

        .spi_clk(layer_1_spi_clk),

        .spi_mosi(layer_1_spi_mosi),
        .spi_miso(layer_1_spi_miso_loopback),
        .spi_csn(layer_1_loopback_csn),

        .interruptn(layers_loopback_interruptn[1]),

        .miso_s_axis_tdata(layer_1_loopback_miso_m_axis_tdata),
        .miso_s_axis_tready(layer_1_loopback_miso_m_axis_tready),
        .miso_s_axis_tvalid(layer_1_loopback_miso_m_axis_tvalid),
        .miso_s_write_size(layer_1_loopback_miso_write_size),

        .mosi_m_axis_tdata(layer_1_loopback_mosi_s_axis_tdata),
        .mosi_m_axis_tready(layer_1_loopback_mosi_s_axis_tready),
        .mosi_m_axis_tvalid(layer_1_loopback_mosi_s_axis_tvalid),
        .mosi_m_read_size(layer_1_loopback_mosi_read_size)
    );

    loopback_spi_if  loopback_spi_layer_2 (
        .clk_core(clk_core),
        .clk_core_resn(clk_core_resn),

        .spi_clk(layer_2_spi_clk),

        .spi_mosi(layer_2_spi_mosi),
        .spi_miso(layer_2_spi_miso_loopback),
        .spi_csn(layer_2_loopback_csn),

        .interruptn(layers_loopback_interruptn[2]),


        .miso_s_axis_tdata(layer_2_loopback_miso_m_axis_tdata),
        .miso_s_axis_tready(layer_2_loopback_miso_m_axis_tready),
        .miso_s_axis_tvalid(layer_2_loopback_miso_m_axis_tvalid),
        .miso_s_write_size(layer_2_loopback_miso_write_size),

        .mosi_m_axis_tdata(layer_2_loopback_mosi_s_axis_tdata),
        .mosi_m_axis_tready(layer_2_loopback_mosi_s_axis_tready),
        .mosi_m_axis_tvalid(layer_2_loopback_mosi_s_axis_tvalid),
        .mosi_m_read_size(layer_2_loopback_mosi_read_size)
    );


    // SPI IO
    //-----------------

    //-- Shared CSN for Layers
    //---------------

    // First layers CSN are set by the control register
    // When Autoread is on, always set CSN to 0 - otherwise the CS control bit sets it
    assign layer_0_spi_csn = !(layer_0_cfg_ctrl_cs || !layer_0_cfg_ctrl_disable_autoread) ;
    assign layer_1_spi_csn = !(layer_1_cfg_ctrl_cs || !layer_1_cfg_ctrl_disable_autoread) ;
    assign layer_2_spi_csn = !(layer_2_cfg_ctrl_cs || !layer_2_cfg_ctrl_disable_autoread) ;
    assign layers_spi_csn = layer_0_spi_csn & layer_1_spi_csn & layer_2_spi_csn;


    assign layer_0_spi_miso_internal =  layer_0_loopback_csn ? layer_0_spi_miso : layer_0_spi_miso_loopback  ;
    assign layer_1_spi_miso_internal =  layer_1_loopback_csn ? layer_1_spi_miso : layer_1_spi_miso_loopback  ;
    assign layer_2_spi_miso_internal =  layer_2_loopback_csn ? layer_2_spi_miso : layer_2_spi_miso_loopback  ;

    //-- Housekeeping
    //--------------

    //-- MOSI and CLK is shared
    //-- CSN is selected based on RFG control
    assign ext_adc_spi_csn =  !hk_ctrl_select_adc;
    assign ext_dac_spi_csn =  !(hk_ctrl_select_dac & !hk_ctrl_select_adc);


    // FPGA Timestamp Counter
    // - If external clear and freeze are selected, clear counter on trigger "T0" input, and update the counter reg going to layer decoder upon trigger negedge pulse
    // - If external trigger features are not used, just count as configured and pass the counter to the layer decoder at each clock cycle
    //---------------------
    
    always_ff @(posedge clk_core) begin 
        if (!clk_core_resn) begin 
            tlu_trigger_synced <= 'b0;
        end
        else begin 
            tlu_trigger_synced <=tlu_trigger;
        end
    end
    
    // MUX output of TS to layers -> either counter or forced value. Counter value LSb can be forced to 0
    assign layers_fpga_timestamp_counter_to_layers = layers_fpga_timestamp_ctrl_force_value ? layers_fpga_timestamp_forced : (tlu_ts_out & ~(64'd0 | layers_fpga_timestamp_ctrl_force_lsb_0));
    
    tlu_client  #(
         .TRIG_TS_WIDTH(64),
         .TRIG_ID_WIDTH(32),
         .BUSY_DURATION_WIDTH(16),
         .TRIGGER_DELAY_WIDTH(16),
         .USE_CHIPSCOPE_TLU(0)
      ) tlu (
        .tlu_clk_in(clk_core),
        .tlu_resn_in(clk_core_resn & layers_fpga_timestamp_ctrl_enable),
        .tlu_sync_in(tlu_t0),
        .tlu_trig_in(tlu_trigger_synced),
        .tlu_busy_out(tlu_busy),

        .enable_in(layers_fpga_timestamp_ctrl_use_tlu),
        .enable_counter_in(layers_fpga_timestamp_ctrl_count),

        .t0_out(),
        .trigger_out(),
        .trigger_ts_out(tlu_ts_out),
        .trigger_id_out(),
        .triggerdata_valid_out(),

        .t0_inject_in(1'b0),
        .trigger_inject_in(1'b0),

        .conf_busy_min_duration_in(layers_tlu_busy_duration),
        .conf_trigger_delay_in(layers_tlu_trigger_delay),
        .conf_t0_mode_in(1'b1),
        .conf_gate_trigger_before_t0_in(1'b1),
        .conf_gate_trigger_when_busy_in(1'b1),
        .conf_busy_on_t0_in(layers_fpga_timestamp_ctrl_tlu_busy_on_t0),

        // Not needed for now
        .busy_in(1'b0)
      );
      
      
      
    // Readback of config Bits 
    // -----------------------
    
    //- First CRC Moduel that returns Config CRC and the bits packed as bytes
    wire [31:0] layers_sr_crc_value;
    wire [15:0] layers_sr_crc_parities;
    assign      layers_sr_crc = {layers_sr_crc_parities,layers_sr_crc_value};
    
    wire [7:0]  layers_crc_bytesout_data;
    wire        layers_crc_bytesout_valid;
    
    logic crc_sout_select;
    always_comb begin
        if (layers_sr_rb_ctrl_sout_select==5'd0) begin 
            crc_sout_select = layers_sr_in_sout0;
        end
        else if (layers_sr_rb_ctrl_sout_select==5'd1) begin 
            crc_sout_select = layers_sr_in_sout1;
        end
        else if (layers_sr_rb_ctrl_sout_select==5'd2) begin 
            crc_sout_select = layers_sr_in_sout2;
        end
        else  begin 
            crc_sout_select = layers_sr_in_sout0;
        end
    end
    
    
    sr_readback_crc sr_readback_crc (
        .clk(clk_core),
        .resn(clk_core_resn),
        .enable(layers_sr_rb_ctrl_crc_enable),

        .sin(crc_sout_select),
        .clk1(layers_sr_out_ck1),
        .clk2(layers_sr_out_ck2),

        .crc(layers_sr_crc_value),
        .parities(layers_sr_crc_parities),
        .crc_valid(layers_sr_crc_write),
        .bits_byte(layers_crc_bytesout_data),
        .bits_byte_valid(layers_crc_bytesout_valid)

    );
    
    
    
    //- Second the FIFO that gets the Bits packed as bytes 
    fifo_axis_1clk_1kB  sr_readback_bytes_fifo (
        .s_axis_aclk(clk_core),
        .s_axis_aresetn(clk_core_resn),

        // From CRC Module
        .s_axis_tdata(layers_crc_bytesout_data),
        .s_axis_tready(),
        .s_axis_tvalid(layers_crc_bytesout_valid),
        .s_axis_tlast(1'b1),

        // To RFG Readout
        .axis_rd_data_count(layers_sr_bytes_read_size),
        .m_axis_tdata(layers_sr_bytes_s_axis_tdata),
        .m_axis_tready(layers_sr_bytes_s_axis_tready),
        .m_axis_tvalid(layers_sr_bytes_s_axis_tvalid),
        .m_axis_tlast()
    );
     
    
    

endmodule
