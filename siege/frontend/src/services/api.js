const BASE = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '')

async function get(path, params = {}) {
  const fullUrl = `${BASE}${path}`
  const url = new URL(fullUrl, window.location.origin)
  Object.entries(params).forEach(([k, v]) => {
    if (v != null && v !== '') url.searchParams.set(k, v)
  })
  const res = await fetch(url.toString())
  if (!res.ok) throw new Error(`HTTP ${res.status} — ${url.toString()}`)
  return res.json()
}

export const api = {
  getStocks: () => get('/stocks/'),
  getMesures: (lotId) => get('/mesures/', { lot_id: lotId }),
  getAlertes: () => get('/alertes/'),
  getDbHealth: async () => {
    // Compat: certains environnements n'ont que /health.
    try {
      return await get('/health/db')
    } catch {
      return await get('/health')
    }
  },
}
