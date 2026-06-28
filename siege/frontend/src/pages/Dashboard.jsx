import { useState, useMemo, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Package, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react'
import { useStocks } from '../hooks/useStocks'
import { useToast } from '../components/Toast'
import LocationFilters from '../components/LocationFilters'
import LotList from '../components/LotList'
import { useLotLocationFilters } from '../hooks/useLotLocationFilters'
import { exportLotsCsv } from '../utils/exportCsv'
import { formatTimeAgo } from '../utils/time'

export default function Dashboard() {
  const {
    data: stocksData,
    isLoading,
    isError,
    error,
    refetch,
    isFetching,
    dataUpdatedAt,
  } = useStocks()
  const [search, setSearch] = useState('')
  const [statusFilters, setStatusFilters] = useState([])
  const [now, setNow] = useState(Date.now())
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

  const {
    selectedPays,
    setSelectedPays,
    selectedExploitation,
    setSelectedExploitation,
    selectedEntrepot,
    setSelectedEntrepot,
    exploitationOptions,
    entrepotOptions,
    locationFilteredLots,
  } = useLotLocationFilters(allLots)

  const filteredLots = useMemo(() => {
    const q = search.trim().toLowerCase()
    return locationFilteredLots.filter((lot) => {
      const matchesSearch = q.length === 0
        || (lot.id || '').toLowerCase().includes(q)
        || (lot.exploitation || '').toLowerCase().includes(q)
        || (lot.entrepot || '').toLowerCase().includes(q)

      const matchesStatus = statusFilters.length === 0 || statusFilters.includes(lot.statut)

      return matchesSearch && matchesStatus
    })
  }, [locationFilteredLots, search, statusFilters])

  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 10_000)
    return () => clearInterval(timer)
  }, [])

  const lastSync = dataUpdatedAt ? formatTimeAgo(dataUpdatedAt, now) : 'jamais'

  function toggleStatus(status) {
    setStatusFilters((prev) => (
      prev.includes(status)
        ? prev.filter((s) => s !== status)
        : [...prev, status]
    ))
  }

  function onExport() {
    if (!filteredLots.length) {
      toast('Aucune ligne a exporter', 'info')
      return
    }
    exportLotsCsv(filteredLots, 'stocks')
    toast('Export CSV termine', 'success')
  }

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

  if (isError) {
    return (
      <div className="card empty-state error-state">
        <p style={{ fontWeight: 700 }}>Erreur de chargement des stocks</p>
        <p style={{ fontSize: '0.8rem' }}>{error?.message || 'API indisponible'}</p>
        <button className="btn" onClick={() => refetch()}>
          Reessayer
        </button>
      </div>
    )
  }

  return (
    <div>
      <div className="page-header">
        <div className="page-title-row">
          <h1 className="page-title">Stocks</h1>
          <div className="page-actions">
            <span className="sync-info" title="Derniere mise a jour des donnees">
              Derniere synchro: {lastSync}
            </span>
            <button className="btn btn-light" onClick={() => refetch()} disabled={isFetching}>
              {isFetching ? 'Rafraichissement…' : 'Rafraichir'}
            </button>
            <button className="btn" onClick={onExport}>Exporter CSV</button>
          </div>
        </div>
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

      <LocationFilters
        selectedPays={selectedPays}
        onPaysChange={setSelectedPays}
        selectedExploitation={selectedExploitation}
        onExploitationChange={setSelectedExploitation}
        selectedEntrepot={selectedEntrepot}
        onEntrepotChange={setSelectedEntrepot}
        exploitationOptions={exploitationOptions}
        entrepotOptions={entrepotOptions}
      />

      <div className="toolbar mb-2">
        <input
          className="input"
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Rechercher lot, exploitation ou entrepot"
        />
        <label className="filter-item">
          <input
            type="checkbox"
            checked={statusFilters.includes('conforme')}
            onChange={() => toggleStatus('conforme')}
          />
          {' '}
          Conforme
        </label>
        <label className="filter-item">
          <input
            type="checkbox"
            checked={statusFilters.includes('alerte')}
            onChange={() => toggleStatus('alerte')}
          />
          {' '}
          Alerte
        </label>
        <label className="filter-item">
          <input
            type="checkbox"
            checked={statusFilters.includes('perime')}
            onChange={() => toggleStatus('perime')}
          />
          {' '}
          Perime
        </label>
      </div>

      <LotList
        lots={filteredLots}
        onSelect={lot => navigate(`/lots/${lot.id}`, { state: { lot } })}
      />
    </div>
  )
}
