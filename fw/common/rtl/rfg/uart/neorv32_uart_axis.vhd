-- ================================================================================ --
-- NEORV32 SoC - Universal Asynchronous Receiver and Transmitter (UART)             --
-- -------------------------------------------------------------------------------- --
-- The NEORV32 RISC-V Processor - https://github.com/stnolting/neorv32              --
-- Copyright (c) NEORV32 contributors.                                              --
-- Copyright (c) 2020 - 2025 Stephan Nolting. All rights reserved.                  --
-- Licensed under the BSD-3-Clause license, see LICENSE for details.                --
-- SPDX-License-Identifier: BSD-3-Clause                                            --
-- ================================================================================ --

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- pragma translate_off
-- RTL_SYNTHESIS OFF
use std.textio.all;
-- RTL_SYNTHESIS ON
-- pragma translate_on

--library neorv32;
--use neorv32.neorv32_package.all;

entity neorv32_uart_axis is

  port (
    clk_i       : in  std_ulogic; -- global clock line
    rstn_i      : in  std_ulogic; -- global reset line, low-active, async
    clkgen_i    : in  std_ulogic_vector(7 downto 0);
    baud        : in std_ulogic_vector(9 downto 0);
    m_axis_tdata : out std_ulogic_vector(7 downto 0);
    m_axis_tvalid : out std_ulogic;
    m_axis_tready  : in std_ulogic;
    s_axis_tdata : in std_ulogic_vector(7 downto 0);
    s_axis_tvalid : in std_ulogic;
    s_axis_tready  : out std_ulogic;
    uart_txd_o  : out std_ulogic; -- serial TX line
    uart_rxd_i  : in  std_ulogic; -- serial RX line
    uart_rtsn_o : out std_ulogic; -- ready to receive ("RTR"), low-active, optional
    uart_ctsn_i : in  std_ulogic; -- allowed to transmit, low-active, optional
    irq_o       : out std_ulogic  -- interrupt
  );
end neorv32_uart_axis;

