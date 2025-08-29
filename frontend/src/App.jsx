import React, { useEffect, useMemo, useRef, useState } from 'react'
import { TickerSelector } from './components/TickerSelector.jsx'
import { PriceChart } from './components/PriceChart.jsx'
import { SentimentStream } from './components/SentimentStream.jsx'
import { wsUrl } from './api.js'

export default function App() {
  const [symbol, setSymbol] = useState('AAPL')
  const [streamData, setStreamData] = useState([])

  // WebSocket connection
  useEffect(() => {
    let active = true
    let ws = new WebSocket(wsUrl(symbol))
    ws.onmessage = (evt) => {
      const msg = JSON.parse(evt.data)
      if (!active) return
      setStreamData((prev) => [...prev.slice(-300), msg])
    }
    // periodically ping server to keep the connection alive
    const ping = setInterval(() => {
      try { ws.send('ping') } catch {}
    }, 10000)

    return () => {
      active = false
      clearInterval(ping)
      ws.close()
    }
  }, [symbol])

  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', padding: 16, maxWidth: 1200, margin: '0 auto' }}>
      <h1>Real-Time Sentiment & Stock Predictor</h1>
      <TickerSelector value={symbol} onChange={setSymbol} />
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 16 }}>
        <PriceChart data={streamData} />
        <SentimentStream data={streamData} />
      </div>
      <p style={{ opacity: 0.7, fontSize: 12 }}>
        Data sources: News sentiment (NewsAPI if key provided), Prices (Yahoo Finance 1m polling). Predictor trains online from recent data.
      </p>
    </div>
  )
}
