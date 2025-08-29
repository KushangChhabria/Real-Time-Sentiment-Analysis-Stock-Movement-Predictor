# app/services/price_service.py
from __future__ import annotations
from typing import Optional
import aiohttp
import pandas as pd
from ..config import settings


class PriceService:
    def __init__(self):
        self._latest: dict[str, float] = {}
        self.finnhub_key: str = settings.finnhub_key
        self.alphavantage_key: str = settings.alphavantage_key

    async def get_price_now(self, symbol: str) -> Optional[float]:
        """
        Get the latest real-time price using Finnhub API.
        Falls back to last cached price if request fails.
        """
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={self.finnhub_key}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    data = await resp.json()

            price = data.get("c")  # current price
            if price and price > 0:
                self._latest[symbol] = price
                return price
        except Exception:
            pass

        # fallback to last known
        return self._latest.get(symbol)

    async def get_change_1m(self, symbol: str) -> Optional[float]:
        """
        Get 1-minute price change using Alpha Vantage intraday (1min interval).
        """
        url = (
            f"https://www.alphavantage.co/query"
            f"?function=TIME_SERIES_INTRADAY&symbol={symbol}"
            f"&interval=1min&apikey={self.alphavantage_key}&outputsize=compact"
        )
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    data = await resp.json()

            ts = data.get("Time Series (1min)")
            if not ts:
                return None

            sorted_times = sorted(ts.keys(), reverse=True)
            if len(sorted_times) < 2:
                return None

            last = float(ts[sorted_times[0]]["4. close"])
            prev = float(ts[sorted_times[1]]["4. close"])
            return (last - prev) / prev if prev != 0 else None

        except Exception:
            return None

    async def get_series(self, symbol: str, lookback_minutes: int = 60) -> pd.DataFrame:
        """
        Get intraday price series from Alpha Vantage (1-minute interval).
        Returns last `lookback_minutes` rows as a DataFrame.
        """
        url = (
            f"https://www.alphavantage.co/query"
            f"?function=TIME_SERIES_INTRADAY&symbol={symbol}"
            f"&interval=1min&apikey={self.alphavantage_key}&outputsize=compact"
        )
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    data = await resp.json()

            ts = data.get("Time Series (1min)")
            if not ts:
                return pd.DataFrame()

            df = pd.DataFrame.from_dict(ts, orient="index", dtype=float)
            df.index = pd.to_datetime(df.index)
            df.sort_index(inplace=True)

            return df.tail(lookback_minutes)

        except Exception:
            return pd.DataFrame()
