from agents.base import BaseAgent, Signal
from typing import Dict, List

class SensexAgent(BaseAgent):
    def __init__(self):
        super().__init__("SENSEX")
        self.symbols = ["SENSEX"]

    def get_symbols(self) -> List[str]:
        return self.symbols

    def analyze(self, market_data: Dict) -> Signal:
        if not market_data:
            return Signal.HOLD

        close = market_data.get("close", 0)
        high = market_data.get("high", 0)
        low = market_data.get("low", 0)

        if high == 0 or low == 0:
            return Signal.HOLD

        range_val = high - low

        # Balanced thresholds: 65%/35% (sweet spot between loose and strict)
        # Captures reversals from range extremes without edge-case noise
        upper_threshold = low + (range_val * 0.65)  # Top 35% of range
        lower_threshold = low + (range_val * 0.35)  # Bottom 35% of range

        if close > upper_threshold:
            return Signal.BUY
        elif close < lower_threshold:
            return Signal.SELL
        else:
            return Signal.HOLD
