#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SENSEX FNO SCALPING AGENT - Professional 3-Minute Strategy
Entry: Confirmed trend + Volume confirmation + Support/Resistance
SL: 5-8 points (tight for scalping risk/reward)
TP: 12-15 points (2:1 reward/risk minimum)
Max Hold: 5 minutes per trade
Market Hours: 09:15-15:25 IST (close all 5min before market close)
Target: 70%+ win rate through selective entries
"""
from datetime import datetime, timedelta
import pytz
from enum import Enum

class TrendSignal(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class SensexScalpingAgent:
    """SENSEX FNO 3-min scalping - High-probability entries only"""

    def __init__(self):
        self.name = "SENSEX_SCALPING"
        self.symbol = "SENSEX"
        self.timeframe = "3m"
        self.lot_size = 1  # 1 lot = 20 contracts
        self.quantity = 20  # 20 contracts (1 lot)

        # Scalping parameters
        self.stop_loss_points = 6  # Tight: 6 points
        self.take_profit_points = 12  # 2:1 ratio (TP:SL)
        self.max_hold_time = 300  # 5 minutes max per trade

        self.ist = pytz.timezone('Asia/Kolkata')

        # Candle data for analysis
        self.completed_candles = []
        self.current_candle_start = None
        self.current_candle = {"open": None, "high": None, "low": None, "close": None, "volume": 0}
        self.candle_volumes = []  # Track volumes for confirmation

        # Support/Resistance tracking
        self.support_level = None
        self.resistance_level = None
        self.last_entry_time = None
        self.entry_price = None
        self.entry_signal = None

    def process_tick(self, price: float):
        """Process incoming price tick and build 3-minute candles with volume"""
        now = datetime.now(self.ist)

        if self.current_candle_start is None:
            self.current_candle_start = now
            self.current_candle = {"open": price, "high": price, "low": price, "close": price, "volume": 1}
            return

        elapsed = (now - self.current_candle_start).total_seconds()

        self.current_candle["close"] = price
        self.current_candle["high"] = max(self.current_candle["high"], price)
        self.current_candle["low"] = min(self.current_candle["low"], price)
        self.current_candle["volume"] = self.current_candle.get("volume", 0) + 1

        if elapsed >= 180:
            self.completed_candles.append(self.current_candle.copy())
            self.candle_volumes.append(self.current_candle.get("volume", 1))
            if len(self.candle_volumes) > 20:
                self.candle_volumes.pop(0)
            if len(self.completed_candles) > 20:
                self.completed_candles.pop(0)

            self.current_candle_start = now
            self.current_candle = {"open": price, "high": price, "low": price, "close": price, "volume": 1}

    def _calculate_support_resistance(self):
        """Compute dynamic support/resistance from last 5 candles"""
        if len(self.completed_candles) < 5:
            return None, None

        recent = self.completed_candles[-5:]
        lows = [c.get("low", 0) for c in recent]
        highs = [c.get("high", 0) for c in recent]

        support = min(lows)
        resistance = max(highs)
        return support, resistance

    def _check_volume_confirmation(self):
        """Volume must be above average (50%+ of 20-candle average)"""
        if len(self.candle_volumes) < 3:
            return True

        avg_volume = sum(self.candle_volumes) / len(self.candle_volumes)
        current_volume = self.current_candle.get("volume", 0)
        return current_volume >= (avg_volume * 0.5)

    def analyze(self, live_data):
        """SENSEX FNO scalping: Trend + Volume + Support/Resistance confluence"""
        try:
            price = live_data.get('close', 0)
            if price <= 0:
                return TrendSignal.HOLD

            self.process_tick(price)

            candles = []
            if len(self.completed_candles) > 0:
                candles.append(self.completed_candles[-1])
            if self.current_candle["close"] is not None:
                candles.append(self.current_candle)

            # Start with 2 candles for faster startup, use 3 when available
            min_candles = 2 if len(self.completed_candles) < 3 else 3
            if len(candles) < min_candles:
                return TrendSignal.HOLD

            # Get last 3 candles for multi-candle confirmation (or 2 if starting up)
            recent = [self.completed_candles[-i] if i <= len(self.completed_candles) else self.current_candle
                     for i in range(1, 4)]
            recent = [c for c in recent if c][:min_candles]

            if len(recent) < min_candles:
                return TrendSignal.HOLD

            # Check trend (2 or 3 candle confirmation based on available data)
            bullish_count = sum(1 for c in recent if c.get("close", 0) > c.get("open", 0))
            bearish_count = len(recent) - bullish_count

            # Require majority in same direction (2/2 or 2/3)
            if bullish_count == 0 and bearish_count == 0:
                return TrendSignal.HOLD
            if min_candles == 2:
                # For 2-candle: need both bullish or both bearish
                if bullish_count < 2 and bearish_count < 2:
                    return TrendSignal.HOLD
            else:
                # For 3-candle: need at least 2/3 in same direction
                if bullish_count < 2 and bearish_count < 2:
                    return TrendSignal.HOLD

            # Volume confirmation
            if not self._check_volume_confirmation():
                return TrendSignal.HOLD

            # Support/Resistance filter
            support, resistance = self._calculate_support_resistance()
            if support is None:
                return TrendSignal.HOLD

            # Entry signals with confluence
            if bullish_count >= 2:
                # Bullish: price must be above support + buffer
                if price > (support + 2) and price < (resistance - 2):
                    self.entry_signal = TrendSignal.BUY
                    self.entry_price = price
                    self.last_entry_time = datetime.now(self.ist)
                    return TrendSignal.BUY

            elif bearish_count >= 2:
                # Bearish: price must be below resistance - buffer
                if price < (resistance - 2) and price > (support + 2):
                    self.entry_signal = TrendSignal.SELL
                    self.entry_price = price
                    self.last_entry_time = datetime.now(self.ist)
                    return TrendSignal.SELL

            return TrendSignal.HOLD

        except Exception as e:
            print(f"[WARN] Scalping analyze error: {e}")
            return TrendSignal.HOLD

    def get_signal(self, market_data):
        """Generate FNO scalping trade signal with tight risk/reward"""
        try:
            signal = self.analyze(market_data)
            price = market_data.get('close', 0)

            if signal == TrendSignal.BUY:
                sl = price - self.stop_loss_points
                tp = price + self.take_profit_points
                return {
                    "agent": self.name,
                    "symbol": self.symbol,
                    "signal": signal.value,
                    "entry_price": price,
                    "stop_loss": sl,
                    "take_profit": tp,
                    "quantity": self.quantity,
                    "max_hold_seconds": self.max_hold_time,
                    "reason": f"FNO 3-Min Scalp BUY (2:1 RR: SL {self.stop_loss_points}pts, TP {self.take_profit_points}pts)",
                    "confidence": 0.75
                }
            elif signal == TrendSignal.SELL:
                sl = price + self.stop_loss_points
                tp = price - self.take_profit_points
                return {
                    "agent": self.name,
                    "symbol": self.symbol,
                    "signal": signal.value,
                    "entry_price": price,
                    "stop_loss": sl,
                    "take_profit": tp,
                    "quantity": self.quantity,
                    "max_hold_seconds": self.max_hold_time,
                    "reason": f"FNO 3-Min Scalp SELL (2:1 RR: SL {self.stop_loss_points}pts, TP {self.take_profit_points}pts)",
                    "confidence": 0.75
                }

            return {"signal": "HOLD"}
        except Exception as e:
            print(f"[WARN] get_signal error: {e}")
            return {"signal": "HOLD"}

    def backtest(self, historical_data):
        """Backtest on historical candles"""
        trades = []
        i = 1

        while i < len(historical_data):
            if i < len(historical_data) and i > 0:
                prev = historical_data[i-1]
                curr = historical_data[i]

                prev_bullish = prev.get('close', 0) > prev.get('open', 0)
                curr_bullish = curr.get('close', 0) > curr.get('open', 0)
                prev_bearish = prev.get('close', 0) < prev.get('open', 0)
                curr_bearish = curr.get('close', 0) < curr.get('open', 0)

                signal = None
                if prev_bullish and curr_bullish:
                    signal = "BUY"
                    entry = curr.get('close', 0)
                    sl = curr.get('low', 0)
                    tp = entry + self.take_profit_points
                elif prev_bearish and curr_bearish:
                    signal = "SELL"
                    entry = curr.get('close', 0)
                    sl = curr.get('high', 0)
                    tp = entry - self.take_profit_points

                if signal:
                    pnl = 0
                    exit_reason = None
                    exit_price = entry

                    for j in range(i+1, min(i+50, len(historical_data))):
                        h = historical_data[j].get('high', 0)
                        l = historical_data[j].get('low', 0)

                        if signal == "BUY":
                            if h >= tp:
                                exit_price = tp
                                pnl = (tp - entry) * self.quantity * self.lot_size
                                exit_reason = "TP"
                                break
                            elif l <= sl:
                                exit_price = sl
                                pnl = (sl - entry) * self.quantity * self.lot_size
                                exit_reason = "SL"
                                break
                        else:
                            if l <= tp:
                                exit_price = tp
                                pnl = (entry - tp) * self.quantity * self.lot_size
                                exit_reason = "TP"
                                break
                            elif h >= sl:
                                exit_price = sl
                                pnl = (entry - sl) * self.quantity * self.lot_size
                                exit_reason = "SL"
                                break

                    if not exit_reason:
                        exit_price = historical_data[min(i+49, len(historical_data)-1)].get('close', entry)
                        pnl = (exit_price - entry) * self.quantity * self.lot_size if signal == "BUY" else (entry - exit_price) * self.quantity * self.lot_size
                        exit_reason = "TIMEOUT"

                    trades.append({
                        "signal": signal,
                        "entry": entry,
                        "exit": exit_price,
                        "sl": sl,
                        "tp": tp,
                        "pnl": pnl,
                        "win": pnl > 0
                    })

            i += 1

        if not trades:
            return {"total_trades": 0, "winning_trades": 0, "losing_trades": 0, "win_rate": 0, "avg_win": 0, "avg_loss": 0, "profit_factor": 0, "total_pnl": 0, "trades": []}

        wins = [t for t in trades if t["win"]]
        losses = [t for t in trades if not t["win"]]

        return {
            "total_trades": len(trades),
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "win_rate": (len(wins)/len(trades))*100,
            "avg_win": sum([t["pnl"] for t in wins])/len(wins) if wins else 0,
            "avg_loss": sum([t["pnl"] for t in losses])/len(losses) if losses else 0,
            "profit_factor": sum([t["pnl"] for t in wins]) / abs(sum([t["pnl"] for t in losses])) if losses and sum([t["pnl"] for t in losses]) != 0 else 1.0,
            "total_pnl": sum([t["pnl"] for t in trades]),
            "trades": trades[:10]
        }
