module tlu_client #(
    parameter TRIG_TS_WIDTH = 48,
    parameter TRIG_ID_WIDTH = 32,
    parameter BUSY_DURATION_WIDTH = 16,
    parameter TRIGGER_DELAY_WIDTH = 16,
    parameter USE_CHIPSCOPE_TLU = 0
  )(
    input  wire                             tlu_clk_in,
    input  wire                             tlu_resn_in,
    input  wire                             tlu_sync_in,
    input  wire                             tlu_trig_in,
    output wire                             tlu_busy_out,

    input  wire                             enable_in, // Enables the TLU Unit
    input  wire                             enable_counter_in, // Enables the counter, even if the TLU is disabled it will count if this is 1

    input  wire                             busy_in,
    output wire                             t0_out,
    output wire                             trigger_out,
    output wire [TRIG_TS_WIDTH-1:0]         trigger_ts_out,
    output wire [TRIG_ID_WIDTH-1:0]         trigger_id_out,
    output wire                             triggerdata_valid_out,
    input  wire                             t0_inject_in,
    input  wire                             trigger_inject_in,
    input  wire [BUSY_DURATION_WIDTH-1:0]   conf_busy_min_duration_in,
    input  wire [TRIGGER_DELAY_WIDTH-1:0]   conf_trigger_delay_in,
    input  wire                             conf_t0_mode_in,
    input  wire                             conf_gate_trigger_before_t0_in,
    input  wire                             conf_gate_trigger_when_busy_in,
    input  wire                             conf_busy_on_t0_in
  );

  if (TRIG_TS_WIDTH<2) $error("TRIG_TS_WIDTH too low.");
  if (TRIG_ID_WIDTH<1) $error("TRIG_ID_WIDTH too low.");

  logic tlu_clk;
  logic tlu_trig;
  logic tlu_sync;
  logic tlu_busy;
  logic t0_i;
  logic trig_i;
  logic trig_delayed;
  logic trigger_delay_enabled;
  logic t0_busy;
  logic running;
  logic trigger_enabled;

  // Richard remove static assign as resets, on FPGA 0 is default, this is causing multiple driver errors in some simulators
  logic [BUSY_DURATION_WIDTH-1:0]   busy_min_duration_counter;
  logic [TRIGGER_DELAY_WIDTH-1:0]   trigger_delay_counter ;
  logic [TRIG_TS_WIDTH-1:0]         timestamp_counter  ;
  logic [TRIG_TS_WIDTH-1:0]         timestamp_hold  ;
  logic [TRIG_ID_WIDTH-1:0]         trigger_counter ;
  logic                             triggerdata_valid;

  assign tlu_clk = tlu_clk_in;

  // with t0_mode == 1 we reset counters on T0 and then count clock cycles and triggers ourselves
  // with t0_mode == 0 we receive trigger number over the T0/SYNC line from the TLU - FIXME: NOT YET IMPLEMENTED

  assign tlu_sync = tlu_sync_in;
  assign tlu_trig = tlu_trig_in;
  /*sync_signal #(
      .WIDTH(2),
      .STAGES(0)
    ) sync_tlu_input (
      .out_clk(tlu_clk),
      .signal_in ({tlu_sync_in, tlu_trig_in}),  // i, async
      .signal_out({tlu_sync, tlu_trig})  // o, sync to out_clk
  );*/

  assign t0_i =  enable_in & ((conf_t0_mode_in && tlu_sync) || t0_inject_in);
  assign trig_i = enable_in & (tlu_trig || trigger_inject_in);
  // if conf_busy_on_t0_in == 1'b1:
  // set busy_min_duration_counter on t0, or, if t0 mode is disabled, when the module is being enabled
  assign t0_busy = conf_busy_on_t0_in && (t0_i || (!conf_t0_mode_in && enable_in && !running));
  assign t0_out = t0_i;
  assign trigger_out = ((trig_i && !trigger_delay_enabled && !(conf_gate_trigger_when_busy_in && tlu_busy))
                        || (trig_delayed)) && trigger_enabled && !t0_i;
  assign triggerdata_valid_out = triggerdata_valid;

  //assign trigger_ts_out = (!enable_in & trigger_counter_enable) ? timestamp_counter : timestamp_hold;
  //assign trigger_ts_out = (!enable_in) ? timestamp_counter : timestamp_hold;
  assign trigger_ts_out =timestamp_hold;

  assign trigger_id_out = trigger_counter;

  /*
    // use this if you want to have the tlu_busy_out signal synchronous to tlu_clk
    logic busy_sync;
    sync_signal #(
      .WIDTH(1),
      .STAGES(1)
    ) sync_running_axi (
      .out_clk(tlu_clk),
      .signal_in (busy_in),
      .signal_out(busy_sync)
    );
    // and then replace busy_in with busy_sync below:
  */
  assign tlu_busy = busy_in | (|busy_min_duration_counter) | (|trigger_delay_counter);
  assign tlu_busy_out = tlu_busy;

  always_ff @ (posedge tlu_clk) begin
    if (~enable_in || !tlu_resn_in) begin
      busy_min_duration_counter <= {BUSY_DURATION_WIDTH{1'b0}};
    end
    else if (trig_i || t0_busy) begin
      busy_min_duration_counter <= conf_busy_min_duration_in;
    end
    else if (|busy_min_duration_counter) begin
      busy_min_duration_counter <= busy_min_duration_counter -1;
    end
  end

  always_ff @ (posedge tlu_clk) begin
    if (~|conf_trigger_delay_in) begin
      trigger_delay_enabled <= 1'b0;
    end
    else  begin
      trigger_delay_enabled <= 1'b1;
    end
  end

  always_ff @ (posedge tlu_clk) begin
    if (~enable_in || ~trigger_delay_enabled || !tlu_resn_in) begin
      trigger_delay_counter <= {TRIGGER_DELAY_WIDTH{1'b0}};
    end
    else if (trig_i) begin
        trigger_delay_counter <= conf_trigger_delay_in;
    end
    else if (|trigger_delay_counter) begin
      trigger_delay_counter <= trigger_delay_counter -1;
    end
  end

  always_ff @ (posedge tlu_clk) begin
    trig_delayed <= 1'b0;
    if (trigger_delay_counter == {{(TRIGGER_DELAY_WIDTH-1){1'b0}},1'b1}) begin
      trig_delayed <= 1'b1;
    end
  end

  // Counting and Holding
  // --------------
  //
  //

  //-- Counter by itself
  wire counter_is_counting = enable_in || enable_counter_in;
  wire timestamp_counter_reset = ( !tlu_resn_in || (  t0_i) );
  always_ff @ (posedge tlu_clk) begin

    if (timestamp_counter_reset) begin
      timestamp_counter <= {conf_t0_mode_in, {TRIG_TS_WIDTH-1{1'b0}}};
    end
    else if (counter_is_counting) begin
        timestamp_counter <= timestamp_counter +1;
    end
  end

  //-- Counter Hold
  wire update_hold  = (counter_is_counting && !enable_in) || (trig_i ); // If counter is enabled but not TLU, always update output
  always_ff @ (posedge tlu_clk) begin

    if (!tlu_resn_in) begin
      timestamp_hold    <= {conf_t0_mode_in, {TRIG_TS_WIDTH-1{1'b0}}};
      trigger_counter   <= {TRIG_ID_WIDTH{1'b0}};
      triggerdata_valid <= 1'b0;
    end
    else if (t0_i) begin

      timestamp_hold    <= {TRIG_TS_WIDTH-1{1'b0}};
      trigger_counter <= {TRIG_ID_WIDTH{1'b0}};
    end
    else begin

      if (update_hold) begin
          timestamp_hold  <= timestamp_counter;
      end

      // Tri data valid
      if ((trig_i && ~trigger_delay_enabled) || trig_delayed) begin
          triggerdata_valid <= 1'b1;
      end
    end
  end

  always_ff @ (posedge tlu_clk) begin
    if (~enable_in || !tlu_resn_in) begin
      trigger_enabled <= 1'b0;
      running         <= 1'b0;
    end
    else begin
      running <= 1'b1;
      if (!conf_t0_mode_in || !conf_gate_trigger_before_t0_in) trigger_enabled <= 1'b1;
      else if (t0_i) trigger_enabled <= 1'b1;
    end
  end

  /////////////////
  // chipscope
  /////////////////
  generate
    if (USE_CHIPSCOPE_TLU) begin
      ila_tlu ila_tlu_inst (
        .clk    (tlu_clk), // input wire clk
        .probe0 (timestamp_hold[7:0]), // input wire [7:0]  probe0
        .probe1 (trigger_counter[7:0]), // input wire [7:0]  probe1
        .probe2 (tlu_sync_in), // input wire [0:0]  probe2
        .probe3 (tlu_trig_in), // input wire [0:0]  probe3
        .probe4 (t0_i), // input wire [0:0]  probe4
        .probe5 (trig_i), // input wire [0:0]  probe5
        .probe6 (trigger_out), // input wire [0:0]  probe6
        .probe7 (triggerdata_valid), // input wire [0:0]  probe7
        .probe8 (enable_in), // input wire [0:0]  probe8
        .probe9 (trigger_enabled), // input wire [0:0]  probe9
        .probe10(running), // input wire [0:0]  probe10
        .probe11(tlu_busy), // input wire [0:0]  probe11
        .probe12(busy_in), // input wire [0:0]  probe12
        .probe13(trig_delayed), // input wire [0:0]  probe13
        .probe14(trigger_delay_enabled), // input wire [0:0]  probe14
        .probe15(trigger_delay_counter[7:0]) // input wire [7:0]  probe15
      );
    end
endgenerate

endmodule
