

/**

Multi Layers parametezied

*/
module layers_readout_switched #(
    parameter LAYER_COUNT = 5,
    parameter TS_WIDTH=64
) (

    // Clocking
    //-------------
    input wire clk_core,
    input wire clk_core_resn,

    input wire clk_io,
    input wire clk_io_resn,

    // Layers Interface
    //-----------------
    input  wire [LAYER_COUNT-1:0]       layers_interruptn,
    output wire [LAYER_COUNT-1:0]       layers_spi_clk,
    output wire [LAYER_COUNT-1:0]       layers_spi_mosi,
    input  wire [LAYER_COUNT*2-1:0]     layers_spi_miso,
    output wire [LAYER_COUNT-1:0]       layers_spi_csn,

    // MOSI
    //----------------
    input wire  [(LAYER_COUNT*8)-1:0]   layers_mosi_s_axis_tdata,
    input wire  [LAYER_COUNT-1:0]       layers_mosi_s_axis_tvalid,
    input wire  [LAYER_COUNT-1:0]       layers_mosi_s_axis_tlast,
    output wire [LAYER_COUNT-1:0]       layers_mosi_s_axis_tready,
    output wire [(LAYER_COUNT*32)-1:0]  layers_mosi_write_size,

    // MISO Merged readout
    //-------------
    output logic [31:0]		            readout_frames_data_count,
    output wire  [7:0]		            readout_frames_m_axis_tdata,
    input  wire				            readout_frames_m_axis_tready,
    output wire				            readout_frames_m_axis_tvalid,

    // Configurations
    //---------------------
    input wire                          config_packet_mode,
    input wire  [LAYER_COUNT-1:0]       config_disable_autoread,
    input wire  [TS_WIDTH-1:0]          config_fpga_timestamp,
    input wire  [1:0]                   config_fpga_timestamp_size,
    input wire  [7:0]                   config_nodata_continue,
    input wire  [LAYER_COUNT-1:0]       config_layers_reset,
    input wire  [LAYER_COUNT-1:0]       config_layers_disable_miso,
    input wire  [7:0]                   config_payload_length,

    // Status
    //---------------------
    output wire [LAYER_COUNT-1:0]        layers_status_frame_decoding,

    // Statistics
    //----------------------
    output wire [LAYER_COUNT-1:0]       layers_stat_count_idle,
    output wire [LAYER_COUNT-1:0]       layers_stat_count_frame,
    output wire [LAYER_COUNT-1:0]       layers_stat_wronglength


);

    // Signals
    //-------------

    // Add Count Layers
    //----------------------

    // Master outputs from layers readout
    wire  [(LAYER_COUNT*8)-1:0]   layers_miso_m_axis_tdata;
    wire  [(LAYER_COUNT*8)-1:0]   layers_miso_m_axis_tdest;
    wire  [LAYER_COUNT-1:0]       layers_miso_m_axis_tvalid;
    wire  [LAYER_COUNT-1:0]       layers_miso_m_axis_tlast;
    wire  [LAYER_COUNT-1:0]       layers_miso_m_axis_tready;
    genvar li;
    generate
        for (li = 0 ; li < LAYER_COUNT ; li++) begin

            layer_if_a #(.LAYER_ID(li+1)) layer_if_I (

                .clk_core(clk_core),
                .clk_core_resn(clk_core_resn),
                .clk_spi(clk_io),
                .clk_spi_resn(clk_io_resn),
                .frames_m_axis_tdata(layers_miso_m_axis_tdata[li*8+7:li*8]),
                .frames_m_axis_tdest(layers_miso_m_axis_tdest[li*8+7:li*8]),
                .frames_m_axis_tlast(layers_miso_m_axis_tlast[li]),
                .frames_m_axis_tready(layers_miso_m_axis_tready[li]),
                .frames_m_axis_tvalid(layers_miso_m_axis_tvalid[li]),

                .interruptn(layers_interruptn[li]),

                .mosi_s_axis_tdata(layers_mosi_s_axis_tdata[li*8+7:li*8]),
                .mosi_s_axis_tlast(layers_mosi_s_axis_tlast[li]),
                .mosi_s_axis_tready(layers_mosi_s_axis_tready[li]),
                .mosi_s_axis_tvalid(layers_mosi_s_axis_tvalid[li]),
                .mosi_s_write_size(layers_mosi_write_size[li*32+31:li*32]),

                .spi_clk(layers_spi_clk[li]),
                .spi_csn(layers_spi_csn[li]),
                .spi_miso(layers_spi_miso[li*2+1:li*2]),
                .spi_mosi(layers_spi_mosi[li]),

                .cfg_disable_autoread(config_disable_autoread[li]),
                .cfg_fpga_timestamp(config_fpga_timestamp),
                .cfg_fpga_timestamp_size(config_fpga_timestamp_size),
                .cfg_nodata_continue(config_nodata_continue),
                .cfg_layer_reset(config_layers_reset[li]),
                .cfg_disable_miso(config_layers_disable_miso[li]),
                .status_frame_decoding(layers_status_frame_decoding[li]),
                .stat_frame_detected(layers_stat_count_frame[li]),
                .stat_idle_detected(layers_stat_count_idle[li]),
                .stat_wronglength_detected(layers_stat_wronglength[li]),
                .cfg_payload_length(config_payload_length)
            );


        end


    endgenerate


    // Switch
    //---------------
    wire [7:0] switch_m_axis_tdata;
    wire switch_m_axis_tlast;
    axis_switch_layer_frame  axis_switch_layer_frame_I(
        .aclk(clk_core),
        .aresetn(clk_core_resn),

        .m_axis_tdata(switch_m_axis_tdata),
        .m_axis_tdest(),
        .m_axis_tlast(switch_m_axis_tlast),
        .m_axis_tready(switch_m_axis_tready),
        .m_axis_tvalid(switch_m_axis_tvalid),

        .s_axis_tdata(layers_miso_m_axis_tdata),
        .s_axis_tdest(layers_miso_m_axis_tdest),
        .s_axis_tlast(layers_miso_m_axis_tlast),
        .s_axis_tready(layers_miso_m_axis_tready),
        .s_axis_tvalid(layers_miso_m_axis_tvalid),
        .s_decode_err(),
        .s_req_suppress({LAYER_COUNT{1'b0}})
    );

    // Data FIFO
    //-----------------
    wire [31:0] readout_frames_data_count_from_buffer;
    wire buffer_in_last = switch_m_axis_tlast | (!config_packet_mode);
    fifo_axis_1clk_1kB  frames_buffer(
        .s_axis_aclk(clk_core),
        .s_axis_aresetn(clk_core_resn),

        // From Switch
        .s_axis_tdata(switch_m_axis_tdata),
        .s_axis_tready(switch_m_axis_tready),
        .s_axis_tvalid(switch_m_axis_tvalid),
        .s_axis_tlast(buffer_in_last),

        // To RFG Readout
        .axis_rd_data_count(readout_frames_data_count_from_buffer),
        .m_axis_tdata(readout_frames_m_axis_tdata),
        .m_axis_tready(readout_frames_m_axis_tready),
        .m_axis_tvalid(readout_frames_m_axis_tvalid),
        .m_axis_tlast()
    );
    
    //-- Size of Data Frame Buffer reported to RFG:
    //-- In packet mode, the size can only be reported if the FIFO is showing valid. Otherwise the size might not be 0, but reading will produce empty bytes, hence falsing readout 
    //-- The solution is to report a 0 size if the FIFO is not showing valid, otherwise we can show the size, which will reflect only full frames 
    //-- If packet mode is not used, we can report the size fully 
    logic [31:0] readout_frames_data_count_temp;
    wire write_in_buffer = switch_m_axis_tready & switch_m_axis_tvalid;
    wire read_in_buffer = readout_frames_m_axis_tready & readout_frames_m_axis_tvalid;
    always_ff @(posedge clk_core) begin
        if (!clk_core_resn) begin
            readout_frames_data_count <= 32'd0;
            readout_frames_data_count_temp <= 'd0; 
        end
        else begin 
            
            if (config_packet_mode) begin 
                
            
            
                // If Write on slave, increment temp count 
                // If Last on slave, add temp count to output 
                if (write_in_buffer && !read_in_buffer) begin
                    readout_frames_data_count_temp <= readout_frames_data_count_temp + 'd1;
                end
                else if (read_in_buffer && !write_in_buffer) begin 
                    readout_frames_data_count_temp <= readout_frames_data_count_temp - 'd1;
                end
                
                if (write_in_buffer && buffer_in_last ) begin 
                    readout_frames_data_count <= (readout_frames_data_count_temp + 'd1) - (read_in_buffer ? 'd1:'d0);
                end
                else if (read_in_buffer) begin 
                    readout_frames_data_count <= readout_frames_data_count_temp - 'd1;
                end
            
            end
            else begin 
                readout_frames_data_count <= readout_frames_data_count_from_buffer;
            end
            
            
            
            
        end
    end
    
    /*wire readout_frames_m_axis_tvalid_posedge;
    reg [1:0] buffer_in_last_del;
    
    edge_detect readout_frames_m_axis_tvali_detect(
        .clk(clk_core),
        .resn(clk_core_resn),
        .in(readout_frames_m_axis_tvalid),
        .rising_edge(readout_frames_m_axis_tvalid_posedge),
        .falling_edge()
        );
    
    always_ff @(posedge clk_core) begin
        if (!clk_core_resn) begin
            readout_frames_data_count <= 32'd0;
            buffer_in_last_del <= 'd0;
        end
        else begin 
            
            buffer_in_last_del <= {buffer_in_last_del[0],buffer_in_last};
            
            if (config_packet_mode & buffer_in_last_del[1]) begin 
                readout_frames_data_count <= readout_frames_data_count_from_buffer;
            end
            else if (config_packet_mode & !readout_frames_m_axis_tvalid) begin 
                readout_frames_data_count <= 32'd0;
            end
            else begin 
                readout_frames_data_count <= readout_frames_data_count_from_buffer;
            end
            
        end
        end*/

endmodule
