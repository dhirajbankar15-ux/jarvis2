from agents.base import BaseAgent, Signal
from typing import Dict, List

class OptionsAgent(BaseAgent):
    def __init__(self):
        super().__init__("OPTIONS")
        self.symbols = ["NIFTY", "BANKNIFTY", "FINNIFTY"]

    def get_symbols(self) -> List[str]:
        return self.symbols

    def analyze(self, market_data: Dict) -> Signal:
        if not market_data:
            return Signal.HOLD

        close = market_data.get("close", 0)
        open_price = market_data.get("open", 0)
        high = market_data.get("high", 0)
        low = market_data.get("low", 0)

        if open_price == 0:
            return Signal.HOLD

        body = abs(close - open_price)
        range_val = high - low

        if range_val == 0:
            return Signal.HOLD

        body_ratio = body / range_val

        if close > open_price and body_ratio > 0.7:
            return Signal.BUY
        elif close < open_price and body_ratio > 0.7:
            return Signal.SELL
        else:
            return Signal.HOLD
