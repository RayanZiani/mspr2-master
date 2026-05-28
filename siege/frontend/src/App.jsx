import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import { Coffee, LayoutDashboard, Bell, Database } from 'lucide-react'
import { ToastProvider } from './components/Toast'
import { useDbHealth } from './hooks/useDbHealth'
import Dashboard from './pages/Dashboard'
import LotView from './pages/LotView'
import AlertsPage from './pages/AlertsPage'

function Navbar() {
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
    <nav className="navbar">
      <NavLink to="/" className="navbar-brand">
        <Coffee size={18} className="navbar-icon" />
        <span className="navbar-title">FutureKawa</span>
        <div className="navbar-sep" />
        <span className="navbar-sub">Supervision IoT</span>
      </NavLink>
      <div className="navbar-links">
        <NavLink
          to="/"
          end
          className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
        >
          <LayoutDashboard size={14} />
          Dashboard
        </NavLink>
        <NavLink
          to="/alertes"
          className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
        >
          <Bell size={14} />
          Alertes
        </NavLink>
        <span className={`nav-link nav-status ${statusCls}`} title={title}>
          <Database size={14} />
          DB
          <span className="db-dot" aria-hidden="true" />
        </span>
      </div>
    </nav>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/lots/:lotId" element={<LotView />} />
            <Route path="/alertes" element={<AlertsPage />} />
          </Routes>
        </main>
      </ToastProvider>
    </BrowserRouter>
  )
}
