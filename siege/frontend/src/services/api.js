const BASE = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '')

function clearSession() {
  localStorage.removeItem('fk_token')
  localStorage.removeItem('fk_role')
  localStorage.removeItem('fk_username')
}

function getToken() {
  return localStorage.getItem('fk_token')
}

async function request(path, { method = 'GET', params, body } = {}) {
  const fullUrl = `${BASE}${path}`
  const url = new URL(fullUrl, window.location.origin)
  Object.entries(params || {}).forEach(([k, v]) => {
    if (v != null && v !== '') url.searchParams.set(k, v)
  })

  const headers = {}
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`
  if (body != null) headers['Content-Type'] = 'application/json'

  const res = await fetch(url.toString(), {
    method,
    headers,
    body: body != null ? JSON.stringify(body) : undefined,
  })

  if (res.status === 401) {
    // Token expiré / invalide (ou ancien token sans role) -> reset session et retour login.
    clearSession()
    if (window.location.pathname !== '/login') window.location.href = '/login'
    throw new Error(`HTTP 401 — ${url.toString()}`)
  }

  if (!res.ok) throw new Error(`HTTP ${res.status} — ${url.toString()}`)
  return res.json()
}

async function get(path, params = {}) {
  return request(path, { method: 'GET', params })
}

export const api = {
  getStocks: () => get('/stocks/'),
  getMesures: (lotId) => get('/mesures/', { lot_id: lotId }),
  getAlertes: () => get('/alertes/'),
  login: (username, password) => request('/auth/login', { method: 'POST', body: { username, password } }),
  me: () => get('/auth/me'),
  listUsers: () => get('/users/'),
  createUser: (payload) => request('/users/', { method: 'POST', body: payload }),
  updateUser: (username, payload) => request(`/users/${encodeURIComponent(username)}`, { method: 'PATCH', body: payload }),
  getDbHealth: async () => {
    // Compat: certains environnements n'ont que /health.
    try {
      return await get('/health/db')
    } catch {
      return await get('/health')
    }
  },
}
