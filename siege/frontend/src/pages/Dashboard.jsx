import { useState, useMemo, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Package, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react'
import { useStocks } from '../hooks/useStocks'
import { useToast } from '../components/Toast'
import CountrySelector from '../components/CountrySelector'
import LotList from '../components/LotList'

export default function Dashboard() {
  const { data: stocksData, isLoading, isError } = useStocks()
  const [selectedPays, setSelectedPays] = useState('')
  const navigate = useNavigate()
  const toast = useToast()

  useEffect(() => {
    if (isError) toast('Erreur de chargement', 'error')
  }, [isError, toast])

  const allLots = useMemo(() => {
    if (!stocksData) return []
    return stocksData.flatMap(p =>
      (p.data || []).map(lot => ({ ...lot, pays: lot.pays || p.pays }))
    )
  }, [stocksData])

  const filteredLots = useMemo(() =>
    selectedPays ? allLots.filter(l => l.pays === selectedPays) : allLots,
    [allLots, selectedPays]
  )

  const stats = useMemo(() => ({
    total:     allLots.length,
    conformes: allLots.filter(l => l.statut === 'conforme').length,
    alertes:   allLots.filter(l => l.statut === 'alerte').length,
    perimes:   allLots.filter(l => l.statut === 'perime').length,
  }), [allLots])

  if (isLoading) {
    return (
      <div className="loading">
        <div className="spinner" />
        <span>Chargement des stocks…</span>
      </div>
    )
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Stocks</h1>
        <p className="page-sub">Vue consolidée multi-pays · Actualisation toutes les 30 s</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon neutral"><Package size={17} /></div>
          <div className="stat-body">
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">Total lots</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon success"><CheckCircle2 size={17} /></div>
          <div className="stat-body">
            <div className="stat-value">{stats.conformes}</div>
            <div className="stat-label">Conformes</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon warning"><AlertTriangle size={17} /></div>
          <div className="stat-body">
            <div className="stat-value">{stats.alertes}</div>
            <div className="stat-label">En alerte</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon danger"><XCircle size={17} /></div>
          <div className="stat-body">
            <div className="stat-value">{stats.perimes}</div>
            <div className="stat-label">Périmés</div>
          </div>
        </div>
      </div>

      <CountrySelector value={selectedPays} onChange={setSelectedPays} />

      <div className="grid-wrapper">
        <LotList
          lots={filteredLots}
          onSelect={lot => navigate(`/lots/${lot.id}`, { state: { lot } })}
        />
      </div>
    </div>
  )
}
