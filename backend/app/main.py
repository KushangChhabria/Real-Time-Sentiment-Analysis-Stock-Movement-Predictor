from __future__ import annotations
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from .config import settings
from .models import SentimentResult
from .services.sentiment_service import SentimentService
from .services.news_service import NewsService
from .services.price_service import PriceService
from .services.predictor_service import PredictorService
from .services.stream_manager import StreamManager


app = FastAPI(title="Real-Time Sentiment & Stock Predictor", version="0.2.0")

# Enable frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In prod, restrict origins!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate services
sentiment = SentimentService(model_name=settings.huggingface_model)
news = NewsService(api_key=settings.newsapi_key, sentiment=sentiment)
prices = PriceService()
predictor = PredictorService()
stream = StreamManager(
    symbols=settings.symbols,
    sentiment=sentiment,
    news=news,
    prices=prices,
    predictor=predictor,
    news_poll_interval=settings.news_poll_interval,
    price_poll_interval=settings.price_poll_interval,
)


@app.on_event("startup")
async def _startup():
    asyncio.create_task(stream.start_background())


@app.get("/api/ping")
def ping():
    return {"status": "ok"}


@app.post("/api/sentiment", response_model=List[SentimentResult])
def classify_texts(texts: List[str]):
    """Classify a batch of raw text strings into sentiment labels."""
    return sentiment.score_texts(texts)


@app.websocket("/ws/stream")
async def ws_stream(websocket: WebSocket, symbol: str):
    """Live stream of price, sentiment, and prediction updates for a given symbol."""
    await stream.connect(symbol, websocket)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        stream.disconnect(symbol, websocket)
