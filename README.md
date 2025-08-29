# Real-Time Sentiment Analysis & Stock Movement Predictor

Tech: **Python, PyTorch, Transformers, FastAPI, WebSockets, React (Vite), Recharts**

This starter implements:
- FinBERT-based sentiment scoring (default: `yiyanghkust/finbert-tone`).
- News + (optional) X/Twitter ingestion hooks (NewsAPI implemented; X via placeholder).
- Intraday price polling (Yahoo Finance 1m as default; Finnhub/Alpha Vantage connectors ready).
- Online predictor (SGDClassifier) to estimate next-interval price direction.
- FastAPI WebSocket stream combining live sentiment + price + prediction.
- React dashboard that visualizes prices and sentiment in real time and lets you pick tickers.

> ⚠️ **API keys required (free tiers available)**: set them in `.env` (copy from `.env.example`).

---

## Prereqs (install once)

- Python 3.10+
- Node.js 18+ (LTS recommended)
- Git (optional)

## 1) Backend — FastAPI

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
cp ../.env.example .env  # then edit .env
uvicorn app.main:app --reload --port 8000
```

Open API docs: http://localhost:8000/docs

## 2) Frontend — React (Vite)

```bash
cd ../frontend
npm install
npm run dev
```

Open the app URL shown by Vite (usually http://localhost:5173).

## Environment (.env)

```
# Comma-separated symbols to track by default
SYMBOLS=AAPL,AMZN,MSFT,TSLA

# Sentiment model; keep default unless you know what you're doing
HUGGINGFACE_MODEL=yiyanghkust/finbert-tone

# (Optional) News & market data keys (free tiers)
NEWSAPI_KEY=
ALPHAVANTAGE_KEY=
FINNHUB_KEY=

# Polling intervals (seconds)
NEWS_POLL_INTERVAL=60
PRICE_POLL_INTERVAL=60
```

## Project Structure

```
realtime-sentiment-stocks/
├─ backend/
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ config.py
│  │  ├─ models.py
│  │  ├─ utils/
│  │  │  └─ text.py
│  │  └─ services/
│  │     ├─ sentiment_service.py
│  │     ├─ news_service.py
│  │     ├─ price_service.py
│  │     ├─ predictor_service.py
│  │     └─ stream_manager.py
│  └─ requirements.txt
├─ frontend/
│  ├─ index.html
│  ├─ package.json
│  ├─ vite.config.js
│  └─ src/
│     ├─ main.jsx
│     ├─ App.jsx
│     ├─ api.js
│     └─ components/
│        ├─ TickerSelector.jsx
│        ├─ PriceChart.jsx
│        └─ SentimentStream.jsx
└─ .env.example
```

## Notes
- X/Twitter data ingestion is provided as a **stub**. To use it, add your own token + logic in `news_service.py` or create a new `twitter_service.py` (marked TODO in the code).
- Intraday prices default to **Yahoo Finance (yfinance)** 1-minute polling. For low-latency streaming, switch to **Finnhub WebSocket** (connector TODO noted in code).

---

### Benchmarks
This starter is designed to be a foundation. Reported metrics (e.g., ~80% sentiment accuracy, +12% over a naïve baseline) depend heavily on data quality and evaluation setup. Use the included pipeline and adapt it to your datasets/targets.
