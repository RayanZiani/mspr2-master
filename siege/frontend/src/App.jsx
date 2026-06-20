import { useEffect, useRef, useState, lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, NavLink, Navigate, useLocation, useNavigate } from 'react-router-dom'
import {
  Coffee,
  LayoutDashboard,
  Bell,
  Activity,
  ShieldCheck,
  LogOut,
  ChevronDown,
  Users,
  Settings2,
  Menu,
  X,
} from 'lucide-react'
import { ToastProvider } from './components/Toast'
import { useDbHealth } from './hooks/useDbHealth'
import { clearSession, getSession, isAuthed } from './auth/session'
import { UserPermissions } from './auth/permissions'

// Chargement différé des pages : réduit le bundle initial (AG Grid, Recharts,
// react-select ne sont téléchargés qu'à l'ouverture des pages concernées).
const Dashboard = lazy(() => import('./pages/Dashboard'))
const LotView = lazy(() => import('./pages/LotView'))
const AlertsPage = lazy(() => import('./pages/AlertsPage'))
const Login = lazy(() => import('./pages/Login'))
const UsersPage = lazy(() => import('./pages/UsersPage'))
const MesuresPage = lazy(() => import('./pages/MesuresPage'))
const HealthPage = lazy(() => import('./pages/HealthPage'))
const CapteursConfigPage = lazy(() => import('./pages/CapteursConfigPage'))

function PageFallback() {
  return (
    <div className="loading">
      <div className="spinner" />
      <span>Chargement…</span>
    </div>
  )
}

function RequireAuth({ children }) {
  if (!isAuthed()) return <Navigate to="/login" replace />
  return children
}

function RequirePerm({ can, children }) {
  if (!isAuthed()) return <Navigate to="/login" replace />
  const perms = UserPermissions()
  if (!can(perms)) return <Navigate to="/" replace />
  return children
}

