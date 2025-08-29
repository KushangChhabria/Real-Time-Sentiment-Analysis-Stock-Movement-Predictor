from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional


class Settings(BaseSettings):
    # Stock symbols to track
    symbols: List[str] = Field(default_factory=lambda: ["AAPL", "AMZN", "MSFT", "TSLA"], alias="SYMBOLS")

    # HuggingFace model for sentiment
    huggingface_model: str = Field(default="yiyanghkust/finbert-tone", alias="HUGGINGFACE_MODEL")

    # API keys
    newsapi_key: Optional[str] = Field(default=None, alias="NEWSAPI_KEY")
    alphavantage_key: Optional[str] = Field(default=None, alias="ALPHAVANTAGE_KEY")
    finnhub_key: Optional[str] = Field(default=None, alias="FINNHUB_KEY")

    # Polling intervals
    news_poll_interval: int = Field(default=60, alias="NEWS_POLL_INTERVAL")
    price_poll_interval: int = Field(default=60, alias="PRICE_POLL_INTERVAL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
