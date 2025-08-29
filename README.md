# Real-Time Sentiment Analysis & Stock Movement Predictor

Tech: **Python, PyTorch, Transformers, FastAPI, WebSockets, React (Vite), Recharts**

Features:
- FinBERT-based sentiment scoring (yiyanghkust/finbert-tone) for financial news.
- News ingestion (NewsAPI; X/Twitter support stub for future integration).
- Intraday price polling (Yahoo Finance 1m updates; optional Finnhub/Alpha Vantage connectors).
- Online predictor (SGDClassifier) that estimates next-minute price movement based on recent sentiment & price trends.
- FastAPI WebSocket server streaming live sentiment, price, and prediction probabilities.
- React dashboard displaying:
- Stock price (1-minute intervals)
- Sentiment (5-minute rolling average)
- Predicted Up Probability (0–1)
- Interactive ticker selector

> ⚠️ **API keys required (free tiers available)**: set them in `.env` (copy from `.env.example`).

---

## Prerequisites (install once)

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

Open the app URL shown by Vite.

Dashboard functionality:
- Select stock ticker
- View live price updates
- Observe real-time sentiment & prediction probability

## Environment (.env)

```
# Symbols to track (comma-separated)
SYMBOLS=AAPL,AMZN,MSFT,TSLA

# Sentiment model (HuggingFace)
HUGGINGFACE_MODEL=yiyanghkust/finbert-tone

# API Keys
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
│  │  ├─ main.py                # FastAPI entry
│  │  ├─ config.py
│  │  ├─ models.py              # Pydantic models
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

## How It Works
# 1) Backend:
- Polls live stock prices and latest news.
- Calculates 5-minute rolling sentiment average per stock.
- Updates online logistic regression model with sentiment & 1-minute price changes.
- Streams price, sentiment, and prediction probability via WebSocket.

# 2) Frontend:
- Connects to WebSocket for live updates.
- Stores the latest 300 data points.
- Renders PriceChart and SentimentStream charts.
- Provides interactive ticker selection.

## Dashboard Charts
# Price Chart:
- Line chart of live 1-minute prices.
# Sentiment & Prediction:
- Area chart with two series:
- Blue: 5-minute rolling sentiment (-1 to 1)
- Green: Predicted Up Probability (0–1)
- Reference line at 0 for easy visualization of positive/negative sentiment.

## Key Learnings / Skills Demonstrated
- Real-time data streaming (WebSockets)
- Asynchronous Python & FastAPI
- Online machine learning (incremental SGDClassifier)
- Data visualization using React & Recharts
- API integration for financial and news data
