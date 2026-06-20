import { getPaysCode, getRole, getSession } from './session'

function _b64UrlDecode(str) {
  try {
    const s = String(str || '').replace(/-/g, '+').replace(/_/g, '/')
    const pad = s.length % 4 === 0 ? '' : '='.repeat(4 - (s.length % 4))
    const json = atob(s + pad)
    return json
  } catch {
    return null
  }
}

function decodeJwtPayload(token) {
  const parts = String(token || '').split('.')
  if (parts.length !== 3) return null
  const raw = _b64UrlDecode(parts[1])
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

function getJwtClaims() {
  const { token } = getSession()
  if (!token) return null
  return decodeJwtPayload(token)
}

function getEffectiveRole() {
  const claims = getJwtClaims()
  return String(claims?.role || getRole() || 'USER').toUpperCase()
}

function getEffectivePaysCode() {
  const claims = getJwtClaims()
  const fromToken = claims?.pays_code
  if (fromToken === null || fromToken === undefined || fromToken === '') return getPaysCode()
  return String(fromToken)
}

const COUNTRY_SLUG_BY_PAYS_CODE = {
  BRESIL: 'bresil',
  EQUATEUR: 'equateur',
  COLOMBIE: 'colombie',
}

export const ROLE_LABELS = {
  SUPER_ADMIN: 'Super Admin',
  ADMIN: 'Administrateur',
  USER: 'Utilisateur',
}

export function roleLabel(role) {
  return ROLE_LABELS[String(role || '').toUpperCase()] || role
}

export function UserPermissions() {
  const role = getEffectiveRole()
  const paysCode = String(getEffectivePaysCode() || '').toUpperCase()

  const isSuperAdmin = role === 'SUPER_ADMIN'
  const isAdmin = role === 'ADMIN' || isSuperAdmin
  const isSiegeUser = role === 'USER' && paysCode === 'SIEGE'

  function canManageUsers() {
    return isSuperAdmin
  }

  function canConfigThresholds() {
    return isAdmin
  }

  function canViewMultiPays() {
    return isAdmin || isSiegeUser
  }

  function canWriteLots() {
    if (isAdmin) return true
    if (isSiegeUser) return false
    return role === 'USER' && Boolean(COUNTRY_SLUG_BY_PAYS_CODE[paysCode])
  }

  function allowedPaysSlugs() {
    if (canViewMultiPays()) return null
    const slug = COUNTRY_SLUG_BY_PAYS_CODE[paysCode]
    return slug ? new Set([slug]) : new Set()
  }

  function getAlertRecipientByPays(pays_code) {
    switch (String(pays_code || '').toUpperCase()) {
      case 'BRESIL':
        return 'resp.br@futurekawa.com'
      case 'EQUATEUR':
        return 'resp.eq@futurekawa.com'
      case 'COLOMBIE':
        return 'resp.co@futurekawa.com'
      case 'SIEGE':
        return 'admin@futurekawa.com'
      default:
        return null
    }
  }

  return {
    role,
    paysCode,
    isSuperAdmin,
    isAdmin,
    isSiegeUser,
    canManageUsers,
    canConfigThresholds,
    canViewMultiPays,
    canWriteLots,
    allowedPaysSlugs,
    getAlertRecipientByPays,
  }
}
