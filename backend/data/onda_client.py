"""Onda Trading API client for XAUUSD and forex data."""
import os
import time
from datetime import datetime
from typing import Dict, Optional
import requests

class OndaClient:
    """
    Onda Trading integration for live XAUUSD pricing (forex/commodities).
    Requires: ONDA_API_KEY, ONDA_ACCESS_TOKEN environment variables
    """

    def __init__(self):
        self.api_key = os.getenv("ONDA_API_KEY", "")
        self.access_token = os.getenv("ONDA_ACCESS_TOKEN", "")
        self.base_url = "https://api.onda.trading/v1"
        self.rate_limit_cooldowns = {}
        self.last_fetch = {}

    def get_live_data(self, symbol: str, quote_type: str = "XAUUSD") -> Dict:
        """
        Fetch live XAUUSD price from Onda Trading API.

        Args:
            symbol: Trading symbol (XAUUSD, EURUSD, etc.)
            quote_type: Quote type (LTP/OHLC)

        Returns:
            Dict with symbol, price, timestamp, OHLC data
        """

        # Check if credentials are real (not placeholders)
        if not self.api_key or self.api_key == "your_onda_api_key":
            return {
                "symbol": symbol,
                "close": 0,
                "status": "credentials_missing",
                "note": "Onda credentials not configured"
            }

        # Check cooldown from rate limiting
        if symbol in self.rate_limit_cooldowns:
            if time.time() < self.rate_limit_cooldowns[symbol]:
                return {"symbol": symbol, "close": 0, "status": "rate_limited"}
            del self.rate_limit_cooldowns[symbol]

        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "X-API-Key": self.api_key,
                "Content-Type": "application/json"
            }

            # Onda LTP endpoint for forex/commodities
            url = f"{self.base_url}/quotes/ltp"
            params = {"symbols": symbol}

            response = requests.get(url, headers=headers, params=params, timeout=5)

            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 120))
                self.rate_limit_cooldowns[symbol] = time.time() + retry_after
                print(f"⚠️  Onda rate limited: {symbol}, cooldown {retry_after}s")
                return {"symbol": symbol, "close": 0, "status": "rate_limited"}

            response.raise_for_status()
            data = response.json()

            if data.get("status") == "success" and data.get("data"):
                quote = data["data"].get(symbol, {})
                if quote and quote.get("ltp", 0) > 0:
                    return {
                        "symbol": symbol,
                        "close": float(quote.get("ltp", 0)),
                        "open": float(quote.get("open", 0) or 0),
                        "high": float(quote.get("high", 0) or 0),
                        "low": float(quote.get("low", 0) or 0),
                        "volume": int(quote.get("volume", 0) or 0),
                        "timestamp": datetime.utcnow().isoformat(),
                        "exchange": "ONDA",
                        "currency": "USD"
                    }

            print(f"⚠️  Onda API error for {symbol}: {data.get('message')}")
            return {"symbol": symbol, "close": 0, "status": "api_error"}

        except requests.exceptions.RequestException as e:
            print(f"⚠️  Onda connection error for {symbol}: {e}")
            return {"symbol": symbol, "close": 0, "status": "connection_error"}
        except Exception as e:
            print(f"⚠️  Onda client error for {symbol}: {e}")
            return {"symbol": symbol, "close": 0, "status": "error"}

    def get_xauusd_price(self) -> float:
        """
        Get current XAUUSD (Gold in USD) price.

        Returns:
            Float price in USD, or 0 if unavailable
        """
        data = self.get_live_data("XAUUSD")
        return data.get("close", 0)

    def get_multiple_prices(self, symbols: list) -> Dict:
        """
        Get prices for multiple forex/commodity symbols.

        Args:
            symbols: List of symbols (XAUUSD, EURUSD, GBPUSD, etc.)

        Returns:
            Dict mapping symbol -> price
        """
        result = {}
        for symbol in symbols:
            data = self.get_live_data(symbol)
            result[symbol] = data.get("close", 0)
        return result
