import { useMemo } from 'react'
import { Database, CheckCircle2, XCircle } from 'lucide-react'
import { useDbHealth } from '../hooks/useDbHealth'
import { formatTimeAgo } from '../utils/time'

export default function HealthPage() {
  const { data, isLoading, isError, error, refetch, isFetching, dataUpdatedAt } = useDbHealth()

  const statusText = useMemo(() => {
    if (isLoading) return 'Verification en cours'
    if (isError) return 'API indisponible'
    if (data?.ok === true || data?.status === 'ok') return 'Base de donnees disponible'
    return 'Base de donnees indisponible'
  }, [data, isError, isLoading])

  const lastSync = dataUpdatedAt ? formatTimeAgo(dataUpdatedAt) : 'jamais'
  const isOk = data?.ok === true || data?.status === 'ok'

  return (
    <div>
      <div className="page-header">
        <div className="page-title-row">
          <h1 className="page-title">Sante systeme</h1>
          <button className="btn btn-light" onClick={() => refetch()} disabled={isFetching}>
            {isFetching ? 'Rafraichissement…' : 'Rafraichir'}
          </button>
        </div>
        <p className="page-sub">Etat de l'API siege et de la base de donnees</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className={`stat-icon ${isOk ? 'success' : 'danger'}`}>
            {isOk ? <CheckCircle2 size={17} /> : <XCircle size={17} />}
          </div>
          <div className="stat-body">
            <div className="stat-value" style={{ fontSize: '1rem', lineHeight: 1.2 }}>
              {statusText}
            </div>
            <div className="stat-label">Etat DB</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon neutral">
            <Database size={17} />
          </div>
          <div className="stat-body">
            <div className="stat-value" style={{ fontSize: '1rem', lineHeight: 1.2 }}>
              {lastSync}
            </div>
            <div className="stat-label">Derniere synchro</div>
          </div>
        </div>
      </div>

      {isError && (
        <div className="card empty-state error-state">
          <p style={{ fontWeight: 700 }}>Erreur de verification</p>
          <p style={{ fontSize: '0.8rem' }}>{error?.message || 'Service indisponible'}</p>
        </div>
      )}

      <div className="card">
        <div className="section-header">Endpoints utiles</div>
        <div className="simple-table-wrap">
          <table className="simple-table">
            <thead>
              <tr>
                <th>Service</th>
                <th>URL</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Health API</td>
                <td>/api/health</td>
              </tr>
              <tr>
                <td>Health DB</td>
                <td>/api/health/db</td>
              </tr>
              <tr>
                <td>Swagger</td>
                <td>/api/docs</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
