import { useParams, useLocation, Link } from 'react-router-dom'
import { useMemo } from 'react'
import { ArrowLeft } from 'lucide-react'
import { useStocks } from '../hooks/useStocks'
import { useMesures } from '../hooks/useMesures'
import { useSeuils } from '../hooks/useSeuils'
import LotDetail from '../components/LotDetail'
import Charts from '../components/Charts'

export default function LotView() {
  const { lotId } = useParams()
  const { state } = useLocation()
  const { data: stocksData } = useStocks()

  const lot = state?.lot ?? (stocksData || [])
    .flatMap(p => (p.data || []).map(l => ({ ...l, pays: l.pays || p.pays })))
    .find(l => l.id === lotId)

  const {
    data: mesuresData,
    isLoading: mesuresLoading,
    isError: mesuresError,
    error,
    refetch,
  } = useMesures(lotId)
  const { bySlug: seuilsBySlug } = useSeuils()

  const latestMesure = useMemo(() => {
    if (!Array.isArray(mesuresData) || !mesuresData.length) return null
    return [...mesuresData].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))[0]
  }, [mesuresData])

  return (
    <div>
      <Link to="/" className="back-link">
        <ArrowLeft size={14} />
        Retour aux stocks
      </Link>

      <div className="page-header">
        <h1 className="page-title">Détail du lot</h1>
        <p className="page-sub">Historique des relevés IoT depuis la mise en stockage</p>
      </div>

      <LotDetail lot={lot} seuilsBySlug={seuilsBySlug} latestMesure={latestMesure} />

      {mesuresLoading ? (
        <div className="loading">
          <div className="spinner" />
          <span>Chargement des mesures…</span>
        </div>
      ) : mesuresError ? (
        <div className="card empty-state error-state">
          <p style={{ fontWeight: 700 }}>Erreur de chargement des mesures</p>
          <p style={{ fontSize: '0.8rem' }}>{error?.message || 'API indisponible'}</p>
          <button className="btn" onClick={() => refetch()}>
            Reessayer
          </button>
        </div>
      ) : (
        <Charts data={mesuresData} pays={lot?.pays} seuilsBySlug={seuilsBySlug} />
      )}
    </div>
  )
}
