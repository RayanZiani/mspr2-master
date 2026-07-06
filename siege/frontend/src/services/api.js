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
  const url = new URL(fullUrl, globalThis.location.origin)
  Object.entries(params || {}).forEach(([k, v]) => {
    if (v == null || v === '') return
    url.searchParams.set(k, v)
  })

  const headers = {}
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`
  if (body == null) {
    delete headers['Content-Type']
  } else {
    headers['Content-Type'] = 'application/json'
  }

  const res = await fetch(url.toString(), {
    method,
    headers,
    body: body == null ? undefined : JSON.stringify(body),
  })

  if (res.status === 401) {
    clearSession()
    if (globalThis.location.pathname !== '/login') globalThis.location.href = '/login'
    throw new Error('Session expirée, veuillez vous reconnecter.')
  }

  if (res.ok) {
    return res.json()
  }
  let msg = `Erreur serveur (HTTP ${res.status}).`
  try {
    const err = await res.json()
    const d = err?.detail
    if (typeof d === 'string') msg = d
    else if (Array.isArray(d) && d[0]?.msg) msg = d[0].msg
  } catch {
    /* ignore */
  }
  throw new Error(msg)
}

async function get(path, params = {}) {
  return request(path, { method: 'GET', params })
}

export const api = {
  getStocks: () => get('/stocks/'),
  getMesures: (lotId) => get('/mesures/', { lot_id: lotId }),
  getAlertes: () => get('/alertes/'),
  getSeuils: () => get('/config/seuils'),
  updateSeuils: (code, payload) => request(`/config/seuils/${encodeURIComponent(code)}`, { method: 'PATCH', body: payload }),
  getWebhookStatus: () => get('/config/webhooks/status'),
  testWebhook: () => request('/config/webhooks/test', { method: 'POST' }),
  login: (username, password) => request('/auth/login', { method: 'POST', body: { username, password } }),
  me: () => get('/auth/me'),
  listUsers: () => get('/users/'),
  createUser: (payload) => request('/users/', { method: 'POST', body: payload }),
  updateUser: (username, payload) => request(`/users/${encodeURIComponent(username)}`, { method: 'PATCH', body: payload }),
  listGestionExploitations: () => get('/gestion/exploitations'),
  createGestionExploitation: (payload) => request('/gestion/exploitations', { method: 'POST', body: payload }),
  updateGestionExploitation: (id, payload) => request(`/gestion/exploitations/${id}`, { method: 'PATCH', body: payload }),
  deleteGestionExploitation: (id) => request(`/gestion/exploitations/${id}`, { method: 'DELETE' }),
  listGestionEntrepots: () => get('/gestion/entrepots'),
  createGestionEntrepot: (payload) => request('/gestion/entrepots', { method: 'POST', body: payload }),
  updateGestionEntrepot: (id, payload) => request(`/gestion/entrepots/${id}`, { method: 'PATCH', body: payload }),
  deleteGestionEntrepot: (id) => request(`/gestion/entrepots/${id}`, { method: 'DELETE' }),
  listGestionLots: () => get('/gestion/lots'),
  createGestionLot: (payload) => request('/gestion/lots', { method: 'POST', body: payload }),
  updateGestionLot: (id, payload) => request(`/gestion/lots/${encodeURIComponent(id)}`, { method: 'PATCH', body: payload }),
  getDbHealth: async () => {
    // Compat: certains environnements n'ont que /health.
    try {
      return await get('/health/db')
    } catch {
      return await get('/health')
    }
  },
}
