from __future__ import annotations
from typing import List
import httpx
import logging
from ..models import SentimentResult
from .sentiment_service import SentimentService
from ..config import settings


log = logging.getLogger(__name__)

NEWSAPI_URL = "https://newsapi.org/v2/everything"
FINNHUB_NEWS_URL = "https://finnhub.io/api/v1/company-news"


class NewsService:
    def __init__(self, api_key: str | None, sentiment: SentimentService):
        self.api_key = api_key
        self.finnhub_key = settings.finnhub_key
        self.sentiment = sentiment

    async def fetch_newsapi_texts(self, symbol: str, limit: int = 10) -> List[str]:
        """Fetch news from NewsAPI"""
        if not self.api_key:
            return []
        params = {
            "q": symbol,
            "language": "en",
            "pageSize": limit,
            "sortBy": "publishedAt",
        }
        headers = {"X-Api-Key": self.api_key}
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(NEWSAPI_URL, params=params, headers=headers)
                r.raise_for_status()
                data = r.json()
        except Exception as e:
            log.warning(f"NewsAPI fetch failed: {e}")
            return []

        texts: List[str] = []
        for a in data.get("articles", []):
            title = a.get("title") or ""
            desc = a.get("description") or ""
            combined = f"{title}. {desc}".strip()
            if combined:
                texts.append(combined)
        return texts

    async def fetch_finnhub_texts(self, symbol: str, limit: int = 10) -> List[str]:
        """Fetch company news from Finnhub"""
        if not self.finnhub_key:
            return []

        # Finnhub requires from/to dates
        import datetime
        today = datetime.date.today()
        past = today - datetime.timedelta(days=7)

        params = {
            "symbol": symbol,
            "from": past.isoformat(),
            "to": today.isoformat(),
            "token": self.finnhub_key,
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(FINNHUB_NEWS_URL, params=params)
                r.raise_for_status()
                data = r.json()
        except Exception as e:
            log.warning(f"Finnhub news fetch failed: {e}")
            return []

        texts: List[str] = []
        for a in data[:limit]:
            headline = a.get("headline") or ""
            summary = a.get("summary") or ""
            combined = f"{headline}. {summary}".strip()
            if combined:
                texts.append(combined)
        return texts

    async def fetch_news_texts(self, symbol: str, limit: int = 10) -> List[str]:
        """Try NewsAPI first, fall back to Finnhub if needed"""
        texts = await self.fetch_newsapi_texts(symbol, limit)
        if not texts:
            texts = await self.fetch_finnhub_texts(symbol, limit)
        return texts

    async def score_latest_news(self, symbol: str, limit: int = 10) -> List[SentimentResult]:
        texts = await self.fetch_news_texts(symbol, limit=limit)
        if not texts:
            return []
        return self.sentiment.score_texts(texts, symbol=symbol, source="news")
