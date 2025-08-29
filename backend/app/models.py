from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class SentimentScore(BaseModel):
    label: str
    score: float


class SentimentResult(BaseModel):
    text: str
    timestamp: datetime
    scores: List[SentimentScore]
    dominant: str = Field(..., description="Label with highest score")
    symbol: Optional[str] = None
    source: Optional[str] = None
    meta: Optional[Dict] = None


class PricePoint(BaseModel):
    symbol: str
    timestamp: datetime
    price: float
    change_1m: Optional[float] = None


class StreamTick(BaseModel):
    symbol: str
    timestamp: datetime
    price: Optional[float] = None
    change_1m: Optional[float] = None
    sentiment_avg_5m: Optional[float] = Field(
        None, description="[-1, 1] average sentiment over past 5 minutes"
    )
    pred_up_prob: Optional[float] = Field(
        None, description="Model-predicted probability of price going up"
    )
