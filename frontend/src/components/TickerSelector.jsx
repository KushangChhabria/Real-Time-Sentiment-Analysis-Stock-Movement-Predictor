import React from 'react'

export function TickerSelector({ value, onChange }) {
  const list = ['AAPL','AMZN','MSFT','TSLA','GOOGL','META','NVDA']

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <label htmlFor="ticker">Ticker</label>
      <select id="ticker" value={value} onChange={(e) => onChange(e.target.value)}>
        {list.map(t => <option key={t} value={t}>{t}</option>)}
      </select>
    </div>
  )
}
