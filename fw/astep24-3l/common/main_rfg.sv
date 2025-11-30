module main_rfg(
    // IO
    // RFG R/W Interface,
    // --------------------,
    input  wire                  clk,
    input  wire                  resn,
    input  wire  [15:0]          rfg_address,
    output reg                   rfg_address_valid,
    input  wire  [7:0]           rfg_write_value,
    output reg                   rfg_write_valid,
    input  wire                  rfg_write,
    input  wire                  rfg_write_last,
    input  wire                  rfg_read,
    output reg                   rfg_read_valid,
    output reg  [7:0]            rfg_read_value,

    output wire [7:0]           clock_ctrl,
    output wire                  clock_ctrl_ext_clk_enable,
    output wire                  clock_ctrl_ext_clk_differential,
    input  wire                  clock_ctrl_current_clk,
    output wire                  clock_ctrl_sample_clock_enable,
    output wire                  clock_ctrl_timestamp_clock_enable,
    input  wire [15:0]            hk_xadc_temperature,
    input  wire                  hk_xadc_temperature_write,
    input  wire [15:0]            hk_xadc_vccint,
    input  wire                  hk_xadc_vccint_write,
    output wire [31:0]           hk_conversion_trigger,
    output reg                   hk_conversion_trigger_interrupt,
    input  wire                  hk_stat_conversions_counter_enable,
    output wire [7:0]           hk_ctrl,
    output wire                  hk_ctrl_select_adc,
    output wire                  hk_ctrl_select_dac,
    output wire                  hk_ctrl_spi_cpol,
    output wire                  hk_ctrl_spi_cpha,
    // AXIS Master interface to write to FIFO hk_adcdac_mosi_fifo,
    // --------------------,
    output logic [7:0]             hk_adcdac_mosi_fifo_m_axis_tdata,
    output logic                   hk_adcdac_mosi_fifo_m_axis_tvalid,
    input  wire                  hk_adcdac_mosi_fifo_m_axis_tready,
    output reg            hk_adcdac_mosi_fifo_m_axis_tlast,
    // AXIS Slave interface to read from FIFO hk_adc_miso_fifo,
    // --------------------,
    input  wire [7:0]            hk_adc_miso_fifo_s_axis_tdata,
    input  wire                  hk_adc_miso_fifo_s_axis_tvalid,
    output wire                  hk_adc_miso_fifo_s_axis_tready,
    input  wire [31:0]            hk_adc_miso_fifo_read_size,
    input  wire                  hk_adc_miso_fifo_read_size_write,
    input  wire            spi_layers_ckdivider_source_clk,
    input  wire            spi_layers_ckdivider_source_resn,
    output logic           spi_layers_ckdivider_divided_clk,
    output wire            spi_layers_ckdivider_divided_resn,
    input  wire            spi_hk_ckdivider_source_clk,
    input  wire            spi_hk_ckdivider_source_resn,
    output logic           spi_hk_ckdivider_divided_clk,
    output wire            spi_hk_ckdivider_divided_resn,
    output wire [7:0]           layer_0_cfg_ctrl,
    output wire                  layer_0_cfg_ctrl_hold,
    output wire                  layer_0_cfg_ctrl_reset,
    output wire                  layer_0_cfg_ctrl_disable_autoread,
    output wire                  layer_0_cfg_ctrl_cs,
    output wire                  layer_0_cfg_ctrl_disable_miso,
    output wire                  layer_0_cfg_ctrl_loopback,
    output wire [7:0]           layer_1_cfg_ctrl,
    output wire                  layer_1_cfg_ctrl_hold,
    output wire                  layer_1_cfg_ctrl_reset,
    output wire                  layer_1_cfg_ctrl_disable_autoread,
    output wire                  layer_1_cfg_ctrl_cs,
    output wire                  layer_1_cfg_ctrl_disable_miso,
    output wire                  layer_1_cfg_ctrl_loopback,
    output wire [7:0]           layer_2_cfg_ctrl,
    output wire                  layer_2_cfg_ctrl_hold,
    output wire                  layer_2_cfg_ctrl_reset,
    output wire                  layer_2_cfg_ctrl_disable_autoread,
    output wire                  layer_2_cfg_ctrl_cs,
    output wire                  layer_2_cfg_ctrl_disable_miso,
    output wire                  layer_2_cfg_ctrl_loopback,
    output wire [7:0]           layer_0_status,
    input  wire                  layer_0_status_interruptn,
    input  wire                  layer_0_status_frame_decoding,
    output wire [7:0]           layer_1_status,
    input  wire                  layer_1_status_interruptn,
    input  wire                  layer_1_status_frame_decoding,
    output wire [7:0]           layer_2_status,
    input  wire                  layer_2_status_interruptn,
    input  wire                  layer_2_status_frame_decoding,
    input  wire                  layer_0_stat_frame_counter_enable,
    input  wire                  layer_1_stat_frame_counter_enable,
    input  wire                  layer_2_stat_frame_counter_enable,
    input  wire                  layer_0_stat_idle_counter_enable,
    input  wire                  layer_1_stat_idle_counter_enable,
    input  wire                  layer_2_stat_idle_counter_enable,
    input  wire                  layer_0_stat_wronglength_counter_enable,
    input  wire                  layer_1_stat_wronglength_counter_enable,
    input  wire                  layer_2_stat_wronglength_counter_enable,
    // AXIS Master interface to write to FIFO layer_0_mosi,
    // --------------------,
    output logic [7:0]             layer_0_mosi_m_axis_tdata,
    output logic                   layer_0_mosi_m_axis_tvalid,
    input  wire                  layer_0_mosi_m_axis_tready,
    output reg            layer_0_mosi_m_axis_tlast,
    input  wire [31:0]            layer_0_mosi_write_size,
    input  wire                  layer_0_mosi_write_size_write,
    // AXIS Master interface to write to FIFO layer_1_mosi,
    // --------------------,
    output logic [7:0]             layer_1_mosi_m_axis_tdata,
    output logic                   layer_1_mosi_m_axis_tvalid,
    input  wire                  layer_1_mosi_m_axis_tready,
    output reg            layer_1_mosi_m_axis_tlast,
    input  wire [31:0]            layer_1_mosi_write_size,
    input  wire                  layer_1_mosi_write_size_write,
    // AXIS Master interface to write to FIFO layer_2_mosi,
    // --------------------,
    output logic [7:0]             layer_2_mosi_m_axis_tdata,
    output logic                   layer_2_mosi_m_axis_tvalid,
    input  wire                  layer_2_mosi_m_axis_tready,
    output reg            layer_2_mosi_m_axis_tlast,
    input  wire [31:0]            layer_2_mosi_write_size,
    input  wire                  layer_2_mosi_write_size_write,
    // AXIS Master interface to write to FIFO layer_0_loopback_miso,
    // --------------------,
    output logic [7:0]             layer_0_loopback_miso_m_axis_tdata,
    output logic                   layer_0_loopback_miso_m_axis_tvalid,
    input  wire                  layer_0_loopback_miso_m_axis_tready,
    input  wire [31:0]            layer_0_loopback_miso_write_size,
    input  wire                  layer_0_loopback_miso_write_size_write,
    // AXIS Master interface to write to FIFO layer_1_loopback_miso,
    // --------------------,
    output logic [7:0]             layer_1_loopback_miso_m_axis_tdata,
    output logic                   layer_1_loopback_miso_m_axis_tvalid,
    input  wire                  layer_1_loopback_miso_m_axis_tready,
    input  wire [31:0]            layer_1_loopback_miso_write_size,
    input  wire                  layer_1_loopback_miso_write_size_write,
    // AXIS Master interface to write to FIFO layer_2_loopback_miso,
    // --------------------,
    output logic [7:0]             layer_2_loopback_miso_m_axis_tdata,
    output logic                   layer_2_loopback_miso_m_axis_tvalid,
    input  wire                  layer_2_loopback_miso_m_axis_tready,
    input  wire [31:0]            layer_2_loopback_miso_write_size,
    input  wire                  layer_2_loopback_miso_write_size_write,
    // AXIS Slave interface to read from FIFO layer_0_loopback_mosi,
    // --------------------,
    input  wire [7:0]            layer_0_loopback_mosi_s_axis_tdata,
    input  wire                  layer_0_loopback_mosi_s_axis_tvalid,
    output wire                  layer_0_loopback_mosi_s_axis_tready,
    input  wire [31:0]            layer_0_loopback_mosi_read_size,
    input  wire                  layer_0_loopback_mosi_read_size_write,
    // AXIS Slave interface to read from FIFO layer_1_loopback_mosi,
    // --------------------,
    input  wire [7:0]            layer_1_loopback_mosi_s_axis_tdata,
    input  wire                  layer_1_loopback_mosi_s_axis_tvalid,
    output wire                  layer_1_loopback_mosi_s_axis_tready,
    input  wire [31:0]            layer_1_loopback_mosi_read_size,
    input  wire                  layer_1_loopback_mosi_read_size_write,
    // AXIS Slave interface to read from FIFO layer_2_loopback_mosi,
    // --------------------,
    input  wire [7:0]            layer_2_loopback_mosi_s_axis_tdata,
    input  wire                  layer_2_loopback_mosi_s_axis_tvalid,
    output wire                  layer_2_loopback_mosi_s_axis_tready,
    input  wire [31:0]            layer_2_loopback_mosi_read_size,
    input  wire                  layer_2_loopback_mosi_read_size_write,
    output wire [15:0]           layers_fpga_timestamp_ctrl,
    output wire                  layers_fpga_timestamp_ctrl_enable,
    output wire                  layers_fpga_timestamp_ctrl_use_divider,
    output wire                  layers_fpga_timestamp_ctrl_use_tlu,
    output wire                  layers_fpga_timestamp_ctrl_tlu_busy_on_t0,
    output wire [1:0]                  layers_fpga_timestamp_ctrl_timestamp_size,
    output wire                  layers_fpga_timestamp_ctrl_force_value,
    output wire                  layers_fpga_timestamp_ctrl_force_lsb_0,
    output wire [31:0]           layers_fpga_timestamp_divider,
    output reg                   layers_fpga_timestamp_divider_interrupt,
    input  wire                  layers_fpga_timestamp_divider_enable,
    input  wire [63:0]            layers_fpga_timestamp_counter,
    output wire [63:0]           layers_fpga_timestamp_forced,
    output wire [15:0]           layers_tlu_trigger_delay,
    output wire [15:0]           layers_tlu_busy_duration,
    output wire [7:0]           layers_cfg_nodata_continue,
    output wire [7:0]           layers_sr_out,
    output wire                  layers_sr_out_ck1,
    output wire                  layers_sr_out_ck2,
    output wire                  layers_sr_out_sin,
    output wire                  layers_sr_out_ld0,
    output wire                  layers_sr_out_ld1,
    output wire                  layers_sr_out_ld2,
    output wire [7:0]           layers_sr_in,
    input  wire                  layers_sr_in_sout0,
    input  wire                  layers_sr_in_sout1,
    input  wire                  layers_sr_in_sout2,
    output wire [7:0]           layers_sr_rb_ctrl,
    output wire                  layers_sr_rb_ctrl_rb,
    output wire                  layers_sr_rb_ctrl_crc_enable,
    output wire [4:0]                  layers_sr_rb_ctrl_sout_select,
    input  wire [47:0]            layers_sr_crc,
    input  wire                  layers_sr_crc_write,
    // AXIS Slave interface to read from FIFO layers_sr_bytes,
    // --------------------,
    input  wire [7:0]            layers_sr_bytes_s_axis_tdata,
    input  wire                  layers_sr_bytes_s_axis_tvalid,
    output wire                  layers_sr_bytes_s_axis_tready,
    input  wire [31:0]            layers_sr_bytes_read_size,
    input  wire                  layers_sr_bytes_read_size_write,
    output wire [7:0]           layers_inj_ctrl,
    output wire                  layers_inj_ctrl_reset,
    output wire                  layers_inj_ctrl_suspend,
    output wire                  layers_inj_ctrl_synced,
    output wire                  layers_inj_ctrl_trigger,
    output wire                  layers_inj_ctrl_write,
    input  wire                  layers_inj_ctrl_done,
    input  wire                  layers_inj_ctrl_running,
    output wire [3:0]           layers_inj_waddr,
    output wire [7:0]           layers_inj_wdata,
    output wire [7:0]           layers_readout_ctrl,
    output wire                  layers_readout_ctrl_packet_mode,
    // AXIS Slave interface to read from FIFO layers_readout,
    // --------------------,
    input  wire [7:0]            layers_readout_s_axis_tdata,
    input  wire                  layers_readout_s_axis_tvalid,
    output wire                  layers_readout_s_axis_tready,
    input  wire [31:0]            layers_readout_read_size,
    input  wire                  layers_readout_read_size_write,
    output wire [7:0]           io_ctrl,
    output wire                  io_ctrl_reserved0,
    output wire                  io_ctrl_reserved1,
    output wire                  io_ctrl_gecco_sample_clock_se,
    output wire                  io_ctrl_gecco_inj_enable,
    output wire                  io_ctrl_reserved4,
    output wire                  io_ctrl_reserved5,
    output wire [7:0]           io_led,
    output wire [7:0]           gecco_sr_ctrl,
    output wire                  gecco_sr_ctrl_ck,
    output wire                  gecco_sr_ctrl_sin,
    output wire                  gecco_sr_ctrl_ld,
    output wire [31:0]           hk_conversion_trigger_match,
    output wire [31:0]           layers_fpga_timestamp_divider_match
    );
    
    
    logic [15:0] hk_xadc_temperature_reg;
    logic [15:0] hk_xadc_vccint_reg;
    logic hk_conversion_trigger_up;
    logic [31:0] hk_adc_miso_fifo_read_size_reg;
    // Clock Divider spi_layers_ckdivider
    logic [7:0] spi_layers_ckdivider_counter;
    logic [7:0] spi_layers_ckdivider_reg;
    // Clock Divider spi_hk_ckdivider
    logic [7:0] spi_hk_ckdivider_counter;
    logic [7:0] spi_hk_ckdivider_reg;
    logic [31:0] layer_0_mosi_write_size_reg;
    logic [31:0] layer_1_mosi_write_size_reg;
    logic [31:0] layer_2_mosi_write_size_reg;
    logic [31:0] layer_0_loopback_miso_write_size_reg;
    logic [31:0] layer_1_loopback_miso_write_size_reg;
    logic [31:0] layer_2_loopback_miso_write_size_reg;
    logic [31:0] layer_0_loopback_mosi_read_size_reg;
    logic [31:0] layer_1_loopback_mosi_read_size_reg;
    logic [31:0] layer_2_loopback_mosi_read_size_reg;
    logic layers_fpga_timestamp_divider_up;
    logic [47:0] layers_sr_crc_reg;
    logic [31:0] layers_sr_bytes_read_size_reg;
    logic [31:0] layers_readout_read_size_reg;
    
    
    // Registers I/O assignments
    // ---------------
    logic [31:0] hk_firmware_id_reg;
    
    logic [31:0] hk_firmware_version_reg;
    
    logic [7:0] clock_ctrl_reg;
    assign clock_ctrl = clock_ctrl_reg;
    
    logic [31:0] hk_conversion_trigger_reg;
    assign hk_conversion_trigger = hk_conversion_trigger_reg;
    
    logic [31:0] hk_stat_conversions_counter_reg;
    
    logic [7:0] hk_ctrl_reg;
    assign hk_ctrl = hk_ctrl_reg;
    
    logic [7:0] layer_0_cfg_ctrl_reg;
    assign layer_0_cfg_ctrl = layer_0_cfg_ctrl_reg;
    
    logic [7:0] layer_1_cfg_ctrl_reg;
    assign layer_1_cfg_ctrl = layer_1_cfg_ctrl_reg;
    
    logic [7:0] layer_2_cfg_ctrl_reg;
    assign layer_2_cfg_ctrl = layer_2_cfg_ctrl_reg;
    
    logic [7:0] layer_0_status_reg;
    assign layer_0_status = layer_0_status_reg;
    
    logic [7:0] layer_1_status_reg;
    assign layer_1_status = layer_1_status_reg;
    
    logic [7:0] layer_2_status_reg;
    assign layer_2_status = layer_2_status_reg;
    
    logic [31:0] layer_0_stat_frame_counter_reg;
    
    logic [31:0] layer_1_stat_frame_counter_reg;
    
    logic [31:0] layer_2_stat_frame_counter_reg;
    
    logic [31:0] layer_0_stat_idle_counter_reg;
    
    logic [31:0] layer_1_stat_idle_counter_reg;
    
    logic [31:0] layer_2_stat_idle_counter_reg;
    
    logic [31:0] layer_0_stat_wronglength_counter_reg;
    
    logic [31:0] layer_1_stat_wronglength_counter_reg;
    
    logic [31:0] layer_2_stat_wronglength_counter_reg;
    
    logic [15:0] layers_fpga_timestamp_ctrl_reg;
    assign layers_fpga_timestamp_ctrl = layers_fpga_timestamp_ctrl_reg;
    
    logic [31:0] layers_fpga_timestamp_divider_reg;
    assign layers_fpga_timestamp_divider = layers_fpga_timestamp_divider_reg;
    
    logic [63:0] layers_fpga_timestamp_forced_reg;
    assign layers_fpga_timestamp_forced = layers_fpga_timestamp_forced_reg;
    
    logic [15:0] layers_tlu_trigger_delay_reg;
    assign layers_tlu_trigger_delay = layers_tlu_trigger_delay_reg;
    
    logic [15:0] layers_tlu_busy_duration_reg;
    assign layers_tlu_busy_duration = layers_tlu_busy_duration_reg;
    
    logic [7:0] layers_cfg_nodata_continue_reg;
    assign layers_cfg_nodata_continue = layers_cfg_nodata_continue_reg;
    
    logic [7:0] layers_sr_out_reg;
    assign layers_sr_out = layers_sr_out_reg;
    
    logic [7:0] layers_sr_in_reg;
    assign layers_sr_in = layers_sr_in_reg;
    
    logic [7:0] layers_sr_rb_ctrl_reg;
    assign layers_sr_rb_ctrl = layers_sr_rb_ctrl_reg;
    
    logic [7:0] layers_inj_ctrl_reg;
    assign layers_inj_ctrl = layers_inj_ctrl_reg;
    
    logic [3:0] layers_inj_waddr_reg;
    assign layers_inj_waddr = layers_inj_waddr_reg;
    
    logic [7:0] layers_inj_wdata_reg;
    assign layers_inj_wdata = layers_inj_wdata_reg;
    
    logic [7:0] layers_readout_ctrl_reg;
    assign layers_readout_ctrl = layers_readout_ctrl_reg;
    
    logic [7:0] io_ctrl_reg;
    assign io_ctrl = io_ctrl_reg;
    
    logic [7:0] io_led_reg;
    assign io_led = io_led_reg;
    
    logic [7:0] gecco_sr_ctrl_reg;
    assign gecco_sr_ctrl = gecco_sr_ctrl_reg;
    
    logic [31:0] hk_conversion_trigger_match_reg;
    assign hk_conversion_trigger_match = hk_conversion_trigger_match_reg;
    
    logic [31:0] layers_fpga_timestamp_divider_match_reg;
    assign layers_fpga_timestamp_divider_match = layers_fpga_timestamp_divider_match_reg;
    
    
    
    // Register Bits assignments
    // ---------------
    assign clock_ctrl_ext_clk_enable = clock_ctrl_reg[0];
    assign clock_ctrl_ext_clk_differential = clock_ctrl_reg[1];
    assign clock_ctrl_sample_clock_enable = clock_ctrl_reg[3];
    assign clock_ctrl_timestamp_clock_enable = clock_ctrl_reg[4];
    assign hk_ctrl_select_adc = hk_ctrl_reg[0];
    assign hk_ctrl_select_dac = hk_ctrl_reg[1];
    assign hk_ctrl_spi_cpol = hk_ctrl_reg[2];
    assign hk_ctrl_spi_cpha = hk_ctrl_reg[3];
    assign layer_0_cfg_ctrl_hold = layer_0_cfg_ctrl_reg[0];
    assign layer_0_cfg_ctrl_reset = layer_0_cfg_ctrl_reg[1];
    assign layer_0_cfg_ctrl_disable_autoread = layer_0_cfg_ctrl_reg[2];
    assign layer_0_cfg_ctrl_cs = layer_0_cfg_ctrl_reg[3];
    assign layer_0_cfg_ctrl_disable_miso = layer_0_cfg_ctrl_reg[4];
    assign layer_0_cfg_ctrl_loopback = layer_0_cfg_ctrl_reg[5];
    assign layer_1_cfg_ctrl_hold = layer_1_cfg_ctrl_reg[0];
    assign layer_1_cfg_ctrl_reset = layer_1_cfg_ctrl_reg[1];
    assign layer_1_cfg_ctrl_disable_autoread = layer_1_cfg_ctrl_reg[2];
    assign layer_1_cfg_ctrl_cs = layer_1_cfg_ctrl_reg[3];
    assign layer_1_cfg_ctrl_disable_miso = layer_1_cfg_ctrl_reg[4];
    assign layer_1_cfg_ctrl_loopback = layer_1_cfg_ctrl_reg[5];
    assign layer_2_cfg_ctrl_hold = layer_2_cfg_ctrl_reg[0];
    assign layer_2_cfg_ctrl_reset = layer_2_cfg_ctrl_reg[1];
    assign layer_2_cfg_ctrl_disable_autoread = layer_2_cfg_ctrl_reg[2];
    assign layer_2_cfg_ctrl_cs = layer_2_cfg_ctrl_reg[3];
    assign layer_2_cfg_ctrl_disable_miso = layer_2_cfg_ctrl_reg[4];
    assign layer_2_cfg_ctrl_loopback = layer_2_cfg_ctrl_reg[5];
    assign layers_fpga_timestamp_ctrl_enable = layers_fpga_timestamp_ctrl_reg[0];
    assign layers_fpga_timestamp_ctrl_use_divider = layers_fpga_timestamp_ctrl_reg[1];
    assign layers_fpga_timestamp_ctrl_use_tlu = layers_fpga_timestamp_ctrl_reg[2];
    assign layers_fpga_timestamp_ctrl_tlu_busy_on_t0 = layers_fpga_timestamp_ctrl_reg[3];
    assign layers_fpga_timestamp_ctrl_timestamp_size = layers_fpga_timestamp_ctrl_reg[5:4];
    assign layers_fpga_timestamp_ctrl_force_value = layers_fpga_timestamp_ctrl_reg[6];
    assign layers_fpga_timestamp_ctrl_force_lsb_0 = layers_fpga_timestamp_ctrl_reg[7];
    assign layers_sr_out_ck1 = layers_sr_out_reg[0];
    assign layers_sr_out_ck2 = layers_sr_out_reg[1];
    assign layers_sr_out_sin = layers_sr_out_reg[2];
    assign layers_sr_out_ld0 = layers_sr_out_reg[3];
    assign layers_sr_out_ld1 = layers_sr_out_reg[4];
    assign layers_sr_out_ld2 = layers_sr_out_reg[5];
    assign layers_sr_rb_ctrl_rb = layers_sr_rb_ctrl_reg[0];
    assign layers_sr_rb_ctrl_crc_enable = layers_sr_rb_ctrl_reg[1];
    assign layers_sr_rb_ctrl_sout_select = layers_sr_rb_ctrl_reg[6:2];
    assign layers_inj_ctrl_reset = layers_inj_ctrl_reg[0];
    assign layers_inj_ctrl_suspend = layers_inj_ctrl_reg[1];
    assign layers_inj_ctrl_synced = layers_inj_ctrl_reg[2];
    assign layers_inj_ctrl_trigger = layers_inj_ctrl_reg[3];
    assign layers_inj_ctrl_write = layers_inj_ctrl_reg[4];
    assign layers_readout_ctrl_packet_mode = layers_readout_ctrl_reg[0];
    assign io_ctrl_reserved0 = io_ctrl_reg[0];
    assign io_ctrl_reserved1 = io_ctrl_reg[1];
    assign io_ctrl_gecco_sample_clock_se = io_ctrl_reg[2];
    assign io_ctrl_gecco_inj_enable = io_ctrl_reg[3];
    assign io_ctrl_reserved4 = io_ctrl_reg[4];
    assign io_ctrl_reserved5 = io_ctrl_reg[5];
    assign gecco_sr_ctrl_ck = gecco_sr_ctrl_reg[0];
    assign gecco_sr_ctrl_sin = gecco_sr_ctrl_reg[1];
    assign gecco_sr_ctrl_ld = gecco_sr_ctrl_reg[2];
    
    
    // TMR Registers (if any)
    // ---------------
    
    // Register Writes
    // ---------------
    always_ff @(posedge clk) begin
        if (!resn) begin
            rfg_write_valid <= 'd0;
            hk_firmware_id_reg <= `RFG_FW_ID;
            hk_firmware_version_reg <= `RFG_FW_BUILD;
            clock_ctrl_reg <= 8'h2;
            hk_xadc_temperature_reg <= '0;
            hk_xadc_vccint_reg <= '0;
            hk_conversion_trigger_reg <= '0;
            hk_conversion_trigger_up <= 1'b1;
            hk_stat_conversions_counter_reg <= '0;
            hk_ctrl_reg <= '0;
            hk_adcdac_mosi_fifo_m_axis_tvalid <= 1'b0;
            hk_adcdac_mosi_fifo_m_axis_tlast  <= 1'b0;
            hk_adc_miso_fifo_read_size_reg <= '0;
            spi_layers_ckdivider_reg <= 8'h4;
            spi_hk_ckdivider_reg <= 8'h4;
            layer_0_cfg_ctrl_reg <= 8'b00000111;
            layer_1_cfg_ctrl_reg <= 8'b00000111;
            layer_2_cfg_ctrl_reg <= 8'b00000111;
            layer_0_status_reg <= '0;
            layer_1_status_reg <= '0;
            layer_2_status_reg <= '0;
            layer_0_stat_frame_counter_reg <= '0;
            layer_1_stat_frame_counter_reg <= '0;
            layer_2_stat_frame_counter_reg <= '0;
            layer_0_stat_idle_counter_reg <= '0;
            layer_1_stat_idle_counter_reg <= '0;
            layer_2_stat_idle_counter_reg <= '0;
            layer_0_stat_wronglength_counter_reg <= '0;
            layer_1_stat_wronglength_counter_reg <= '0;
            layer_2_stat_wronglength_counter_reg <= '0;
            layer_0_mosi_m_axis_tvalid <= 1'b0;
            layer_0_mosi_m_axis_tlast  <= 1'b0;
            layer_0_mosi_write_size_reg <= '0;
            layer_1_mosi_m_axis_tvalid <= 1'b0;
            layer_1_mosi_m_axis_tlast  <= 1'b0;
            layer_1_mosi_write_size_reg <= '0;
            layer_2_mosi_m_axis_tvalid <= 1'b0;
            layer_2_mosi_m_axis_tlast  <= 1'b0;
            layer_2_mosi_write_size_reg <= '0;
            layer_0_loopback_miso_m_axis_tvalid <= 1'b0;
            layer_0_loopback_miso_write_size_reg <= '0;
            layer_1_loopback_miso_m_axis_tvalid <= 1'b0;
            layer_1_loopback_miso_write_size_reg <= '0;
            layer_2_loopback_miso_m_axis_tvalid <= 1'b0;
            layer_2_loopback_miso_write_size_reg <= '0;
            layer_0_loopback_mosi_read_size_reg <= '0;
            layer_1_loopback_mosi_read_size_reg <= '0;
            layer_2_loopback_mosi_read_size_reg <= '0;
            layers_fpga_timestamp_ctrl_reg <= 16'h0010;
            layers_fpga_timestamp_divider_reg <= '0;
            layers_fpga_timestamp_divider_up <= 1'b1;
            layers_fpga_timestamp_forced_reg <= '0;
            layers_tlu_trigger_delay_reg <= 16'd2;
            layers_tlu_busy_duration_reg <= 16'd16;
            layers_cfg_nodata_continue_reg <= 8'd5;
            layers_sr_out_reg <= '0;
            layers_sr_in_reg <= '0;
            layers_sr_rb_ctrl_reg <= '0;
            layers_sr_crc_reg <= '0;
            layers_sr_bytes_read_size_reg <= '0;
            layers_inj_ctrl_reg <= 8'b00000110;
            layers_inj_waddr_reg <= '0;
            layers_inj_wdata_reg <= '0;
            layers_readout_ctrl_reg <= 8'h01;
            layers_readout_read_size_reg <= '0;
            io_ctrl_reg <= 8'b00011000;
            io_led_reg <= '0;
            gecco_sr_ctrl_reg <= '0;
            hk_conversion_trigger_match_reg <= 32'd10;
            layers_fpga_timestamp_divider_match_reg <= 32'd4;
        end else begin
            
            
            // Single in bits are always sampled
            clock_ctrl_reg[2] <= clock_ctrl_current_clk;
            layer_0_status_reg[0] <= layer_0_status_interruptn;
            layer_0_status_reg[1] <= layer_0_status_frame_decoding;
            layer_1_status_reg[0] <= layer_1_status_interruptn;
            layer_1_status_reg[1] <= layer_1_status_frame_decoding;
            layer_2_status_reg[0] <= layer_2_status_interruptn;
            layer_2_status_reg[1] <= layer_2_status_frame_decoding;
            layers_sr_in_reg[0] <= layers_sr_in_sout0;
            layers_sr_in_reg[1] <= layers_sr_in_sout1;
            layers_sr_in_reg[2] <= layers_sr_in_sout2;
            layers_inj_ctrl_reg[5] <= layers_inj_ctrl_done;
            layers_inj_ctrl_reg[6] <= layers_inj_ctrl_running;
            
            
            // Write for simple registers
            case({rfg_write,rfg_address})
                {1'b1,16'h8}: begin
                    clock_ctrl_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'hd}: begin
                    hk_conversion_trigger_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'he}: begin
                    hk_conversion_trigger_reg[15:8] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'hf}: begin
                    hk_conversion_trigger_reg[23:16] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h10}: begin
                    hk_conversion_trigger_reg[31:24] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h15}: begin
                    hk_ctrl_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h1c}: begin
                    spi_layers_ckdivider_reg <= rfg_write_value;
                end
                {1'b1,16'h1d}: begin
                    spi_hk_ckdivider_reg <= rfg_write_value;
                end
                {1'b1,16'h1e}: begin
                    layer_0_cfg_ctrl_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h1f}: begin
                    layer_1_cfg_ctrl_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h20}: begin
                    layer_2_cfg_ctrl_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h24}: begin
                    layer_0_stat_frame_counter_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h25}: begin
                    layer_0_stat_frame_counter_reg[15:8] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h26}: begin
                    layer_0_stat_frame_counter_reg[23:16] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h27}: begin
                    layer_0_stat_frame_counter_reg[31:24] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h28}: begin
                    layer_1_stat_frame_counter_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h29}: begin
                    layer_1_stat_frame_counter_reg[15:8] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h2a}: begin
                    layer_1_stat_frame_counter_reg[23:16] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h2b}: begin
                    layer_1_stat_frame_counter_reg[31:24] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h2c}: begin
                    layer_2_stat_frame_counter_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h2d}: begin
                    layer_2_stat_frame_counter_reg[15:8] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h2e}: begin
                    layer_2_stat_frame_counter_reg[23:16] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h2f}: begin
                    layer_2_stat_frame_counter_reg[31:24] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h30}: begin
                    layer_0_stat_idle_counter_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h31}: begin
                    layer_0_stat_idle_counter_reg[15:8] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h32}: begin
                    layer_0_stat_idle_counter_reg[23:16] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h33}: begin
                    layer_0_stat_idle_counter_reg[31:24] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h34}: begin
                    layer_1_stat_idle_counter_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h35}: begin
                    layer_1_stat_idle_counter_reg[15:8] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h36}: begin
                    layer_1_stat_idle_counter_reg[23:16] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h37}: begin
                    layer_1_stat_idle_counter_reg[31:24] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h38}: begin
                    layer_2_stat_idle_counter_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h39}: begin
                    layer_2_stat_idle_counter_reg[15:8] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h3a}: begin
                    layer_2_stat_idle_counter_reg[23:16] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h3b}: begin
                    layer_2_stat_idle_counter_reg[31:24] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h3c}: begin
                    layer_0_stat_wronglength_counter_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h3d}: begin
                    layer_0_stat_wronglength_counter_reg[15:8] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h3e}: begin
                    layer_0_stat_wronglength_counter_reg[23:16] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h3f}: begin
                    layer_0_stat_wronglength_counter_reg[31:24] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h40}: begin
                    layer_1_stat_wronglength_counter_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h41}: begin
                    layer_1_stat_wronglength_counter_reg[15:8] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h42}: begin
                    layer_1_stat_wronglength_counter_reg[23:16] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h43}: begin
                    layer_1_stat_wronglength_counter_reg[31:24] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h44}: begin
                    layer_2_stat_wronglength_counter_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h45}: begin
                    layer_2_stat_wronglength_counter_reg[15:8] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h46}: begin
                    layer_2_stat_wronglength_counter_reg[23:16] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h47}: begin
                    layer_2_stat_wronglength_counter_reg[31:24] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h75}: begin
                    layers_fpga_timestamp_ctrl_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h76}: begin
                    layers_fpga_timestamp_ctrl_reg[15:8] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h77}: begin
                    layers_fpga_timestamp_divider_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h78}: begin
                    layers_fpga_timestamp_divider_reg[15:8] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h79}: begin
                    layers_fpga_timestamp_divider_reg[23:16] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h7a}: begin
                    layers_fpga_timestamp_divider_reg[31:24] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h83}: begin
                    layers_fpga_timestamp_forced_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h84}: begin
                    layers_fpga_timestamp_forced_reg[15:8] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h85}: begin
                    layers_fpga_timestamp_forced_reg[23:16] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h86}: begin
                    layers_fpga_timestamp_forced_reg[31:24] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h87}: begin
                    layers_fpga_timestamp_forced_reg[39:32] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h88}: begin
                    layers_fpga_timestamp_forced_reg[47:40] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h89}: begin
                    layers_fpga_timestamp_forced_reg[55:48] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h8a}: begin
                    layers_fpga_timestamp_forced_reg[63:56] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h8b}: begin
                    layers_tlu_trigger_delay_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h8c}: begin
                    layers_tlu_trigger_delay_reg[15:8] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h8d}: begin
                    layers_tlu_busy_duration_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h8e}: begin
                    layers_tlu_busy_duration_reg[15:8] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h8f}: begin
                    layers_cfg_nodata_continue_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h90}: begin
                    layers_sr_out_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h91}: begin
                    layers_sr_in_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h92}: begin
                    layers_sr_rb_ctrl_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h9e}: begin
                    layers_inj_ctrl_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'h9f}: begin
                    layers_inj_waddr_reg[3:0] <= rfg_write_value[3:0];
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'ha0}: begin
                    layers_inj_wdata_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'ha1}: begin
                    layers_readout_ctrl_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'ha7}: begin
                    io_ctrl_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'ha8}: begin
                    io_led_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'ha9}: begin
                    gecco_sr_ctrl_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'haa}: begin
                    hk_conversion_trigger_match_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'hab}: begin
                    hk_conversion_trigger_match_reg[15:8] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'hac}: begin
                    hk_conversion_trigger_match_reg[23:16] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'had}: begin
                    hk_conversion_trigger_match_reg[31:24] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'hae}: begin
                    layers_fpga_timestamp_divider_match_reg[7:0] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'haf}: begin
                    layers_fpga_timestamp_divider_match_reg[15:8] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'hb0}: begin
                    layers_fpga_timestamp_divider_match_reg[23:16] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                {1'b1,16'hb1}: begin
                    layers_fpga_timestamp_divider_match_reg[31:24] <= rfg_write_value;
                    rfg_write_valid <= 'd1;
                end
                default: begin
                    rfg_write_valid <= 'd0 ;
                end
            endcase
            
            // Write for FIFO Master
            if(rfg_write && rfg_address==16'h16) begin
                hk_adcdac_mosi_fifo_m_axis_tvalid <= 1'b1;
                hk_adcdac_mosi_fifo_m_axis_tdata  <= rfg_write_value;
                hk_adcdac_mosi_fifo_m_axis_tlast  <= rfg_write_last;
            end else begin
                hk_adcdac_mosi_fifo_m_axis_tvalid <= 1'b0;
                hk_adcdac_mosi_fifo_m_axis_tlast  <= 1'b0;
            end
            if(rfg_write && rfg_address==16'h48) begin
                layer_0_mosi_m_axis_tvalid <= 1'b1;
                layer_0_mosi_m_axis_tdata  <= rfg_write_value;
                layer_0_mosi_m_axis_tlast  <= rfg_write_last;
            end else begin
                layer_0_mosi_m_axis_tvalid <= 1'b0;
                layer_0_mosi_m_axis_tlast  <= 1'b0;
            end
            if(rfg_write && rfg_address==16'h4d) begin
                layer_1_mosi_m_axis_tvalid <= 1'b1;
                layer_1_mosi_m_axis_tdata  <= rfg_write_value;
                layer_1_mosi_m_axis_tlast  <= rfg_write_last;
            end else begin
                layer_1_mosi_m_axis_tvalid <= 1'b0;
                layer_1_mosi_m_axis_tlast  <= 1'b0;
            end
            if(rfg_write && rfg_address==16'h52) begin
                layer_2_mosi_m_axis_tvalid <= 1'b1;
                layer_2_mosi_m_axis_tdata  <= rfg_write_value;
                layer_2_mosi_m_axis_tlast  <= rfg_write_last;
            end else begin
                layer_2_mosi_m_axis_tvalid <= 1'b0;
                layer_2_mosi_m_axis_tlast  <= 1'b0;
            end
            if(rfg_write && rfg_address==16'h57) begin
                layer_0_loopback_miso_m_axis_tvalid <= 1'b1;
                layer_0_loopback_miso_m_axis_tdata  <= rfg_write_value;
            end else begin
                layer_0_loopback_miso_m_axis_tvalid <= 1'b0;
            end
            if(rfg_write && rfg_address==16'h5c) begin
                layer_1_loopback_miso_m_axis_tvalid <= 1'b1;
                layer_1_loopback_miso_m_axis_tdata  <= rfg_write_value;
            end else begin
                layer_1_loopback_miso_m_axis_tvalid <= 1'b0;
            end
            if(rfg_write && rfg_address==16'h61) begin
                layer_2_loopback_miso_m_axis_tvalid <= 1'b1;
                layer_2_loopback_miso_m_axis_tdata  <= rfg_write_value;
            end else begin
                layer_2_loopback_miso_m_axis_tvalid <= 1'b0;
            end
            
            // Writes for HW Write only
            if(hk_xadc_temperature_write) begin
                hk_xadc_temperature_reg <= hk_xadc_temperature ;
            end
            if(hk_xadc_vccint_write) begin
                hk_xadc_vccint_reg <= hk_xadc_vccint ;
            end
            if(hk_adc_miso_fifo_read_size_write) begin
                hk_adc_miso_fifo_read_size_reg <= hk_adc_miso_fifo_read_size ;
            end
            if(layer_0_mosi_write_size_write) begin
                layer_0_mosi_write_size_reg <= layer_0_mosi_write_size ;
            end
            if(layer_1_mosi_write_size_write) begin
                layer_1_mosi_write_size_reg <= layer_1_mosi_write_size ;
            end
            if(layer_2_mosi_write_size_write) begin
                layer_2_mosi_write_size_reg <= layer_2_mosi_write_size ;
            end
            if(layer_0_loopback_miso_write_size_write) begin
                layer_0_loopback_miso_write_size_reg <= layer_0_loopback_miso_write_size ;
            end
            if(layer_1_loopback_miso_write_size_write) begin
                layer_1_loopback_miso_write_size_reg <= layer_1_loopback_miso_write_size ;
            end
            if(layer_2_loopback_miso_write_size_write) begin
                layer_2_loopback_miso_write_size_reg <= layer_2_loopback_miso_write_size ;
            end
            if(layer_0_loopback_mosi_read_size_write) begin
                layer_0_loopback_mosi_read_size_reg <= layer_0_loopback_mosi_read_size ;
            end
            if(layer_1_loopback_mosi_read_size_write) begin
                layer_1_loopback_mosi_read_size_reg <= layer_1_loopback_mosi_read_size ;
            end
            if(layer_2_loopback_mosi_read_size_write) begin
                layer_2_loopback_mosi_read_size_reg <= layer_2_loopback_mosi_read_size ;
            end
            if(layers_sr_crc_write) begin
                layers_sr_crc_reg <= layers_sr_crc ;
            end
            if(layers_sr_bytes_read_size_write) begin
                layers_sr_bytes_read_size_reg <= layers_sr_bytes_read_size ;
            end
            if(layers_readout_read_size_write) begin
                layers_readout_read_size_reg <= layers_readout_read_size ;
            end
            // Writes for Counter
            // Counter with interrupt on matching register: If the match register is written, reset the counter
            if((rfg_write && rfg_address==16'haa)) begin
                hk_conversion_trigger_reg <= 'd0;
            end
            else if(!(rfg_write && rfg_address==16'hd)) begin
                hk_conversion_trigger_reg <= hk_conversion_trigger_up ? hk_conversion_trigger_reg + 'd1 : hk_conversion_trigger_reg - 'd1 ;
            end
            
            // Counter with interrupt on matching register: Enable counting when match counter is reached, and set up-down to change counting direction
            if(( (hk_conversion_trigger_up && hk_conversion_trigger_reg == (hk_conversion_trigger_match_reg - 1)) || (!hk_conversion_trigger_up && hk_conversion_trigger_reg==1 )) ) begin
                hk_conversion_trigger_interrupt <= 1'b1;
                hk_conversion_trigger_up <= !hk_conversion_trigger_up;
            end else begin
                hk_conversion_trigger_interrupt <= 1'b0;
            end
            
            if(hk_stat_conversions_counter_enable) begin
                hk_stat_conversions_counter_reg <= hk_stat_conversions_counter_reg + 1 ;
            end
            if(!(rfg_write && rfg_address==16'h24) && layer_0_stat_frame_counter_enable) begin
                layer_0_stat_frame_counter_reg <= layer_0_stat_frame_counter_reg + 1 ;
            end
            if(!(rfg_write && rfg_address==16'h28) && layer_1_stat_frame_counter_enable) begin
                layer_1_stat_frame_counter_reg <= layer_1_stat_frame_counter_reg + 1 ;
            end
            if(!(rfg_write && rfg_address==16'h2c) && layer_2_stat_frame_counter_enable) begin
                layer_2_stat_frame_counter_reg <= layer_2_stat_frame_counter_reg + 1 ;
            end
            if(!(rfg_write && rfg_address==16'h30) && layer_0_stat_idle_counter_enable) begin
                layer_0_stat_idle_counter_reg <= layer_0_stat_idle_counter_reg + 1 ;
            end
            if(!(rfg_write && rfg_address==16'h34) && layer_1_stat_idle_counter_enable) begin
                layer_1_stat_idle_counter_reg <= layer_1_stat_idle_counter_reg + 1 ;
            end
            if(!(rfg_write && rfg_address==16'h38) && layer_2_stat_idle_counter_enable) begin
                layer_2_stat_idle_counter_reg <= layer_2_stat_idle_counter_reg + 1 ;
            end
            if(!(rfg_write && rfg_address==16'h3c) && layer_0_stat_wronglength_counter_enable) begin
                layer_0_stat_wronglength_counter_reg <= layer_0_stat_wronglength_counter_reg + 1 ;
            end
            if(!(rfg_write && rfg_address==16'h40) && layer_1_stat_wronglength_counter_enable) begin
                layer_1_stat_wronglength_counter_reg <= layer_1_stat_wronglength_counter_reg + 1 ;
            end
            if(!(rfg_write && rfg_address==16'h44) && layer_2_stat_wronglength_counter_enable) begin
                layer_2_stat_wronglength_counter_reg <= layer_2_stat_wronglength_counter_reg + 1 ;
            end
            // Counter with interrupt on matching register: If the match register is written, reset the counter
            if((rfg_write && rfg_address==16'hae)) begin
                layers_fpga_timestamp_divider_reg <= 'd0;
            end
            else if(!(rfg_write && rfg_address==16'h77) && layers_fpga_timestamp_divider_enable) begin
                layers_fpga_timestamp_divider_reg <= layers_fpga_timestamp_divider_up ? layers_fpga_timestamp_divider_reg + 'd1 : layers_fpga_timestamp_divider_reg - 'd1 ;
            end
            // Counter with interrupt on matching register: Enable counting when match counter is reached, and set up-down to change counting direction
            if(( (layers_fpga_timestamp_divider_up && layers_fpga_timestamp_divider_reg == (layers_fpga_timestamp_divider_match_reg - 1)) || (!layers_fpga_timestamp_divider_up && layers_fpga_timestamp_divider_reg==1 )) && layers_fpga_timestamp_divider_enable) begin
                layers_fpga_timestamp_divider_interrupt <= 1'b1;
                layers_fpga_timestamp_divider_up <= !layers_fpga_timestamp_divider_up;
            end else begin
                layers_fpga_timestamp_divider_interrupt <= 1'b0;
            end
            
        end
    end
    
    
    // Read for FIFO Slave
    // ---------------
    assign hk_adc_miso_fifo_s_axis_tready = rfg_read && rfg_address==16'h17;
    assign layer_0_loopback_mosi_s_axis_tready = rfg_read && rfg_address==16'h66;
    assign layer_1_loopback_mosi_s_axis_tready = rfg_read && rfg_address==16'h6b;
    assign layer_2_loopback_mosi_s_axis_tready = rfg_read && rfg_address==16'h70;
    assign layers_sr_bytes_s_axis_tready = rfg_read && rfg_address==16'h99;
    assign layers_readout_s_axis_tready = rfg_read && rfg_address==16'ha2;
    
    
    // Register Read
    // ---------------
    always_ff@(posedge clk) begin
        if (!resn) begin
            rfg_read_valid <= 0;
            rfg_read_value <= 0;
        end else begin
            // Read for simple registers
            case({rfg_read,rfg_address})
                {1'b1,16'h0}: begin
                    rfg_read_value <= hk_firmware_id_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h1}: begin
                    rfg_read_value <= hk_firmware_id_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h2}: begin
                    rfg_read_value <= hk_firmware_id_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h3}: begin
                    rfg_read_value <= hk_firmware_id_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h4}: begin
                    rfg_read_value <= hk_firmware_version_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h5}: begin
                    rfg_read_value <= hk_firmware_version_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h6}: begin
                    rfg_read_value <= hk_firmware_version_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h7}: begin
                    rfg_read_value <= hk_firmware_version_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h8}: begin
                    rfg_read_value <= clock_ctrl_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h9}: begin
                    rfg_read_value <= hk_xadc_temperature_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'ha}: begin
                    rfg_read_value <= hk_xadc_temperature_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'hb}: begin
                    rfg_read_value <= hk_xadc_vccint_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'hc}: begin
                    rfg_read_value <= hk_xadc_vccint_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'hd}: begin
                    rfg_read_value <= hk_conversion_trigger_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'he}: begin
                    rfg_read_value <= hk_conversion_trigger_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'hf}: begin
                    rfg_read_value <= hk_conversion_trigger_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h10}: begin
                    rfg_read_value <= hk_conversion_trigger_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h11}: begin
                    rfg_read_value <= hk_stat_conversions_counter_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h12}: begin
                    rfg_read_value <= hk_stat_conversions_counter_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h13}: begin
                    rfg_read_value <= hk_stat_conversions_counter_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h14}: begin
                    rfg_read_value <= hk_stat_conversions_counter_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h15}: begin
                    rfg_read_value <= hk_ctrl_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h17}: begin
                    rfg_read_value <= hk_adc_miso_fifo_s_axis_tvalid ? hk_adc_miso_fifo_s_axis_tdata : 16'hff;
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h18}: begin
                    rfg_read_value <= hk_adc_miso_fifo_read_size_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h19}: begin
                    rfg_read_value <= hk_adc_miso_fifo_read_size_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h1a}: begin
                    rfg_read_value <= hk_adc_miso_fifo_read_size_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h1b}: begin
                    rfg_read_value <= hk_adc_miso_fifo_read_size_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h1c}: begin
                    rfg_read_value <= spi_layers_ckdivider_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h1d}: begin
                    rfg_read_value <= spi_hk_ckdivider_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h1e}: begin
                    rfg_read_value <= layer_0_cfg_ctrl_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h1f}: begin
                    rfg_read_value <= layer_1_cfg_ctrl_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h20}: begin
                    rfg_read_value <= layer_2_cfg_ctrl_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h21}: begin
                    rfg_read_value <= layer_0_status_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h22}: begin
                    rfg_read_value <= layer_1_status_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h23}: begin
                    rfg_read_value <= layer_2_status_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h24}: begin
                    rfg_read_value <= layer_0_stat_frame_counter_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h25}: begin
                    rfg_read_value <= layer_0_stat_frame_counter_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h26}: begin
                    rfg_read_value <= layer_0_stat_frame_counter_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h27}: begin
                    rfg_read_value <= layer_0_stat_frame_counter_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h28}: begin
                    rfg_read_value <= layer_1_stat_frame_counter_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h29}: begin
                    rfg_read_value <= layer_1_stat_frame_counter_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h2a}: begin
                    rfg_read_value <= layer_1_stat_frame_counter_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h2b}: begin
                    rfg_read_value <= layer_1_stat_frame_counter_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h2c}: begin
                    rfg_read_value <= layer_2_stat_frame_counter_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h2d}: begin
                    rfg_read_value <= layer_2_stat_frame_counter_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h2e}: begin
                    rfg_read_value <= layer_2_stat_frame_counter_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h2f}: begin
                    rfg_read_value <= layer_2_stat_frame_counter_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h30}: begin
                    rfg_read_value <= layer_0_stat_idle_counter_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h31}: begin
                    rfg_read_value <= layer_0_stat_idle_counter_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h32}: begin
                    rfg_read_value <= layer_0_stat_idle_counter_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h33}: begin
                    rfg_read_value <= layer_0_stat_idle_counter_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h34}: begin
                    rfg_read_value <= layer_1_stat_idle_counter_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h35}: begin
                    rfg_read_value <= layer_1_stat_idle_counter_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h36}: begin
                    rfg_read_value <= layer_1_stat_idle_counter_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h37}: begin
                    rfg_read_value <= layer_1_stat_idle_counter_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h38}: begin
                    rfg_read_value <= layer_2_stat_idle_counter_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h39}: begin
                    rfg_read_value <= layer_2_stat_idle_counter_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h3a}: begin
                    rfg_read_value <= layer_2_stat_idle_counter_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h3b}: begin
                    rfg_read_value <= layer_2_stat_idle_counter_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h3c}: begin
                    rfg_read_value <= layer_0_stat_wronglength_counter_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h3d}: begin
                    rfg_read_value <= layer_0_stat_wronglength_counter_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h3e}: begin
                    rfg_read_value <= layer_0_stat_wronglength_counter_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h3f}: begin
                    rfg_read_value <= layer_0_stat_wronglength_counter_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h40}: begin
                    rfg_read_value <= layer_1_stat_wronglength_counter_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h41}: begin
                    rfg_read_value <= layer_1_stat_wronglength_counter_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h42}: begin
                    rfg_read_value <= layer_1_stat_wronglength_counter_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h43}: begin
                    rfg_read_value <= layer_1_stat_wronglength_counter_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h44}: begin
                    rfg_read_value <= layer_2_stat_wronglength_counter_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h45}: begin
                    rfg_read_value <= layer_2_stat_wronglength_counter_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h46}: begin
                    rfg_read_value <= layer_2_stat_wronglength_counter_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h47}: begin
                    rfg_read_value <= layer_2_stat_wronglength_counter_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h49}: begin
                    rfg_read_value <= layer_0_mosi_write_size_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h4a}: begin
                    rfg_read_value <= layer_0_mosi_write_size_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h4b}: begin
                    rfg_read_value <= layer_0_mosi_write_size_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h4c}: begin
                    rfg_read_value <= layer_0_mosi_write_size_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h4e}: begin
                    rfg_read_value <= layer_1_mosi_write_size_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h4f}: begin
                    rfg_read_value <= layer_1_mosi_write_size_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h50}: begin
                    rfg_read_value <= layer_1_mosi_write_size_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h51}: begin
                    rfg_read_value <= layer_1_mosi_write_size_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h53}: begin
                    rfg_read_value <= layer_2_mosi_write_size_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h54}: begin
                    rfg_read_value <= layer_2_mosi_write_size_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h55}: begin
                    rfg_read_value <= layer_2_mosi_write_size_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h56}: begin
                    rfg_read_value <= layer_2_mosi_write_size_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h58}: begin
                    rfg_read_value <= layer_0_loopback_miso_write_size_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h59}: begin
                    rfg_read_value <= layer_0_loopback_miso_write_size_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h5a}: begin
                    rfg_read_value <= layer_0_loopback_miso_write_size_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h5b}: begin
                    rfg_read_value <= layer_0_loopback_miso_write_size_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h5d}: begin
                    rfg_read_value <= layer_1_loopback_miso_write_size_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h5e}: begin
                    rfg_read_value <= layer_1_loopback_miso_write_size_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h5f}: begin
                    rfg_read_value <= layer_1_loopback_miso_write_size_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h60}: begin
                    rfg_read_value <= layer_1_loopback_miso_write_size_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h62}: begin
                    rfg_read_value <= layer_2_loopback_miso_write_size_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h63}: begin
                    rfg_read_value <= layer_2_loopback_miso_write_size_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h64}: begin
                    rfg_read_value <= layer_2_loopback_miso_write_size_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h65}: begin
                    rfg_read_value <= layer_2_loopback_miso_write_size_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h66}: begin
                    rfg_read_value <= layer_0_loopback_mosi_s_axis_tvalid ? layer_0_loopback_mosi_s_axis_tdata : 16'hff;
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h67}: begin
                    rfg_read_value <= layer_0_loopback_mosi_read_size_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h68}: begin
                    rfg_read_value <= layer_0_loopback_mosi_read_size_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h69}: begin
                    rfg_read_value <= layer_0_loopback_mosi_read_size_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h6a}: begin
                    rfg_read_value <= layer_0_loopback_mosi_read_size_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h6b}: begin
                    rfg_read_value <= layer_1_loopback_mosi_s_axis_tvalid ? layer_1_loopback_mosi_s_axis_tdata : 16'hff;
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h6c}: begin
                    rfg_read_value <= layer_1_loopback_mosi_read_size_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h6d}: begin
                    rfg_read_value <= layer_1_loopback_mosi_read_size_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h6e}: begin
                    rfg_read_value <= layer_1_loopback_mosi_read_size_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h6f}: begin
                    rfg_read_value <= layer_1_loopback_mosi_read_size_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h70}: begin
                    rfg_read_value <= layer_2_loopback_mosi_s_axis_tvalid ? layer_2_loopback_mosi_s_axis_tdata : 16'hff;
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h71}: begin
                    rfg_read_value <= layer_2_loopback_mosi_read_size_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h72}: begin
                    rfg_read_value <= layer_2_loopback_mosi_read_size_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h73}: begin
                    rfg_read_value <= layer_2_loopback_mosi_read_size_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h74}: begin
                    rfg_read_value <= layer_2_loopback_mosi_read_size_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h75}: begin
                    rfg_read_value <= layers_fpga_timestamp_ctrl_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h76}: begin
                    rfg_read_value <= layers_fpga_timestamp_ctrl_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h77}: begin
                    rfg_read_value <= layers_fpga_timestamp_divider_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h78}: begin
                    rfg_read_value <= layers_fpga_timestamp_divider_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h79}: begin
                    rfg_read_value <= layers_fpga_timestamp_divider_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h7a}: begin
                    rfg_read_value <= layers_fpga_timestamp_divider_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h7b}: begin
                    rfg_read_value <= layers_fpga_timestamp_counter[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h7c}: begin
                    rfg_read_value <= layers_fpga_timestamp_counter[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h7d}: begin
                    rfg_read_value <= layers_fpga_timestamp_counter[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h7e}: begin
                    rfg_read_value <= layers_fpga_timestamp_counter[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h7f}: begin
                    rfg_read_value <= layers_fpga_timestamp_counter[39:32];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h80}: begin
                    rfg_read_value <= layers_fpga_timestamp_counter[47:40];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h81}: begin
                    rfg_read_value <= layers_fpga_timestamp_counter[55:48];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h82}: begin
                    rfg_read_value <= layers_fpga_timestamp_counter[63:56];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h83}: begin
                    rfg_read_value <= layers_fpga_timestamp_forced_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h84}: begin
                    rfg_read_value <= layers_fpga_timestamp_forced_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h85}: begin
                    rfg_read_value <= layers_fpga_timestamp_forced_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h86}: begin
                    rfg_read_value <= layers_fpga_timestamp_forced_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h87}: begin
                    rfg_read_value <= layers_fpga_timestamp_forced_reg[39:32];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h88}: begin
                    rfg_read_value <= layers_fpga_timestamp_forced_reg[47:40];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h89}: begin
                    rfg_read_value <= layers_fpga_timestamp_forced_reg[55:48];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h8a}: begin
                    rfg_read_value <= layers_fpga_timestamp_forced_reg[63:56];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h8b}: begin
                    rfg_read_value <= layers_tlu_trigger_delay_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h8c}: begin
                    rfg_read_value <= layers_tlu_trigger_delay_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h8d}: begin
                    rfg_read_value <= layers_tlu_busy_duration_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h8e}: begin
                    rfg_read_value <= layers_tlu_busy_duration_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h8f}: begin
                    rfg_read_value <= layers_cfg_nodata_continue_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h90}: begin
                    rfg_read_value <= layers_sr_out_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h91}: begin
                    rfg_read_value <= layers_sr_in_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h92}: begin
                    rfg_read_value <= layers_sr_rb_ctrl_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h93}: begin
                    rfg_read_value <= layers_sr_crc_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h94}: begin
                    rfg_read_value <= layers_sr_crc_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h95}: begin
                    rfg_read_value <= layers_sr_crc_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h96}: begin
                    rfg_read_value <= layers_sr_crc_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h97}: begin
                    rfg_read_value <= layers_sr_crc_reg[39:32];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h98}: begin
                    rfg_read_value <= layers_sr_crc_reg[47:40];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h99}: begin
                    rfg_read_value <= layers_sr_bytes_s_axis_tvalid ? layers_sr_bytes_s_axis_tdata : 16'hff;
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h9a}: begin
                    rfg_read_value <= layers_sr_bytes_read_size_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h9b}: begin
                    rfg_read_value <= layers_sr_bytes_read_size_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h9c}: begin
                    rfg_read_value <= layers_sr_bytes_read_size_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h9d}: begin
                    rfg_read_value <= layers_sr_bytes_read_size_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h9e}: begin
                    rfg_read_value <= layers_inj_ctrl_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'h9f}: begin
                    rfg_read_value <= {4'd0,layers_inj_waddr_reg[3:0]};
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'ha0}: begin
                    rfg_read_value <= layers_inj_wdata_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'ha1}: begin
                    rfg_read_value <= layers_readout_ctrl_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'ha2}: begin
                    rfg_read_value <= layers_readout_s_axis_tvalid ? layers_readout_s_axis_tdata : 16'hff;
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'ha3}: begin
                    rfg_read_value <= layers_readout_read_size_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'ha4}: begin
                    rfg_read_value <= layers_readout_read_size_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'ha5}: begin
                    rfg_read_value <= layers_readout_read_size_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'ha6}: begin
                    rfg_read_value <= layers_readout_read_size_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'ha7}: begin
                    rfg_read_value <= io_ctrl_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'ha8}: begin
                    rfg_read_value <= io_led_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'ha9}: begin
                    rfg_read_value <= gecco_sr_ctrl_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'haa}: begin
                    rfg_read_value <= hk_conversion_trigger_match_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'hab}: begin
                    rfg_read_value <= hk_conversion_trigger_match_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'hac}: begin
                    rfg_read_value <= hk_conversion_trigger_match_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'had}: begin
                    rfg_read_value <= hk_conversion_trigger_match_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'hae}: begin
                    rfg_read_value <= layers_fpga_timestamp_divider_match_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'haf}: begin
                    rfg_read_value <= layers_fpga_timestamp_divider_match_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'hb0}: begin
                    rfg_read_value <= layers_fpga_timestamp_divider_match_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,16'hb1}: begin
                    rfg_read_value <= layers_fpga_timestamp_divider_match_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                default: begin
                    rfg_read_valid <= 0 ;
                end
            endcase
            
        end
    end
    
    
    always_ff@(posedge spi_layers_ckdivider_source_clk) begin
        if (!spi_layers_ckdivider_source_resn) begin
            spi_layers_ckdivider_divided_clk <= 1'b0;
            spi_layers_ckdivider_counter <= 16'h00;
        end else begin
            if (spi_layers_ckdivider_counter==spi_layers_ckdivider_reg) begin
                spi_layers_ckdivider_divided_clk <= !spi_layers_ckdivider_divided_clk;
                spi_layers_ckdivider_counter <= 16'h00;
            end else begin
                spi_layers_ckdivider_counter <= spi_layers_ckdivider_counter+1;
            end
        end
    end
    reg [7:0] spi_layers_ckdivider_divided_resn_delay;
    assign spi_layers_ckdivider_divided_resn = spi_layers_ckdivider_divided_resn_delay[7];
    always_ff@(posedge spi_layers_ckdivider_divided_clk or negedge spi_layers_ckdivider_source_resn) begin
        if (!spi_layers_ckdivider_source_resn) begin
            spi_layers_ckdivider_divided_resn_delay <= 16'h00;
        end else begin
            spi_layers_ckdivider_divided_resn_delay <= {spi_layers_ckdivider_divided_resn_delay[6:0],1'b1};
        end
    end
    
    
    always_ff@(posedge spi_hk_ckdivider_source_clk) begin
        if (!spi_hk_ckdivider_source_resn) begin
            spi_hk_ckdivider_divided_clk <= 1'b0;
            spi_hk_ckdivider_counter <= 16'h00;
        end else begin
            if (spi_hk_ckdivider_counter==spi_hk_ckdivider_reg) begin
                spi_hk_ckdivider_divided_clk <= !spi_hk_ckdivider_divided_clk;
                spi_hk_ckdivider_counter <= 16'h00;
            end else begin
                spi_hk_ckdivider_counter <= spi_hk_ckdivider_counter+1;
            end
        end
    end
    reg [7:0] spi_hk_ckdivider_divided_resn_delay;
    assign spi_hk_ckdivider_divided_resn = spi_hk_ckdivider_divided_resn_delay[7];
    always_ff@(posedge spi_hk_ckdivider_divided_clk or negedge spi_hk_ckdivider_source_resn) begin
        if (!spi_hk_ckdivider_source_resn) begin
            spi_hk_ckdivider_divided_resn_delay <= 16'h00;
        end else begin
            spi_hk_ckdivider_divided_resn_delay <= {spi_hk_ckdivider_divided_resn_delay[6:0],1'b1};
        end
    end
    
    
    
    
    // Simple Address valid bit out
    always_ff@(posedge clk) begin
        if (!resn) begin
            rfg_address_valid <= 'd0;
        end else begin
            rfg_address_valid <= rfg_address >= 'd0 && rfg_address <= 'hb1;
        end
    end
    
    
endmodule
