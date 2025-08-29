export const API_BASE = 'http://localhost:8000'

export function wsUrl(symbol) {
  const url = new URL(API_BASE.replace('http', 'ws') + '/ws/stream')
  url.searchParams.set('symbol', symbol)
  return url.toString()
}
