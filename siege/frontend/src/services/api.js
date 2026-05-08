const BASE = import.meta.env.VITE_API_BASE_URL || '/api'

async function get(path) {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export const api = {
  getStocks: () => get('/stocks/'),
  getMesures: (lotId) => get(`/mesures/?lot_id=${lotId}`),
  getAlertes: () => get('/alertes/'),
}