function AccountMenu({ statusCls, statusTitle }) {
  const navigate = useNavigate()
  const { username } = getSession()
  const perms = UserPermissions()
  const role = perms.role
  const [open, setOpen] = useState(false)
  const ref = useRef(null)
  const initial = (username || '?').trim().charAt(0).toUpperCase()

  useEffect(() => {
    function onDoc(e) {
      if (!ref.current) return
      if (!ref.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', onDoc)
    return () => document.removeEventListener('mousedown', onDoc)
  }, [])

  function go(to) {
    setOpen(false)
    navigate(to)
  }

  function logout() {
    clearSession()
    window.location.href = '/login'
  }

  return (
    <div className="account" ref={ref}>
      <button type="button" className="account-btn" onClick={() => setOpen(v => !v)} aria-haspopup="menu" aria-expanded={open}>
        <span className="account-avatar">{initial}</span>
        <span className="account-btn-text">{username || 'Compte'}</span>
        <ChevronDown size={14} className={`account-chevron${open ? ' open' : ''}`} />
      </button>

      {open && (
        <div className="account-menu" role="menu">
          <div className="account-meta">
            <div className="account-user">{username || 'Compte'}</div>
            <div className="account-role">{role}</div>
          </div>

          <button type="button" className="account-item" onClick={() => go('/sante')} role="menuitem" title={statusTitle}>
            <ShieldCheck size={15} />
            <span>Santé système</span>
            <span className={`status-mini ${statusCls}`} aria-hidden="true" />
          </button>

          {perms.isAdmin && (
            <button type="button" className="account-item" onClick={() => go('/config/capteurs')} role="menuitem">
              <Settings2 size={15} />
              <span>Config capteurs</span>
            </button>
          )}

          {perms.isAdmin && (
            <button type="button" className="account-item" onClick={() => go('/users')} role="menuitem">
              <Users size={15} />
              <span>Utilisateurs</span>
            </button>
          )}

          <div className="account-divider" />

          <button type="button" className="account-item danger" onClick={logout} role="menuitem">
            <LogOut size={15} />
            <span>Déconnexion</span>
          </button>
        </div>
      )}
    </div>
  )
}

function Navbar() {
  const loc = useLocation()
  const authed = isAuthed()
  const onLogin = loc.pathname === '/login'
  const perms = UserPermissions()
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => { setMenuOpen(false) }, [loc.pathname])

  const { data, isFetching, isError } = useDbHealth()
  const isOk = data?.ok === true || data?.status === 'ok'
  const isLoading = !data && isFetching && !isError

  const statusCls = isLoading ? 'db-loading' : isOk ? 'db-ok' : 'db-bad'
  const statusTitle = isLoading
    ? 'Système : vérification en cours'
    : isOk
      ? 'Système opérationnel (base de données OK)'
      : `Système dégradé${isError ? ' (API indisponible)' : ' (base de données KO)'}`

  const navItems = [
    { to: '/', end: true, Icon: LayoutDashboard, label: 'Dashboard', show: true },
    { to: '/mesures', Icon: Activity, label: 'Mesures', show: true },
    { to: '/alertes', Icon: Bell, label: 'Alertes', show: perms.isAdmin || perms.isSiegeUser },
  ].filter(i => i.show)

  return (
    <nav className={`navbar${onLogin ? ' navbar-login' : ''}`}>
      <NavLink to="/" className="navbar-brand">
        <span className="navbar-logo"><Coffee size={17} /></span>
        <span className="navbar-title">FutureKawa</span>
        <div className="navbar-sep" />
        <span className="navbar-sub">Supervision IoT</span>
      </NavLink>

      {authed && !onLogin && (
        <>
          <div className="navbar-nav">
            {navItems.map(({ to, end, Icon, label }) => (
              <NavLink key={to} to={to} end={end} className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
                <Icon size={15} />
                <span>{label}</span>
              </NavLink>
            ))}
          </div>

          <div className="navbar-actions">
            <NavLink to="/sante" className={({ isActive }) => `status-pill ${statusCls}${isActive ? ' active' : ''}`} title={statusTitle}>
              <span className="db-dot" aria-hidden="true" />
              <span className="status-pill-text">Système</span>
            </NavLink>

            <AccountMenu statusCls={statusCls} statusTitle={statusTitle} />

            <button
              type="button"
              className="navbar-burger"
              onClick={() => setMenuOpen(v => !v)}
              aria-label={menuOpen ? 'Fermer le menu' : 'Ouvrir le menu'}
              aria-expanded={menuOpen}
            >
              {menuOpen ? <X size={19} /> : <Menu size={19} />}
            </button>
          </div>

          {menuOpen && (
            <div className="navbar-mobile">
              {navItems.map(({ to, end, Icon, label }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={end}
                  className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
                  onClick={() => setMenuOpen(false)}
                >
                  <Icon size={16} />
                  <span>{label}</span>
                </NavLink>
              ))}
            </div>
          )}
        </>
      )}
    </nav>
  )
}

export default function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <ToastProvider>
        <Navbar />
        <main className="main-content">
          <Suspense fallback={<PageFallback />}>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/"
              element={<RequireAuth><Dashboard /></RequireAuth>}
            />
            <Route
              path="/lots/:lotId"
              element={<RequireAuth><LotView /></RequireAuth>}
            />
            <Route
              path="/alertes"
              element={<RequirePerm can={p => p.isAdmin || p.isSiegeUser}><AlertsPage /></RequirePerm>}
            />
            <Route
              path="/mesures"
              element={<RequireAuth><MesuresPage /></RequireAuth>}
            />
            <Route
              path="/sante"
              element={<RequireAuth><HealthPage /></RequireAuth>}
            />
            <Route
              path="/config/capteurs"
              element={<RequirePerm can={p => p.canConfigThresholds()}><CapteursConfigPage /></RequirePerm>}
            />
            <Route
              path="/users"
              element={<RequirePerm can={p => p.canManageUsers()}><UsersPage /></RequirePerm>}
            />
          </Routes>
          </Suspense>
        </main>
      </ToastProvider>
    </BrowserRouter>
  )
}