architecture neorv32_uart_axis_rtl of neorv32_uart_axis is

  -- simulation mode? --
  --constant sim_mode_en_c : boolean := SIM_MODE_EN and is_simulation_c;

  -- control register bits --
  constant ctrl_en_c            : natural :=  0; -- r/w: UART enable
  constant ctrl_sim_en_c        : natural :=  1; -- r/w: simulation-mode enable
  constant ctrl_hwfc_en_c       : natural :=  2; -- r/w: enable RTS/CTS hardware flow-control
  constant ctrl_prsc0_c         : natural :=  3; -- r/w: baud prescaler bit 0
  constant ctrl_prsc2_c         : natural :=  5; -- r/w: baud prescaler bit 2
  constant ctrl_baud0_c         : natural :=  6; -- r/w: baud divisor bit 0
  constant ctrl_baud9_c         : natural := 15; -- r/w: baud divisor bit 9
  constant ctrl_rx_nempty_c     : natural := 16; -- r/-: RX FIFO not empty
  constant ctrl_rx_half_c       : natural := 17; -- r/-: RX FIFO at least half-full
  constant ctrl_rx_full_c       : natural := 18; -- r/-: RX FIFO full
  constant ctrl_tx_empty_c      : natural := 19; -- r/-: TX FIFO empty
  constant ctrl_tx_nhalf_c      : natural := 20; -- r/-: TX FIFO not at least half-full
  constant ctrl_tx_nfull_c      : natural := 21; -- r/-: TX FIFO not full
  constant ctrl_irq_rx_nempty_c : natural := 22; -- r/w: IRQ if RX FIFO not empty
  constant ctrl_irq_rx_half_c   : natural := 23; -- r/w: IRQ if RX FIFO at least half-full
  constant ctrl_irq_rx_full_c   : natural := 24; -- r/w: IRQ if RX FIFO full
  constant ctrl_irq_tx_empty_c  : natural := 25; -- r/w: IRQ if TX FIFO empty
  constant ctrl_irq_tx_nhalf_c  : natural := 26; -- r/w: IRQ if TX FIFO not at least half-full
  constant ctrl_irq_tx_nfull_c  : natural := 27; -- r/w: IRQ if TX FIFO not full
  constant ctrl_rx_clr_c        : natural := 28; -- r/w: Clear RX FIFO, flag auto-clears
  constant ctrl_tx_clr_c        : natural := 29; -- r/w: Clear TX FIFO, flag auto-clears
  constant ctrl_rx_over_c       : natural := 30; -- r/-: RX FIFO overflow
  constant ctrl_tx_busy_c       : natural := 31; -- r/-: UART transmitter is busy and TX FIFO not empty

  -- data register bits --
  constant data_rtx_lsb_c        : natural :=  0; -- r/w: RX/TX data LSB
  constant data_rtx_msb_c        : natural :=  7; -- r/w: RX/TX data MSB
  constant data_rx_fifo_size_lsb : natural :=  8; -- r/-: log2(RX FIFO size) LSB
  constant data_rx_fifo_size_msb : natural := 11; -- r/-: log2(RX FIFO size) MSB
  constant data_tx_fifo_size_lsb : natural := 12; -- r/-: log2(TX FIFO size) LSB
  constant data_tx_fifo_size_msb : natural := 15; -- r/-: log2(TX FIFO size) MSB

  -- helpers --
  --constant log2_rx_fifo_c : natural := index_size_f(UART_RX_FIFO);
  --constant log2_tx_fifo_c : natural := index_size_f(UART_TX_FIFO);

  -- clock generator --
  signal uart_clk : std_ulogic;


  -- AXIS
  signal m_axis_tvalid_int : std_ulogic;
  signal s_axis_tready_int : std_ulogic;

  -- control register --
  type ctrl_t is record
    enable        : std_ulogic;
    sim_mode      : std_ulogic;
    hwfc_en       : std_ulogic;
    prsc          : std_ulogic_vector(2 downto 0);
    baud          : std_ulogic_vector(9 downto 0);
    irq_rx_nempty : std_ulogic;
    irq_rx_half   : std_ulogic;
    irq_rx_full   : std_ulogic;
    irq_tx_empty  : std_ulogic;
    irq_tx_nhalf  : std_ulogic;
    irq_tx_nfull  : std_ulogic;
    clr_rx        : std_ulogic;
    clr_tx        : std_ulogic;
  end record;
  signal ctrl : ctrl_t;

  -- UART transmitter --
  type tx_engine_t is record
    state   : std_ulogic_vector(2 downto 0);
    sreg    : std_ulogic_vector(8 downto 0);
    bitcnt  : std_ulogic_vector(3 downto 0);
    baudcnt : std_ulogic_vector(9 downto 0);
    done    : std_ulogic;
    busy    : std_ulogic;
    cts     : std_ulogic_vector(1 downto 0);
    txd     : std_ulogic;
  end record;
  signal tx_engine : tx_engine_t;

  -- UART receiver --
  type rx_engine_t is record
    state   : std_ulogic_vector(1 downto 0);
    sreg    : std_ulogic_vector(8 downto 0);
    bitcnt  : std_ulogic_vector(3 downto 0);
    baudcnt : std_ulogic_vector(9 downto 0);
    done    : std_ulogic;
    sync    : std_ulogic_vector(2 downto 0);
    over    : std_ulogic;
  end record;
  signal rx_engine : rx_engine_t;

