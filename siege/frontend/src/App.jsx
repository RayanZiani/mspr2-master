import { useEffect, useRef, useState } from 'react'
import { BrowserRouter, Routes, Route, NavLink, Navigate, useLocation } from 'react-router-dom'
import {
  Coffee,
  LayoutDashboard,
  Bell,
  Activity,
  ShieldCheck,
  Database,
  LogOut,
  UserCircle2,
  ChevronDown,
  Users,
} from 'lucide-react'
import { ToastProvider } from './components/Toast'
import { useDbHealth } from './hooks/useDbHealth'
import { clearSession, getRole, getSession, isAuthed } from './auth/session'
import Dashboard from './pages/Dashboard'
import LotView from './pages/LotView'
import AlertsPage from './pages/AlertsPage'
import Login from './pages/Login'
import UsersPage from './pages/UsersPage'
import MesuresPage from './pages/MesuresPage'
import HealthPage from './pages/HealthPage'

function RequireAuth({ children }) {
  if (!isAuthed()) return <Navigate to="/login" replace />
  return children
}

function RequireRole({ roles, children }) {
  if (!isAuthed()) return <Navigate to="/login" replace />
  const role = getRole()
  if (!roles.includes(role)) return <Navigate to="/" replace />
  return children
}

function AccountMenu() {
  const { username } = getSession()
  const role = getRole()
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    function onDoc(e) {
      if (!ref.current) return
      if (!ref.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', onDoc)
    return () => document.removeEventListener('mousedown', onDoc)
  }, [])

  function logout() {
    clearSession()
    window.location.href = '/login'
  }

  return (
    <div className="account" ref={ref}>
      <button type="button" className="account-btn" onClick={() => setOpen(v => !v)}>
        <UserCircle2 size={16} />
        <span className="account-btn-text">{username || 'Compte'}</span>
        <ChevronDown size={14} className={`account-chevron${open ? ' open' : ''}`} />
      </button>

      {open && (
        <div className="account-menu" role="menu">
          <div className="account-meta">
            <div className="account-user">{username || '—'}</div>
            <div className="account-role">{role}</div>
          </div>
          <button type="button" className="account-item" onClick={logout} role="menuitem">
            <LogOut size={14} />
            Déconnexion
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
  const role = getRole()

  const { data, isFetching, isError } = useDbHealth()
  const isOk = data?.ok === true || data?.status === 'ok'
  const isKo = data?.ok === false
  const isLoading = !data && isFetching && !isError

  const statusCls = isLoading ? 'db-loading' : isOk ? 'db-ok' : 'db-bad'
  const title = isLoading
    ? 'Base de données : vérification…'
    : isOk
      ? 'Base de données : OK'
      : `Base de données : KO${isError ? ' (API indisponible)' : ''}`

  return (
    <nav className={`navbar${onLogin ? ' navbar-login' : ''}`}>
      <NavLink to="/" className="navbar-brand">
        <Coffee size={18} className="navbar-icon" />
        <span className="navbar-title">FutureKawa</span>
        <div className="navbar-sep" />
        <span className="navbar-sub">Supervision IoT</span>
      </NavLink>
      <div className="navbar-links">
        {authed && !onLogin && (
          <>
            <NavLink
              to="/"
              end
              className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
            >
              <LayoutDashboard size={14} />
              Dashboard
            </NavLink>
            <NavLink
              to="/mesures"
              className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
            >
              <Activity size={14} />
              Mesures
            </NavLink>
            <NavLink
              to="/sante"
              className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
            >
              <ShieldCheck size={14} />
              Santé
            </NavLink>
            {role === 'ADMIN' && (
              <NavLink
                to="/alertes"
                className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
              >
                <Bell size={14} />
                Alertes
              </NavLink>
            )}
            {role === 'ADMIN' && (
              <NavLink
                to="/users"
                className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
              >
                <Users size={14} />
                Utilisateurs
              </NavLink>
            )}
          </>
        )}
        <span className={`nav-link nav-status ${statusCls}`} title={title}>
          <Database size={14} />
          {onLogin ? (isOk ? 'DB connectée' : 'DB') : 'DB'}
          <span className="db-dot" aria-hidden="true" />
        </span>
        {authed && !onLogin && <AccountMenu />}
      </div>
    </nav>
  )
}

export default function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <ToastProvider>
        <Navbar />
        <main className="main-content">
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
              element={<RequireRole roles={['ADMIN']}><AlertsPage /></RequireRole>}
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
              path="/users"
              element={<RequireRole roles={['ADMIN']}><UsersPage /></RequireRole>}
            />
          </Routes>
        </main>
      </ToastProvider>
    </BrowserRouter>
  )
}
