from agents.base import BaseAgent, Signal
from typing import Dict, List

class StocksAgent(BaseAgent):
    def __init__(self):
        super().__init__("STOCKS")
        self.symbols = ["RELIANCE", "TCS", "INFY", "WIPRO", "ICICIBANK"]

    def get_symbols(self) -> List[str]:
        return self.symbols

    def analyze(self, market_data: Dict) -> Signal:
        if not market_data:
            return Signal.HOLD

        close = market_data.get("close", 0)
        open_price = market_data.get("open", 0)
        volume = market_data.get("volume", 0)

        if volume == 0:
            return Signal.HOLD

        change_percent = ((close - open_price) / open_price) * 100 if open_price else 0

        if change_percent > 1.5:
            return Signal.BUY
        elif change_percent < -1.5:
            return Signal.SELL
        else:
            return Signal.HOLD
