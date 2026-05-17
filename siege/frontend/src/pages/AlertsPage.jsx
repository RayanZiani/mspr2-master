import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlertTriangle, XCircle, PackageCheck } from 'lucide-react'
import { useStocks } from '../hooks/useStocks'
import AlertBadge from '../components/AlertBadge'

export default function AlertsPage() {
  const { data: stocksData, isLoading } = useStocks()
  const navigate = useNavigate()

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

  if (isLoading) {
    return (
      <div className="loading">
        <div className="spinner" />
        <span>Chargement…</span>
      </div>
    )
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Alertes actives</h1>
        <p className="page-sub">
          {alertes.length === 0
            ? 'Aucune alerte — tous les lots sont conformes'
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
