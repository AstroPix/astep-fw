module main_rfg(
    // IO
    // RFG R/W Interface,
    // --------------------,
    input  wire                clk,
    input  wire                resn,
    input  wire  [7:0]         rfg_address,
    input  wire  [7:0]         rfg_write_value,
    input  wire                rfg_write,
    input  wire                rfg_write_last,
    input  wire                rfg_read,
    output reg                 rfg_read_valid,
    output reg  [7:0]          rfg_read_value,

    input  wire [15:0]            hk_xadc_temperature,
    input  wire                  hk_xadc_temperature_write,
    input  wire [15:0]            hk_xadc_vccint,
    input  wire                  hk_xadc_vccint_write,
    output wire [31:0]            hk_conversion_trigger,
    output  reg                  hk_conversion_trigger_interrupt,
    input   wire                  hk_stat_conversions_counter_enable,
    output wire [7:0]            hk_ctrl,
    output wire                  hk_ctrl_select_adc,
    // AXIS Master interface to write to FIFO hk_adcdac_mosi_fifo,
    // --------------------,
    output reg [7:0]             hk_adcdac_mosi_fifo_m_axis_tdata,
    output reg                   hk_adcdac_mosi_fifo_m_axis_tvalid,
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
    output reg             spi_layers_ckdivider_divided_clk,
    output wire            spi_layers_ckdivider_divided_resn,
    input  wire            spi_hk_ckdivider_source_clk,
    input  wire            spi_hk_ckdivider_source_resn,
    output reg             spi_hk_ckdivider_divided_clk,
    output wire            spi_hk_ckdivider_divided_resn,
    output wire [7:0]            layer_0_cfg_ctrl,
    output wire                  layer_0_cfg_ctrl_hold,
    output wire                  layer_0_cfg_ctrl_reset,
    output wire                  layer_0_cfg_ctrl_disable_autoread,
    output wire                  layer_0_cfg_ctrl_cs,
    output wire                  layer_0_cfg_ctrl_disable_miso,
    output wire [7:0]            layer_1_cfg_ctrl,
    output wire                  layer_1_cfg_ctrl_hold,
    output wire                  layer_1_cfg_ctrl_reset,
    output wire                  layer_1_cfg_ctrl_disable_autoread,
    output wire                  layer_1_cfg_ctrl_cs,
    output wire                  layer_1_cfg_ctrl_disable_miso,
    output wire [7:0]            layer_2_cfg_ctrl,
    output wire                  layer_2_cfg_ctrl_hold,
    output wire                  layer_2_cfg_ctrl_reset,
    output wire                  layer_2_cfg_ctrl_disable_autoread,
    output wire                  layer_2_cfg_ctrl_cs,
    output wire                  layer_2_cfg_ctrl_disable_miso,
    output wire [7:0]            layer_0_status,
    input  wire                  layer_0_status_interruptn,
    input  wire                  layer_0_status_frame_decoding,
    output wire [7:0]            layer_1_status,
    input  wire                  layer_1_status_interruptn,
    input  wire                  layer_1_status_frame_decoding,
    output wire [7:0]            layer_2_status,
    input  wire                  layer_2_status_interruptn,
    input  wire                  layer_2_status_frame_decoding,
    input   wire                  layer_0_stat_frame_counter_enable,
    input   wire                  layer_1_stat_frame_counter_enable,
    input   wire                  layer_2_stat_frame_counter_enable,
    input   wire                  layer_0_stat_idle_counter_enable,
    input   wire                  layer_1_stat_idle_counter_enable,
    input   wire                  layer_2_stat_idle_counter_enable,
    // AXIS Master interface to write to FIFO layer_0_mosi,
    // --------------------,
    output reg [7:0]             layer_0_mosi_m_axis_tdata,
    output reg                   layer_0_mosi_m_axis_tvalid,
    input  wire                  layer_0_mosi_m_axis_tready,
    output reg            layer_0_mosi_m_axis_tlast,
    input  wire [31:0]            layer_0_mosi_write_size,
    input  wire                  layer_0_mosi_write_size_write,
    // AXIS Master interface to write to FIFO layer_1_mosi,
    // --------------------,
    output reg [7:0]             layer_1_mosi_m_axis_tdata,
    output reg                   layer_1_mosi_m_axis_tvalid,
    input  wire                  layer_1_mosi_m_axis_tready,
    output reg            layer_1_mosi_m_axis_tlast,
    input  wire [31:0]            layer_1_mosi_write_size,
    input  wire                  layer_1_mosi_write_size_write,
    // AXIS Master interface to write to FIFO layer_2_mosi,
    // --------------------,
    output reg [7:0]             layer_2_mosi_m_axis_tdata,
    output reg                   layer_2_mosi_m_axis_tvalid,
    input  wire                  layer_2_mosi_m_axis_tready,
    output reg            layer_2_mosi_m_axis_tlast,
    input  wire [31:0]            layer_2_mosi_write_size,
    input  wire                  layer_2_mosi_write_size_write,
    output wire [31:0]            layers_cfg_frame_tag_counter,
    input   wire                  layers_cfg_frame_tag_counter_enable,
    output wire [7:0]            layers_cfg_nodata_continue,
    output wire [7:0]            layers_sr_out,
    output wire                  layers_sr_out_ck1,
    output wire                  layers_sr_out_ck2,
    output wire                  layers_sr_out_sin,
    output wire                  layers_sr_out_ld0,
    output wire                  layers_sr_out_ld1,
    output wire                  layers_sr_out_ld2,
    output wire [7:0]            layers_sr_in,
    output wire                  layers_sr_in_rb,
    input  wire                  layers_sr_in_sout0,
    input  wire                  layers_sr_in_sout1,
    input  wire                  layers_sr_in_sout2,
    output wire [7:0]            layers_inj_ctrl,
    output wire                  layers_inj_ctrl_reset,
    output wire                  layers_inj_ctrl_suspend,
    output wire                  layers_inj_ctrl_synced,
    output wire                  layers_inj_ctrl_trigger,
    output wire                  layers_inj_ctrl_write,
    input  wire                  layers_inj_ctrl_done,
    input  wire                  layers_inj_ctrl_running,
    output wire [3:0]            layers_inj_waddr,
    output wire [7:0]            layers_inj_wdata,
    // AXIS Slave interface to read from FIFO layers_readout,
    // --------------------,
    input  wire [7:0]            layers_readout_s_axis_tdata,
    input  wire                  layers_readout_s_axis_tvalid,
    output wire                  layers_readout_s_axis_tready,
    input  wire [31:0]            layers_readout_read_size,
    input  wire                  layers_readout_read_size_write,
    output wire [7:0]            io_ctrl,
    output wire                  io_ctrl_sample_clock_enable,
    output wire                  io_ctrl_timestamp_clock_enable,
    output wire                  io_ctrl_gecco_sample_clock_se,
    output wire                  io_ctrl_gecco_inj_enable,
    output wire [7:0]            io_led,
    output wire [7:0]            gecco_sr_ctrl,
    output wire                  gecco_sr_ctrl_ck,
    output wire                  gecco_sr_ctrl_sin,
    output wire                  gecco_sr_ctrl_ld,
    output wire [31:0]            hk_conversion_trigger_match
    );
    
    
    reg [15:0] hk_xadc_temperature_reg;
    reg [15:0] hk_xadc_vccint_reg;
    reg hk_conversion_trigger_up;
    reg [31:0] hk_adc_miso_fifo_read_size_reg;
    // Clock Divider spi_layers_ckdivider
    reg [7:0] spi_layers_ckdivider_counter;
    reg [7:0] spi_layers_ckdivider_reg;
    // Clock Divider spi_hk_ckdivider
    reg [7:0] spi_hk_ckdivider_counter;
    reg [7:0] spi_hk_ckdivider_reg;
    reg [31:0] layer_0_mosi_write_size_reg;
    reg [31:0] layer_1_mosi_write_size_reg;
    reg [31:0] layer_2_mosi_write_size_reg;
    reg [31:0] layers_readout_read_size_reg;
    
    
    // Registers I/O assignments
    // ---------------
    reg [31:0] hk_firmware_id_reg;
    
    reg [31:0] hk_firmware_version_reg;
    
    reg [31:0] hk_conversion_trigger_reg;
    assign hk_conversion_trigger = hk_conversion_trigger_reg;
    
    reg [31:0] hk_stat_conversions_counter_reg;
    
    reg [7:0] hk_ctrl_reg;
    assign hk_ctrl = hk_ctrl_reg;
    
    reg [7:0] layer_0_cfg_ctrl_reg;
    assign layer_0_cfg_ctrl = layer_0_cfg_ctrl_reg;
    
    reg [7:0] layer_1_cfg_ctrl_reg;
    assign layer_1_cfg_ctrl = layer_1_cfg_ctrl_reg;
    
    reg [7:0] layer_2_cfg_ctrl_reg;
    assign layer_2_cfg_ctrl = layer_2_cfg_ctrl_reg;
    
    reg [7:0] layer_0_status_reg;
    assign layer_0_status = layer_0_status_reg;
    
    reg [7:0] layer_1_status_reg;
    assign layer_1_status = layer_1_status_reg;
    
    reg [7:0] layer_2_status_reg;
    assign layer_2_status = layer_2_status_reg;
    
    reg [31:0] layer_0_stat_frame_counter_reg;
    
    reg [31:0] layer_1_stat_frame_counter_reg;
    
    reg [31:0] layer_2_stat_frame_counter_reg;
    
    reg [31:0] layer_0_stat_idle_counter_reg;
    
    reg [31:0] layer_1_stat_idle_counter_reg;
    
    reg [31:0] layer_2_stat_idle_counter_reg;
    
    reg [31:0] layers_cfg_frame_tag_counter_reg;
    assign layers_cfg_frame_tag_counter = layers_cfg_frame_tag_counter_reg;
    
    reg [7:0] layers_cfg_nodata_continue_reg;
    assign layers_cfg_nodata_continue = layers_cfg_nodata_continue_reg;
    
    reg [7:0] layers_sr_out_reg;
    assign layers_sr_out = layers_sr_out_reg;
    
    reg [7:0] layers_sr_in_reg;
    assign layers_sr_in = layers_sr_in_reg;
    
    reg [7:0] layers_inj_ctrl_reg;
    assign layers_inj_ctrl = layers_inj_ctrl_reg;
    
    reg [3:0] layers_inj_waddr_reg;
    assign layers_inj_waddr = layers_inj_waddr_reg;
    
    reg [7:0] layers_inj_wdata_reg;
    assign layers_inj_wdata = layers_inj_wdata_reg;
    
    reg [7:0] io_ctrl_reg;
    assign io_ctrl = io_ctrl_reg;
    
    reg [7:0] io_led_reg;
    assign io_led = io_led_reg;
    
    reg [7:0] gecco_sr_ctrl_reg;
    assign gecco_sr_ctrl = gecco_sr_ctrl_reg;
    
    reg [31:0] hk_conversion_trigger_match_reg;
    assign hk_conversion_trigger_match = hk_conversion_trigger_match_reg;
    
    
    
    // Register Bits assignments
    // ---------------
    assign hk_ctrl_select_adc = hk_ctrl_reg[0];
    assign layer_0_cfg_ctrl_hold = layer_0_cfg_ctrl_reg[0];
    assign layer_0_cfg_ctrl_reset = layer_0_cfg_ctrl_reg[1];
    assign layer_0_cfg_ctrl_disable_autoread = layer_0_cfg_ctrl_reg[2];
    assign layer_0_cfg_ctrl_cs = layer_0_cfg_ctrl_reg[3];
    assign layer_0_cfg_ctrl_disable_miso = layer_0_cfg_ctrl_reg[4];
    assign layer_1_cfg_ctrl_hold = layer_1_cfg_ctrl_reg[0];
    assign layer_1_cfg_ctrl_reset = layer_1_cfg_ctrl_reg[1];
    assign layer_1_cfg_ctrl_disable_autoread = layer_1_cfg_ctrl_reg[2];
    assign layer_1_cfg_ctrl_cs = layer_1_cfg_ctrl_reg[3];
    assign layer_1_cfg_ctrl_disable_miso = layer_1_cfg_ctrl_reg[4];
    assign layer_2_cfg_ctrl_hold = layer_2_cfg_ctrl_reg[0];
    assign layer_2_cfg_ctrl_reset = layer_2_cfg_ctrl_reg[1];
    assign layer_2_cfg_ctrl_disable_autoread = layer_2_cfg_ctrl_reg[2];
    assign layer_2_cfg_ctrl_cs = layer_2_cfg_ctrl_reg[3];
    assign layer_2_cfg_ctrl_disable_miso = layer_2_cfg_ctrl_reg[4];
    assign layers_sr_out_ck1 = layers_sr_out_reg[0];
    assign layers_sr_out_ck2 = layers_sr_out_reg[1];
    assign layers_sr_out_sin = layers_sr_out_reg[2];
    assign layers_sr_out_ld0 = layers_sr_out_reg[3];
    assign layers_sr_out_ld1 = layers_sr_out_reg[4];
    assign layers_sr_out_ld2 = layers_sr_out_reg[5];
    assign layers_sr_in_rb = layers_sr_in_reg[0];
    assign layers_inj_ctrl_reset = layers_inj_ctrl_reg[0];
    assign layers_inj_ctrl_suspend = layers_inj_ctrl_reg[1];
    assign layers_inj_ctrl_synced = layers_inj_ctrl_reg[2];
    assign layers_inj_ctrl_trigger = layers_inj_ctrl_reg[3];
    assign layers_inj_ctrl_write = layers_inj_ctrl_reg[4];
    assign io_ctrl_sample_clock_enable = io_ctrl_reg[0];
    assign io_ctrl_timestamp_clock_enable = io_ctrl_reg[1];
    assign io_ctrl_gecco_sample_clock_se = io_ctrl_reg[2];
    assign io_ctrl_gecco_inj_enable = io_ctrl_reg[3];
    assign gecco_sr_ctrl_ck = gecco_sr_ctrl_reg[0];
    assign gecco_sr_ctrl_sin = gecco_sr_ctrl_reg[1];
    assign gecco_sr_ctrl_ld = gecco_sr_ctrl_reg[2];
    
    
    // Register Writes
    // ---------------
    always@(posedge clk) begin
        if (!resn) begin
            hk_firmware_id_reg <= `RFG_FW_ID;
            hk_firmware_version_reg <= `RFG_FW_BUILD;
            hk_xadc_temperature_reg <= 0;
            hk_xadc_vccint_reg <= 0;
            hk_conversion_trigger_reg <= 0;
            hk_conversion_trigger_up <= 1'b1;
            hk_stat_conversions_counter_reg <= 0;
            hk_ctrl_reg <= 0;
            hk_adcdac_mosi_fifo_m_axis_tvalid <= 1'b0;
            hk_adcdac_mosi_fifo_m_axis_tlast  <= 1'b0;
            hk_adc_miso_fifo_read_size_reg <= 0;
            spi_layers_ckdivider_reg <= 8'h4;
            spi_hk_ckdivider_reg <= 8'h4;
            layer_0_cfg_ctrl_reg <= 8'b00000111;
            layer_1_cfg_ctrl_reg <= 8'b00000111;
            layer_2_cfg_ctrl_reg <= 8'b00000111;
            layer_0_status_reg <= 0;
            layer_1_status_reg <= 0;
            layer_2_status_reg <= 0;
            layer_0_stat_frame_counter_reg <= 0;
            layer_1_stat_frame_counter_reg <= 0;
            layer_2_stat_frame_counter_reg <= 0;
            layer_0_stat_idle_counter_reg <= 0;
            layer_1_stat_idle_counter_reg <= 0;
            layer_2_stat_idle_counter_reg <= 0;
            layer_0_mosi_m_axis_tvalid <= 1'b0;
            layer_0_mosi_m_axis_tlast  <= 1'b0;
            layer_0_mosi_write_size_reg <= 0;
            layer_1_mosi_m_axis_tvalid <= 1'b0;
            layer_1_mosi_m_axis_tlast  <= 1'b0;
            layer_1_mosi_write_size_reg <= 0;
            layer_2_mosi_m_axis_tvalid <= 1'b0;
            layer_2_mosi_m_axis_tlast  <= 1'b0;
            layer_2_mosi_write_size_reg <= 0;
            layers_cfg_frame_tag_counter_reg <= 0;
            layers_cfg_nodata_continue_reg <= 8'd5;
            layers_sr_out_reg <= 0;
            layers_sr_in_reg <= 0;
            layers_inj_ctrl_reg <= 8'b00000110;
            layers_inj_waddr_reg <= 0;
            layers_inj_wdata_reg <= 0;
            layers_readout_read_size_reg <= 0;
            io_ctrl_reg <= 8'b00001000;
            io_led_reg <= 0;
            gecco_sr_ctrl_reg <= 0;
            hk_conversion_trigger_match_reg <= 32'd10;
        end else begin
            
            
            // Single in bits are always sampled
            layer_0_status_reg[0] <= layer_0_status_interruptn;
            layer_0_status_reg[1] <= layer_0_status_frame_decoding;
            layer_1_status_reg[0] <= layer_1_status_interruptn;
            layer_1_status_reg[1] <= layer_1_status_frame_decoding;
            layer_2_status_reg[0] <= layer_2_status_interruptn;
            layer_2_status_reg[1] <= layer_2_status_frame_decoding;
            layers_sr_in_reg[1] <= layers_sr_in_sout0;
            layers_sr_in_reg[2] <= layers_sr_in_sout1;
            layers_sr_in_reg[3] <= layers_sr_in_sout2;
            layers_inj_ctrl_reg[5] <= layers_inj_ctrl_done;
            layers_inj_ctrl_reg[6] <= layers_inj_ctrl_running;
            
            
            // Write for simple registers
            case({rfg_write,rfg_address})
                {1'b1,8'hc}: begin
                    hk_conversion_trigger_reg[7:0] <= rfg_write_value;
                end
                {1'b1,8'hd}: begin
                    hk_conversion_trigger_reg[15:8] <= rfg_write_value;
                end
                {1'b1,8'he}: begin
                    hk_conversion_trigger_reg[23:16] <= rfg_write_value;
                end
                {1'b1,8'hf}: begin
                    hk_conversion_trigger_reg[31:24] <= rfg_write_value;
                end
                {1'b1,8'h14}: begin
                    hk_ctrl_reg[7:0] <= rfg_write_value;
                end
                {1'b1,8'h1b}: begin
                    spi_layers_ckdivider_reg <= rfg_write_value;
                end
                {1'b1,8'h1c}: begin
                    spi_hk_ckdivider_reg <= rfg_write_value;
                end
                {1'b1,8'h1d}: begin
                    layer_0_cfg_ctrl_reg[7:0] <= rfg_write_value;
                end
                {1'b1,8'h1e}: begin
                    layer_1_cfg_ctrl_reg[7:0] <= rfg_write_value;
                end
                {1'b1,8'h1f}: begin
                    layer_2_cfg_ctrl_reg[7:0] <= rfg_write_value;
                end
                {1'b1,8'h23}: begin
                    layer_0_stat_frame_counter_reg[7:0] <= rfg_write_value;
                end
                {1'b1,8'h24}: begin
                    layer_0_stat_frame_counter_reg[15:8] <= rfg_write_value;
                end
                {1'b1,8'h25}: begin
                    layer_0_stat_frame_counter_reg[23:16] <= rfg_write_value;
                end
                {1'b1,8'h26}: begin
                    layer_0_stat_frame_counter_reg[31:24] <= rfg_write_value;
                end
                {1'b1,8'h27}: begin
                    layer_1_stat_frame_counter_reg[7:0] <= rfg_write_value;
                end
                {1'b1,8'h28}: begin
                    layer_1_stat_frame_counter_reg[15:8] <= rfg_write_value;
                end
                {1'b1,8'h29}: begin
                    layer_1_stat_frame_counter_reg[23:16] <= rfg_write_value;
                end
                {1'b1,8'h2a}: begin
                    layer_1_stat_frame_counter_reg[31:24] <= rfg_write_value;
                end
                {1'b1,8'h2b}: begin
                    layer_2_stat_frame_counter_reg[7:0] <= rfg_write_value;
                end
                {1'b1,8'h2c}: begin
                    layer_2_stat_frame_counter_reg[15:8] <= rfg_write_value;
                end
                {1'b1,8'h2d}: begin
                    layer_2_stat_frame_counter_reg[23:16] <= rfg_write_value;
                end
                {1'b1,8'h2e}: begin
                    layer_2_stat_frame_counter_reg[31:24] <= rfg_write_value;
                end
                {1'b1,8'h2f}: begin
                    layer_0_stat_idle_counter_reg[7:0] <= rfg_write_value;
                end
                {1'b1,8'h30}: begin
                    layer_0_stat_idle_counter_reg[15:8] <= rfg_write_value;
                end
                {1'b1,8'h31}: begin
                    layer_0_stat_idle_counter_reg[23:16] <= rfg_write_value;
                end
                {1'b1,8'h32}: begin
                    layer_0_stat_idle_counter_reg[31:24] <= rfg_write_value;
                end
                {1'b1,8'h33}: begin
                    layer_1_stat_idle_counter_reg[7:0] <= rfg_write_value;
                end
                {1'b1,8'h34}: begin
                    layer_1_stat_idle_counter_reg[15:8] <= rfg_write_value;
                end
                {1'b1,8'h35}: begin
                    layer_1_stat_idle_counter_reg[23:16] <= rfg_write_value;
                end
                {1'b1,8'h36}: begin
                    layer_1_stat_idle_counter_reg[31:24] <= rfg_write_value;
                end
                {1'b1,8'h37}: begin
                    layer_2_stat_idle_counter_reg[7:0] <= rfg_write_value;
                end
                {1'b1,8'h38}: begin
                    layer_2_stat_idle_counter_reg[15:8] <= rfg_write_value;
                end
                {1'b1,8'h39}: begin
                    layer_2_stat_idle_counter_reg[23:16] <= rfg_write_value;
                end
                {1'b1,8'h3a}: begin
                    layer_2_stat_idle_counter_reg[31:24] <= rfg_write_value;
                end
                {1'b1,8'h4a}: begin
                    layers_cfg_frame_tag_counter_reg[7:0] <= rfg_write_value;
                end
                {1'b1,8'h4b}: begin
                    layers_cfg_frame_tag_counter_reg[15:8] <= rfg_write_value;
                end
                {1'b1,8'h4c}: begin
                    layers_cfg_frame_tag_counter_reg[23:16] <= rfg_write_value;
                end
                {1'b1,8'h4d}: begin
                    layers_cfg_frame_tag_counter_reg[31:24] <= rfg_write_value;
                end
                {1'b1,8'h4e}: begin
                    layers_cfg_nodata_continue_reg[7:0] <= rfg_write_value;
                end
                {1'b1,8'h4f}: begin
                    layers_sr_out_reg[7:0] <= rfg_write_value;
                end
                {1'b1,8'h50}: begin
                    layers_sr_in_reg[7:0] <= rfg_write_value;
                end
                {1'b1,8'h51}: begin
                    layers_inj_ctrl_reg[7:0] <= rfg_write_value;
                end
                {1'b1,8'h52}: begin
                    layers_inj_waddr_reg[3:0] <= rfg_write_value[3:0];
                end
                {1'b1,8'h53}: begin
                    layers_inj_wdata_reg[7:0] <= rfg_write_value;
                end
                {1'b1,8'h59}: begin
                    io_ctrl_reg[7:0] <= rfg_write_value;
                end
                {1'b1,8'h5a}: begin
                    io_led_reg[7:0] <= rfg_write_value;
                end
                {1'b1,8'h5b}: begin
                    gecco_sr_ctrl_reg[7:0] <= rfg_write_value;
                end
                {1'b1,8'h5c}: begin
                    hk_conversion_trigger_match_reg[7:0] <= rfg_write_value;
                end
                {1'b1,8'h5d}: begin
                    hk_conversion_trigger_match_reg[15:8] <= rfg_write_value;
                end
                {1'b1,8'h5e}: begin
                    hk_conversion_trigger_match_reg[23:16] <= rfg_write_value;
                end
                {1'b1,8'h5f}: begin
                    hk_conversion_trigger_match_reg[31:24] <= rfg_write_value;
                end
                default: begin
                end
            endcase
            
            // Write for FIFO Master
            if(rfg_write && rfg_address==8'h15) begin
                hk_adcdac_mosi_fifo_m_axis_tvalid <= 1'b1;
                hk_adcdac_mosi_fifo_m_axis_tdata  <= rfg_write_value;
                hk_adcdac_mosi_fifo_m_axis_tlast  <= rfg_write_last;
            end else begin
                hk_adcdac_mosi_fifo_m_axis_tvalid <= 1'b0;
                hk_adcdac_mosi_fifo_m_axis_tlast  <= 1'b0;
            end
            if(rfg_write && rfg_address==8'h3b) begin
                layer_0_mosi_m_axis_tvalid <= 1'b1;
                layer_0_mosi_m_axis_tdata  <= rfg_write_value;
                layer_0_mosi_m_axis_tlast  <= rfg_write_last;
            end else begin
                layer_0_mosi_m_axis_tvalid <= 1'b0;
                layer_0_mosi_m_axis_tlast  <= 1'b0;
            end
            if(rfg_write && rfg_address==8'h40) begin
                layer_1_mosi_m_axis_tvalid <= 1'b1;
                layer_1_mosi_m_axis_tdata  <= rfg_write_value;
                layer_1_mosi_m_axis_tlast  <= rfg_write_last;
            end else begin
                layer_1_mosi_m_axis_tvalid <= 1'b0;
                layer_1_mosi_m_axis_tlast  <= 1'b0;
            end
            if(rfg_write && rfg_address==8'h45) begin
                layer_2_mosi_m_axis_tvalid <= 1'b1;
                layer_2_mosi_m_axis_tdata  <= rfg_write_value;
                layer_2_mosi_m_axis_tlast  <= rfg_write_last;
            end else begin
                layer_2_mosi_m_axis_tvalid <= 1'b0;
                layer_2_mosi_m_axis_tlast  <= 1'b0;
            end
            
            // Write for HW Write only
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
            if(layers_readout_read_size_write) begin
                layers_readout_read_size_reg <= layers_readout_read_size ;
            end
            // Write for Counter
            if(!(rfg_write && rfg_address==8'hc)) begin
                hk_conversion_trigger_reg <= hk_conversion_trigger_up ? hk_conversion_trigger_reg + 1 : hk_conversion_trigger_reg -1 ;
            end
            if(( (hk_conversion_trigger_up && hk_conversion_trigger_reg == (hk_conversion_trigger_match_reg - 1)) || (!hk_conversion_trigger_up && hk_conversion_trigger_reg==1 )) ) begin
                hk_conversion_trigger_interrupt <= 1'b1;
                hk_conversion_trigger_up <= !hk_conversion_trigger_up;
            end else begin
                hk_conversion_trigger_interrupt <= 1'b0;
            end
            if(hk_stat_conversions_counter_enable) begin
                hk_stat_conversions_counter_reg <= hk_stat_conversions_counter_reg + 1 ;
            end
            if(!(rfg_write && rfg_address==8'h23) && layer_0_stat_frame_counter_enable) begin
                layer_0_stat_frame_counter_reg <= layer_0_stat_frame_counter_reg + 1 ;
            end
            if(!(rfg_write && rfg_address==8'h27) && layer_1_stat_frame_counter_enable) begin
                layer_1_stat_frame_counter_reg <= layer_1_stat_frame_counter_reg + 1 ;
            end
            if(!(rfg_write && rfg_address==8'h2b) && layer_2_stat_frame_counter_enable) begin
                layer_2_stat_frame_counter_reg <= layer_2_stat_frame_counter_reg + 1 ;
            end
            if(!(rfg_write && rfg_address==8'h2f) && layer_0_stat_idle_counter_enable) begin
                layer_0_stat_idle_counter_reg <= layer_0_stat_idle_counter_reg + 1 ;
            end
            if(!(rfg_write && rfg_address==8'h33) && layer_1_stat_idle_counter_enable) begin
                layer_1_stat_idle_counter_reg <= layer_1_stat_idle_counter_reg + 1 ;
            end
            if(!(rfg_write && rfg_address==8'h37) && layer_2_stat_idle_counter_enable) begin
                layer_2_stat_idle_counter_reg <= layer_2_stat_idle_counter_reg + 1 ;
            end
            if(!(rfg_write && rfg_address==8'h4a) && layers_cfg_frame_tag_counter_enable) begin
                layers_cfg_frame_tag_counter_reg <= layers_cfg_frame_tag_counter_reg + 1 ;
            end
        end
    end
    
    
    // Read for FIFO Slave
    assign hk_adc_miso_fifo_s_axis_tready = rfg_read && rfg_address==8'h16;
    assign layers_readout_s_axis_tready = rfg_read && rfg_address==8'h54;
    
    
    // Register Read
    // ---------------
    always@(posedge clk) begin
        if (!resn) begin
            rfg_read_valid <= 0;
            rfg_read_value <= 0;
        end else begin
            // Read for simple registers
            case({rfg_read,rfg_address})
                {1'b1,8'h0}: begin
                    rfg_read_value <= hk_firmware_id_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h1}: begin
                    rfg_read_value <= hk_firmware_id_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h2}: begin
                    rfg_read_value <= hk_firmware_id_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h3}: begin
                    rfg_read_value <= hk_firmware_id_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h4}: begin
                    rfg_read_value <= hk_firmware_version_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h5}: begin
                    rfg_read_value <= hk_firmware_version_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h6}: begin
                    rfg_read_value <= hk_firmware_version_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h7}: begin
                    rfg_read_value <= hk_firmware_version_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h8}: begin
                    rfg_read_value <= hk_xadc_temperature_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h9}: begin
                    rfg_read_value <= hk_xadc_temperature_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'ha}: begin
                    rfg_read_value <= hk_xadc_vccint_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'hb}: begin
                    rfg_read_value <= hk_xadc_vccint_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'hc}: begin
                    rfg_read_value <= hk_conversion_trigger_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'hd}: begin
                    rfg_read_value <= hk_conversion_trigger_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'he}: begin
                    rfg_read_value <= hk_conversion_trigger_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'hf}: begin
                    rfg_read_value <= hk_conversion_trigger_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h10}: begin
                    rfg_read_value <= hk_stat_conversions_counter_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h11}: begin
                    rfg_read_value <= hk_stat_conversions_counter_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h12}: begin
                    rfg_read_value <= hk_stat_conversions_counter_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h13}: begin
                    rfg_read_value <= hk_stat_conversions_counter_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h14}: begin
                    rfg_read_value <= hk_ctrl_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h16}: begin
                    rfg_read_value <= hk_adc_miso_fifo_s_axis_tvalid ? hk_adc_miso_fifo_s_axis_tdata : 8'hff;
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h17}: begin
                    rfg_read_value <= hk_adc_miso_fifo_read_size_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h18}: begin
                    rfg_read_value <= hk_adc_miso_fifo_read_size_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h19}: begin
                    rfg_read_value <= hk_adc_miso_fifo_read_size_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h1a}: begin
                    rfg_read_value <= hk_adc_miso_fifo_read_size_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h1b}: begin
                    rfg_read_value <= spi_layers_ckdivider_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h1c}: begin
                    rfg_read_value <= spi_hk_ckdivider_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h1d}: begin
                    rfg_read_value <= layer_0_cfg_ctrl_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h1e}: begin
                    rfg_read_value <= layer_1_cfg_ctrl_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h1f}: begin
                    rfg_read_value <= layer_2_cfg_ctrl_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h20}: begin
                    rfg_read_value <= layer_0_status_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h21}: begin
                    rfg_read_value <= layer_1_status_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h22}: begin
                    rfg_read_value <= layer_2_status_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h23}: begin
                    rfg_read_value <= layer_0_stat_frame_counter_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h24}: begin
                    rfg_read_value <= layer_0_stat_frame_counter_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h25}: begin
                    rfg_read_value <= layer_0_stat_frame_counter_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h26}: begin
                    rfg_read_value <= layer_0_stat_frame_counter_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h27}: begin
                    rfg_read_value <= layer_1_stat_frame_counter_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h28}: begin
                    rfg_read_value <= layer_1_stat_frame_counter_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h29}: begin
                    rfg_read_value <= layer_1_stat_frame_counter_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h2a}: begin
                    rfg_read_value <= layer_1_stat_frame_counter_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h2b}: begin
                    rfg_read_value <= layer_2_stat_frame_counter_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h2c}: begin
                    rfg_read_value <= layer_2_stat_frame_counter_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h2d}: begin
                    rfg_read_value <= layer_2_stat_frame_counter_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h2e}: begin
                    rfg_read_value <= layer_2_stat_frame_counter_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h2f}: begin
                    rfg_read_value <= layer_0_stat_idle_counter_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h30}: begin
                    rfg_read_value <= layer_0_stat_idle_counter_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h31}: begin
                    rfg_read_value <= layer_0_stat_idle_counter_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h32}: begin
                    rfg_read_value <= layer_0_stat_idle_counter_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h33}: begin
                    rfg_read_value <= layer_1_stat_idle_counter_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h34}: begin
                    rfg_read_value <= layer_1_stat_idle_counter_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h35}: begin
                    rfg_read_value <= layer_1_stat_idle_counter_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h36}: begin
                    rfg_read_value <= layer_1_stat_idle_counter_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h37}: begin
                    rfg_read_value <= layer_2_stat_idle_counter_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h38}: begin
                    rfg_read_value <= layer_2_stat_idle_counter_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h39}: begin
                    rfg_read_value <= layer_2_stat_idle_counter_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h3a}: begin
                    rfg_read_value <= layer_2_stat_idle_counter_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h3c}: begin
                    rfg_read_value <= layer_0_mosi_write_size_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h3d}: begin
                    rfg_read_value <= layer_0_mosi_write_size_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h3e}: begin
                    rfg_read_value <= layer_0_mosi_write_size_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h3f}: begin
                    rfg_read_value <= layer_0_mosi_write_size_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h41}: begin
                    rfg_read_value <= layer_1_mosi_write_size_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h42}: begin
                    rfg_read_value <= layer_1_mosi_write_size_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h43}: begin
                    rfg_read_value <= layer_1_mosi_write_size_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h44}: begin
                    rfg_read_value <= layer_1_mosi_write_size_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h46}: begin
                    rfg_read_value <= layer_2_mosi_write_size_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h47}: begin
                    rfg_read_value <= layer_2_mosi_write_size_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h48}: begin
                    rfg_read_value <= layer_2_mosi_write_size_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h49}: begin
                    rfg_read_value <= layer_2_mosi_write_size_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h4a}: begin
                    rfg_read_value <= layers_cfg_frame_tag_counter_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h4b}: begin
                    rfg_read_value <= layers_cfg_frame_tag_counter_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h4c}: begin
                    rfg_read_value <= layers_cfg_frame_tag_counter_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h4d}: begin
                    rfg_read_value <= layers_cfg_frame_tag_counter_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h4e}: begin
                    rfg_read_value <= layers_cfg_nodata_continue_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h4f}: begin
                    rfg_read_value <= layers_sr_out_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h50}: begin
                    rfg_read_value <= layers_sr_in_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h51}: begin
                    rfg_read_value <= layers_inj_ctrl_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h53}: begin
                    rfg_read_value <= layers_inj_wdata_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h54}: begin
                    rfg_read_value <= layers_readout_s_axis_tvalid ? layers_readout_s_axis_tdata : 8'hff;
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h55}: begin
                    rfg_read_value <= layers_readout_read_size_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h56}: begin
                    rfg_read_value <= layers_readout_read_size_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h57}: begin
                    rfg_read_value <= layers_readout_read_size_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h58}: begin
                    rfg_read_value <= layers_readout_read_size_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h59}: begin
                    rfg_read_value <= io_ctrl_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h5a}: begin
                    rfg_read_value <= io_led_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h5b}: begin
                    rfg_read_value <= gecco_sr_ctrl_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h5c}: begin
                    rfg_read_value <= hk_conversion_trigger_match_reg[7:0];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h5d}: begin
                    rfg_read_value <= hk_conversion_trigger_match_reg[15:8];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h5e}: begin
                    rfg_read_value <= hk_conversion_trigger_match_reg[23:16];
                    rfg_read_valid <= 1 ;
                end
                {1'b1,8'h5f}: begin
                    rfg_read_value <= hk_conversion_trigger_match_reg[31:24];
                    rfg_read_valid <= 1 ;
                end
                default: begin
                rfg_read_valid <= 0 ;
                end
            endcase
            
        end
    end
    
    
    always@(posedge spi_layers_ckdivider_source_clk) begin
        if (!spi_layers_ckdivider_source_resn) begin
            spi_layers_ckdivider_divided_clk <= 1'b0;
            spi_layers_ckdivider_counter <= 8'h00;
        end else begin
            if (spi_layers_ckdivider_counter==spi_layers_ckdivider_reg) begin
                spi_layers_ckdivider_divided_clk <= !spi_layers_ckdivider_divided_clk;
                spi_layers_ckdivider_counter <= 8'h00;
            end else begin
                spi_layers_ckdivider_counter <= spi_layers_ckdivider_counter+1;
            end
        end
    end
    reg [7:0] spi_layers_ckdivider_divided_resn_delay;
    assign spi_layers_ckdivider_divided_resn = spi_layers_ckdivider_divided_resn_delay[7];
    always@(posedge spi_layers_ckdivider_divided_clk or negedge spi_layers_ckdivider_source_resn) begin
        if (!spi_layers_ckdivider_source_resn) begin
            spi_layers_ckdivider_divided_resn_delay <= 8'h00;
        end else begin
            spi_layers_ckdivider_divided_resn_delay <= {spi_layers_ckdivider_divided_resn_delay[6:0],1'b1};
        end
    end
    
    
    always@(posedge spi_hk_ckdivider_source_clk) begin
        if (!spi_hk_ckdivider_source_resn) begin
            spi_hk_ckdivider_divided_clk <= 1'b0;
            spi_hk_ckdivider_counter <= 8'h00;
        end else begin
            if (spi_hk_ckdivider_counter==spi_hk_ckdivider_reg) begin
                spi_hk_ckdivider_divided_clk <= !spi_hk_ckdivider_divided_clk;
                spi_hk_ckdivider_counter <= 8'h00;
            end else begin
                spi_hk_ckdivider_counter <= spi_hk_ckdivider_counter+1;
            end
        end
    end
    reg [7:0] spi_hk_ckdivider_divided_resn_delay;
    assign spi_hk_ckdivider_divided_resn = spi_hk_ckdivider_divided_resn_delay[7];
    always@(posedge spi_hk_ckdivider_divided_clk or negedge spi_hk_ckdivider_source_resn) begin
        if (!spi_hk_ckdivider_source_resn) begin
            spi_hk_ckdivider_divided_resn_delay <= 8'h00;
        end else begin
            spi_hk_ckdivider_divided_resn_delay <= {spi_hk_ckdivider_divided_resn_delay[6:0],1'b1};
        end
    end
    
    
endmodule
