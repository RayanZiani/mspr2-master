import { useMemo, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlertTriangle, XCircle, PackageCheck } from 'lucide-react'
import { useStocks } from '../hooks/useStocks'
import { useSeuils } from '../hooks/useSeuils'
import AlertBadge from '../components/AlertBadge'
import { useToast } from '../components/Toast'
import { exportLotsCsv } from '../utils/exportCsv'
import { formatTimeAgo } from '../utils/time'

export default function AlertsPage() {
  const {
    data: stocksData,
    isLoading,
    isError,
    error,
    refetch,
    isFetching,
    dataUpdatedAt,
  } = useStocks()
  const { bySlug: seuilsBySlug } = useSeuils()
  const navigate = useNavigate()
  const toast = useToast()
  const [now, setNow] = useState(Date.now())

  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 10_000)
    return () => clearInterval(timer)
  }, [])

  const alertes = useMemo(() => {
    if (!stocksData) return []
    return stocksData.flatMap(p =>
      (p.data || [])
        .filter(l => l.statut && l.statut !== 'conforme')
        .map(l => ({ ...l, pays: l.pays || p.pays }))
    )
  }, [stocksData])

  const perimes  = alertes.filter(l => l.statut === 'perime')
  const enAlerte = alertes.filter(l => l.statut === 'alerte')
  const lastSync = dataUpdatedAt ? formatTimeAgo(dataUpdatedAt, now) : 'jamais'

  function onExport() {
    if (!alertes.length) {
      toast('Aucune alerte a exporter', 'info')
      return
    }
    exportLotsCsv(alertes, 'alertes')
    toast('Export CSV termine', 'success')
  }

  if (isLoading) {
    return (
      <div className="loading">
        <div className="spinner" />
        <span>Chargement…</span>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="card empty-state error-state">
        <p style={{ fontWeight: 700 }}>Erreur de chargement des alertes</p>
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
          <h1 className="page-title">Alertes actives</h1>
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
        <p className="page-sub">
          {alertes.length === 0
            ? 'Aucune alerte, tous les lots sont conformes'
            : `${alertes.length} lot(s) en situation anormale`}
        </p>
      </div>

      {alertes.length === 0 ? (
        <div className="card empty-state">
          <PackageCheck size={36} className="empty-icon" />
          <p style={{ fontWeight: 500 }}>Tous les lots sont conformes</p>
          <p style={{ fontSize: '0.8rem' }}>Aucune action requise.</p>
        </div>
      ) : (
        <>
          {perimes.length > 0 && (
            <div className="mb-3">
              <div className="section-header danger">
                <XCircle size={13} />
                Lots périmés ({perimes.length})
              </div>
              <div className="alert-list">
                {perimes.map(l => (
                  <AlertBadge
                    key={l.id}
                    lot={l}
                    seuilsBySlug={seuilsBySlug}
                    onClick={() => navigate(`/lots/${l.id}`, { state: { lot: l } })}
                  />
                ))}
              </div>
            </div>
          )}
          {enAlerte.length > 0 && (
            <div>
              <div className="section-header warning">
                <AlertTriangle size={13} />
                Conditions hors plage ({enAlerte.length})
              </div>
              <div className="alert-list">
                {enAlerte.map(l => (
                  <AlertBadge
                    key={l.id}
                    lot={l}
                    seuilsBySlug={seuilsBySlug}
                    onClick={() => navigate(`/lots/${l.id}`, { state: { lot: l } })}
                  />
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
