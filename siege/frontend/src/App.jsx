import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import { Coffee, LayoutDashboard, Bell } from 'lucide-react'
import { ToastProvider } from './components/Toast'
import Dashboard from './pages/Dashboard'
import LotView from './pages/LotView'
import AlertsPage from './pages/AlertsPage'

function Navbar() {
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