begin

  -- Bus Access -----------------------------------------------------------------------------
  -- -------------------------------------------------------------------------------------------
  bus_access: process( clk_i)
  begin
    if (rstn_i = '0') then
      --bus_rsp_o          <= rsp_terminate_c;
      ctrl.enable        <= '0';
      ctrl.sim_mode      <= '0';
      ctrl.hwfc_en       <= '0';
      ctrl.prsc          <= (others => '0');
      ctrl.baud          <= (others => '0');
      ctrl.irq_rx_nempty <= '0';
      ctrl.irq_rx_half   <= '0';
      ctrl.irq_rx_full   <= '0';
      ctrl.irq_tx_empty  <= '0';
      ctrl.irq_tx_nhalf  <= '0';
      ctrl.irq_tx_nfull  <= '0';
      ctrl.clr_rx        <= '0';
      ctrl.clr_tx        <= '0';
    elsif rising_edge(clk_i) then


        ctrl.enable        <= '0';
        ctrl.sim_mode      <= '0';
        ctrl.hwfc_en       <= '0';
        ctrl.prsc          <= (others => '0');
        ctrl.baud          <= (others => '0');
        ctrl.irq_rx_nempty <= '0';
        ctrl.irq_rx_half   <= '0';
        ctrl.irq_rx_full   <= '0';
        ctrl.irq_tx_empty  <= '0';
        ctrl.irq_tx_nhalf  <= '0';
        ctrl.irq_tx_nfull  <= '0';
        ctrl.clr_rx        <= '0';
        ctrl.clr_tx        <= '0';

        ctrl.baud <= baud;
        ctrl.enable <= '1';

      -- defaults --
      --bus_rsp_o.ack  <= bus_req_i.stb;
      --bus_rsp_o.err  <= '0';
      --bus_rsp_o.data <= (others => '0');
      ctrl.clr_rx    <= '0'; -- auto-clear
      ctrl.clr_tx    <= '0'; -- auto-clear


    end if;
  end process bus_access;

  -- UART clock enable --
  uart_clk_gen : process(clk_i)
  begin
    if (rstn_i = '0') then
      uart_clk <= '0';
    elsif rising_edge(clk_i) then

        uart_clk <= not uart_clk;   -- RX FIFO full

      --irq_o <= ctrl.enable and (
       --        (ctrl.irq_tx_empty  and (not tx_fifo.avail)) or -- TX FIFO empty
       --        (ctrl.irq_tx_nhalf  and (not tx_fifo.half))  or -- TX FIFO not at least half full
       --        (ctrl.irq_tx_nfull  and tx_fifo.free)        or -- TX FIFO not full
       --        (ctrl.irq_rx_nempty and rx_fifo.avail)       or -- RX FIFO not empty
        --       (ctrl.irq_rx_half   and rx_fifo.half)        or -- RX FIFO at least half full
        --       (ctrl.irq_rx_full   and (not rx_fifo.free)));   -- RX FIFO full
    end if;
  end process uart_clk_gen;
  --uart_clk <= clkgen_i(to_integer(unsigned(ctrl.prsc)));



  -- Interrupt Generator --------------------------------------------------------------------
  -- -------------------------------------------------------------------------------------------
  irq_gen: process(rstn_i, clk_i)
  begin
    if (rstn_i = '0') then
      irq_o <= '0';
    elsif rising_edge(clk_i) then

        irq_o <= std_ulogic((ctrl.enable) and (m_axis_tready ) and (m_axis_tvalid_int ));   -- RX FIFO full

      --irq_o <= ctrl.enable and (
       --        (ctrl.irq_tx_empty  and (not tx_fifo.avail)) or -- TX FIFO empty
       --        (ctrl.irq_tx_nhalf  and (not tx_fifo.half))  or -- TX FIFO not at least half full
       --        (ctrl.irq_tx_nfull  and tx_fifo.free)        or -- TX FIFO not full
       --        (ctrl.irq_rx_nempty and rx_fifo.avail)       or -- RX FIFO not empty
        --       (ctrl.irq_rx_half   and rx_fifo.half)        or -- RX FIFO at least half full
        --       (ctrl.irq_rx_full   and (not rx_fifo.free)));   -- RX FIFO full
    end if;
  end process irq_gen;


  -- Transmit Engine ------------------------------------------------------------------------
  -- -------------------------------------------------------------------------------------------

  s_axis_tready <= s_axis_tready_int;

  transmitter: process(rstn_i, clk_i)
  begin
    if (rstn_i = '0') then
      tx_engine.cts     <= (others => '0');
      tx_engine.done    <= '0';
      tx_engine.state   <= (others => '0');
      tx_engine.baudcnt <= (others => '0');
      tx_engine.bitcnt  <= (others => '0');
      tx_engine.sreg    <= (others => '0');
      tx_engine.txd     <= '1';

      s_axis_tready_int <= '1';

    elsif rising_edge(clk_i) then
      -- synchronize clear-to-send --
      tx_engine.cts <= tx_engine.cts(0) & uart_ctsn_i;

      -- defaults --
      tx_engine.done <= '0';
      tx_engine.txd  <= '1';

      -- FSM --
      tx_engine.state(2) <= ctrl.enable;
      case tx_engine.state is

        when "100" => -- IDLE: wait for new data to send
        -- ------------------------------------------------------------
          s_axis_tready_int <= '1';
          tx_engine.baudcnt <= ctrl.baud;
          tx_engine.bitcnt  <= "1011"; -- 1 start-bit + 8 data-bits + 1 stop-bit + 1 pause-bit
          tx_engine.sreg    <= s_axis_tdata & '0'; -- data & start-bit
          if ((s_axis_tvalid = '1') and (s_axis_tready_int = '1')) then
            tx_engine.state(1 downto 0) <= "01";
            s_axis_tready_int <= '0';
          end if;

        when "101" => -- WAIT: check if we can start sending
        -- ------------------------------------------------------------
          s_axis_tready_int <= '0';

          if (uart_clk = '1') and -- start with next clock tick
             ((tx_engine.cts(1) = '0') or (ctrl.hwfc_en = '0')) then -- allowed to send OR flow-control disabled
            tx_engine.state(1 downto 0) <= "11";
          end if;

        when "111" => -- SEND: transmit data
        -- ------------------------------------------------------------
          tx_engine.txd <= tx_engine.sreg(0);
          if (uart_clk = '1') then
            if (tx_engine.baudcnt = "0000000000") then -- bit done?
              tx_engine.baudcnt <= ctrl.baud;
              tx_engine.bitcnt  <= std_ulogic_vector(unsigned(tx_engine.bitcnt) - 1);
              tx_engine.sreg    <= '1' & tx_engine.sreg(tx_engine.sreg'left downto 1);
            else
              tx_engine.baudcnt <= std_ulogic_vector(unsigned(tx_engine.baudcnt) - 1);
            end if;
          end if;
          if (tx_engine.bitcnt = "0000") then -- all bits send?
            tx_engine.done              <= '1';
            tx_engine.state(1 downto 0) <= "00";
          end if;

        when others => -- "0--": disabled
        -- ------------------------------------------------------------
          s_axis_tready_int <= '0';
          tx_engine.state(1 downto 0) <= "00";

      end case;
    end if;
  end process transmitter;

  -- transmitter busy --
  tx_engine.busy <= '0' when (tx_engine.state(1 downto 0) = "00") else '1';

  -- serial data output --
  uart_txd_o <= tx_engine.txd;


  -- Receive Engine -------------------------------------------------------------------------
  -- -------------------------------------------------------------------------------------------

  m_axis_tvalid <= m_axis_tvalid_int;


  receiver: process(rstn_i, clk_i)
  begin
    if (rstn_i = '0') then
      rx_engine.sync    <= (others => '0');
      rx_engine.done    <= '0';
      rx_engine.state   <= (others => '0');
      rx_engine.baudcnt <= (others => '0');
      rx_engine.bitcnt  <= (others => '0');
      rx_engine.sreg    <= (others => '0');

      m_axis_tvalid_int <= '0';

    elsif rising_edge(clk_i) then


    --rx_fifo.clear <= '1' when (ctrl.enable = '0') or (ctrl.sim_mode = '1') or (ctrl.clr_rx = '1') else '0';
    --rx_fifo.wdata <= rx_engine.sreg(7 downto 0);
    --rx_fifo.we    <= rx_engine.done;
    --rx_fifo.re    <= '1' when (bus_req_i.stb = '1') and (bus_req_i.rw = '0') and (bus_req_i.addr(2) = '1') else '0';

      -- input synchronizer --
      rx_engine.sync(2) <= uart_rxd_i;
      if (uart_clk = '1') then
        rx_engine.sync(1 downto 0) <= rx_engine.sync(2 downto 1);
      end if;

      -- defaults --
      rx_engine.done <= '0';

      -- Axis write
      m_axis_tvalid_int <= rx_engine.done;
      if (rx_engine.done = '1') then
         m_axis_tdata <= rx_engine.sreg(7 downto 0);
      end if;


      -- FSM --
      rx_engine.state(1) <= ctrl.enable;
      case rx_engine.state is

        when "10" => -- IDLE: wait for incoming transmission
        -- ------------------------------------------------------------
          rx_engine.baudcnt <= '0' & ctrl.baud(9 downto 1); -- half baud delay at the beginning to sample in the middle of each bit
          rx_engine.bitcnt  <= "1010"; -- 1 start-bit + 8 data-bits + 1 stop-bit
          if (rx_engine.sync(1 downto 0) = "01") then -- start bit detected (falling edge)?
            rx_engine.state(0) <= '1';
          end if;

        when "11" => -- RECEIVE: sample receive data
        -- ------------------------------------------------------------
          if (uart_clk = '1') then
            if (rx_engine.baudcnt = "0000000000") then -- bit done
              rx_engine.baudcnt <= ctrl.baud;
              rx_engine.bitcnt  <= std_ulogic_vector(unsigned(rx_engine.bitcnt) - 1);
              rx_engine.sreg    <= rx_engine.sync(2) & rx_engine.sreg(rx_engine.sreg'left downto 1);
            else
              rx_engine.baudcnt <= std_ulogic_vector(unsigned(rx_engine.baudcnt) - 1);
            end if;
          end if;
          if (rx_engine.bitcnt = "0000") then -- all bits received?
            rx_engine.done     <= '1'; -- receiving done
            rx_engine.state(0) <= '0';
          end if;

        when others => -- "0-": disabled
        -- ------------------------------------------------------------
          rx_engine.state(0) <= '0';

      end case;
    end if;
  end process receiver;

  -- RX overrun flag --
  fifo_overrun: process(rstn_i, clk_i)
  begin
    if (rstn_i = '0') then
      rx_engine.over <= '0';
    elsif rising_edge(clk_i) then
      if (ctrl.enable = '0') then -- clear when disabled
        rx_engine.over <= '0';
      elsif (m_axis_tvalid_int = '1') and (m_axis_tready = '0') then -- writing to full FIFO
        rx_engine.over <= '1';
      end if;
    end if;
  end process fifo_overrun;

  -- HW flow-control: ready to receive? --
  rtr_control: process(rstn_i, clk_i)
  begin
    if (rstn_i = '0') then
      uart_rtsn_o <= '0';
    elsif rising_edge(clk_i) then
      if (ctrl.hwfc_en = '1') then
        if (ctrl.enable = '0') or (m_axis_tready = '0') then  -- UART disabled or RX FIFO at least half-full: no "safe space" left in RX FIFO
          uart_rtsn_o <= '1'; -- NOT allowed to send
        else
          uart_rtsn_o <= '0'; -- ready to receive
        end if;
      else
        uart_rtsn_o <= '0'; -- always ready to receive when HW flow-control is disabled
      end if;
    end if;
  end process rtr_control;




end neorv32_uart_axis_rtl;
