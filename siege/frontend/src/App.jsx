import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import LotView from './pages/LotView'
import AlertsPage from './pages/AlertsPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/lots/:lotId" element={<LotView />} />
        <Route path="/alertes" element={<AlertsPage />} />
      </Routes>
    </BrowserRouter>
  )
}
