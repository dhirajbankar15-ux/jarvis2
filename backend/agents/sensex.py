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

        range_percent = ((high - low) / low) * 100

        if close > (low + (high - low) * 0.7):
            return Signal.BUY
        elif close < (low + (high - low) * 0.3):
            return Signal.SELL
        else:
            return Signal.HOLD
