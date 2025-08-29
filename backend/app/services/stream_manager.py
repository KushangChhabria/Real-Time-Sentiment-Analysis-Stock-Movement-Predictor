# app/services/stream_manager.py
from __future__ import annotations
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from fastapi import WebSocket, WebSocketDisconnect
import logging

from ..models import StreamTick
from .sentiment_service import SentimentService
from .news_service import NewsService
from .price_service import PriceService
from .predictor_service import PredictorService

log = logging.getLogger(__name__)


class StreamManager:
    def __init__(
        self,
        symbols: List[str],
        sentiment: SentimentService,
        news: NewsService,
        prices: PriceService,
        predictor: PredictorService,
        news_poll_interval: int = 60,
        price_poll_interval: int = 60,
    ):
        self.symbols = symbols
        self.sentiment = sentiment
        self.news = news
        self.prices = prices
        self.predictor = predictor
        self.news_poll_interval = news_poll_interval
        self.price_poll_interval = price_poll_interval

        # connections per symbol
        self.connections: Dict[str, List[WebSocket]] = {s: [] for s in symbols}
        # rolling sentiment scalar samples per symbol: (timestamp, scalar)
        self.sentiment_buffer: Dict[str, List[tuple[datetime, float]]] = {s: [] for s in symbols}
        # last known price per symbol
        self.last_price: Dict[str, float] = {}

    async def connect(self, symbol: str, websocket: WebSocket):
        await websocket.accept()
        self.connections.setdefault(symbol, []).append(websocket)
        log.info(f"WebSocket connected for {symbol}, total={len(self.connections[symbol])}")

    def disconnect(self, symbol: str, websocket: WebSocket):
        conns = self.connections.get(symbol, [])
        if websocket in conns:
            conns.remove(websocket)
            log.info(f"WebSocket disconnected for {symbol}, remaining={len(conns)}")

    async def _broadcast(self, symbol: str, payload: dict):
        dead = []
        for ws in list(self.connections.get(symbol, [])):
            try:
                await ws.send_json(payload)
            except (WebSocketDisconnect, RuntimeError):
                dead.append(ws)
        for ws in dead:
            self.disconnect(symbol, ws)

    async def start_background(self):
        asyncio.create_task(self._poll_news_loop())
        asyncio.create_task(self._poll_price_loop())

    # -------------------------------
    # News Polling
    # -------------------------------
    async def _poll_news_loop(self):
        while True:
            try:
                await asyncio.gather(*(self._poll_news_for_symbol(s) for s in self.symbols))
            except Exception as e:
                log.error(f"Error in news polling: {e}")
            await asyncio.sleep(self.news_poll_interval)

    async def _poll_news_for_symbol(self, symbol: str):
        try:
            scored = await self.news.score_latest_news(symbol, limit=8)
        except Exception as e:
            log.warning(f"Failed to fetch/score news for {symbol}: {e}")
            return

        scalars = []
        for s in scored:
            try:
                val = self.sentiment.to_scalar(s)
                scalars.append((s.timestamp, val))
            except Exception as e:
                log.error(f"Sentiment scalar conversion failed for {symbol}: {e}")

        if scalars:
            self.sentiment_buffer.setdefault(symbol, []).extend(scalars)
            # drop > 1 hour old
            cutoff = datetime.utcnow() - timedelta(hours=1)
            self.sentiment_buffer[symbol] = [
                (t, v) for (t, v) in self.sentiment_buffer[symbol] if t >= cutoff
            ]

    def _sentiment_avg_5m(self, symbol: str) -> Optional[float]:
        now = datetime.utcnow()
        vals = [v for (t, v) in self.sentiment_buffer.get(symbol, []) if (now - t).total_seconds() <= 300]
        if not vals:
            return None
        return float(sum(vals) / len(vals))

    # -------------------------------
    # Price Polling
    # -------------------------------
    async def _poll_price_loop(self):
        while True:
            try:
                await asyncio.gather(*(self._poll_price_for_symbol(s) for s in self.symbols))
            except Exception as e:
                log.error(f"Error in price polling: {e}")
            await asyncio.sleep(self.price_poll_interval)

    async def _poll_price_for_symbol(self, symbol: str):
        try:
            price, change_1m = await asyncio.gather(
                self.prices.get_price_now(symbol),
                self.prices.get_change_1m(symbol),
            )
            if price is not None:
                self.last_price[symbol] = price
            await self._tick(symbol, price, change_1m)
        except Exception as e:
            log.warning(f"Failed to fetch price for {symbol}: {e}")

    # -------------------------------
    # Tick Handling
    # -------------------------------
    async def _tick(self, symbol: str, price: float | None, change_1m: float | None):
        avg5 = self._sentiment_avg_5m(symbol)

        # Update predictor if we have both sentiment & price movement
        if change_1m is not None and avg5 is not None:
            try:
                await self.predictor.update(symbol, avg5, 1 if change_1m > 0 else 0)
            except Exception as e:
                log.error(f"Predictor update failed for {symbol}: {e}")

        pred: float | None = None
        if avg5 is not None:
            try:
                raw_pred = await self.predictor.predict_proba(symbol, avg5)
                if raw_pred is not None:
                    # keep original probability (0-1) but scale later in frontend
                    pred = raw_pred
            except Exception as e:
                log.error(f"Prediction failed for {symbol}: {e}")

        payload = StreamTick(
            symbol=symbol,
            timestamp=datetime.utcnow(),
            price=price,
            change_1m=change_1m,
            sentiment_avg_5m=avg5 if avg5 is not None else 0,
            pred_up_prob=pred,
        ).model_dump(mode="json")

        await self._broadcast(symbol, payload)

