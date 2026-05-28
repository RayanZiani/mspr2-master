export function getSession() {
  const token = localStorage.getItem('fk_token')
  const role = localStorage.getItem('fk_role')
  const username = localStorage.getItem('fk_username')
  return { token, role, username }
}

export function setSession({ token, role, username }) {
  if (token) localStorage.setItem('fk_token', token)
  if (role) localStorage.setItem('fk_role', role)
  if (username) localStorage.setItem('fk_username', username)
}

export function setProfile({ pays_code, email }) {
  if (pays_code !== undefined) {
    if (pays_code === null || pays_code === '') localStorage.removeItem('fk_pays_code')
    else localStorage.setItem('fk_pays_code', String(pays_code))
  }
  if (email !== undefined) {
    if (email === null || email === '') localStorage.removeItem('fk_email')
    else localStorage.setItem('fk_email', String(email))
  }
}

export function getPaysCode() {
  return localStorage.getItem('fk_pays_code') || ''
}

export function getEmail() {
  return localStorage.getItem('fk_email') || ''
}

export function clearSession() {
  localStorage.removeItem('fk_token')
  localStorage.removeItem('fk_role')
  localStorage.removeItem('fk_username')
  localStorage.removeItem('fk_pays_code')
  localStorage.removeItem('fk_email')
}

export function isAuthed() {
  return Boolean(localStorage.getItem('fk_token'))
}

export function getRole() {
  return localStorage.getItem('fk_role') || 'USER'
}

