import { useMemo, useState, useEffect } from 'react'
import { Activity } from 'lucide-react'
import LocationFilters from '../components/LocationFilters'
import Charts from '../components/Charts'
import { useStocks } from '../hooks/useStocks'
import { useMesures } from '../hooks/useMesures'
import { useLotLocationFilters } from '../hooks/useLotLocationFilters'
import { UserPermissions } from '../auth/permissions'
import { groupLotsByOrigin } from '../utils/groupLotsByOrigin'

export default function MesuresPage() {
  const {
    data: stocksData,
    isLoading: stocksLoading,
    isError: stocksError,
    error: stocksErr,
    refetch: refetchStocks,
  } = useStocks()

  const [selectedLotId, setSelectedLotId] = useState('')

  const allLots = useMemo(() => {
    if (!stocksData) return []
    return stocksData.flatMap((p) =>
      (p.data || []).map((lot) => ({ ...lot, pays: lot.pays || p.pays }))
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

  const perms = UserPermissions()
  const lotGroups = useMemo(() => {
    if (!perms.isSuperAdmin || !locationFilteredLots.length) return null
    return groupLotsByOrigin(locationFilteredLots, { includePays: !selectedPays })
  }, [locationFilteredLots, perms.isSuperAdmin, selectedPays])

  useEffect(() => {
    if (!locationFilteredLots.length) {
      setSelectedLotId('')
      return
    }
    if (!selectedLotId || !locationFilteredLots.find((lot) => lot.id === selectedLotId)) {
      setSelectedLotId(locationFilteredLots[0].id)
    }
  }, [locationFilteredLots, selectedLotId])

  const currentLot = useMemo(
    () => locationFilteredLots.find((l) => l.id === selectedLotId),
    [locationFilteredLots, selectedLotId]
  )

  const {
    data: mesuresData,
    isLoading: mesuresLoading,
    isError: mesuresError,
    error: mesuresErr,
    refetch: refetchMesures,
    isFetching: mesuresFetching,
  } = useMesures(selectedLotId)

  const rows = useMemo(() => {
    if (!Array.isArray(mesuresData)) return []
    return [...mesuresData]
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      .slice(0, 12)
  }, [mesuresData])

  if (stocksLoading) {
    return (
      <div className="loading">
        <div className="spinner" />
        <span>Chargement des lots…</span>
      </div>
    )
  }

  if (stocksError) {
    return (
      <div className="card empty-state error-state">
        <p style={{ fontWeight: 700 }}>Erreur de chargement des lots</p>
        <p style={{ fontSize: '0.8rem' }}>{stocksErr?.message || 'API indisponible'}</p>
        <button className="btn" onClick={() => refetchStocks()}>
          Reessayer
        </button>
      </div>
    )
  }

  return (
    <div>
      <div className="page-header">
        <div className="page-title-row">
          <h1 className="page-title">Mesures</h1>
          <button className="btn btn-light" onClick={() => refetchMesures()} disabled={!selectedLotId || mesuresFetching}>
            {mesuresFetching ? 'Rafraichissement…' : 'Rafraichir'}
          </button>
        </div>
        <p className="page-sub">Visualiser les releves temperature/humidite par lot</p>
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
        <label className="filter-item" htmlFor="lot-select">Lot</label>
        <select
          id="lot-select"
          className="input"
          value={selectedLotId}
          onChange={(e) => setSelectedLotId(e.target.value)}
        >
          {!locationFilteredLots.length && <option value="">Aucun lot disponible</option>}
          {lotGroups
            ? lotGroups.map((group) => (
              <optgroup key={group.key} label={group.label}>
                {group.lots.map((lot) => (
                  <option key={lot.id} value={lot.id}>
                    {lot.id}
                  </option>
                ))}
              </optgroup>
            ))
            : locationFilteredLots.map((lot) => (
              <option key={lot.id} value={lot.id}>
                {lot.id} - {lot.exploitation || '-'} / {lot.entrepot || '-'}
              </option>
            ))}
        </select>
      </div>

      {!selectedLotId ? (
        <div className="card empty-state">
          <Activity size={36} className="empty-icon" />
          <p style={{ fontWeight: 500 }}>Aucun lot a afficher</p>
          <p style={{ fontSize: '0.8rem' }}>Chargez des stocks pour consulter les mesures.</p>
        </div>
      ) : mesuresLoading ? (
        <div className="loading">
          <div className="spinner" />
          <span>Chargement des mesures…</span>
        </div>
      ) : mesuresError ? (
        <div className="card empty-state error-state">
          <p style={{ fontWeight: 700 }}>Erreur de chargement des mesures</p>
          <p style={{ fontSize: '0.8rem' }}>{mesuresErr?.message || 'API indisponible'}</p>
          <button className="btn" onClick={() => refetchMesures()}>
            Reessayer
          </button>
        </div>
      ) : (
        <>
          <div className="card mb-2">
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Lot courant: <strong>{currentLot?.id || '-'}</strong>
            </p>
          </div>

          <Charts data={mesuresData} pays={currentLot?.pays} />

          <div className="card">
            <div className="section-header">
              Derniers releves
            </div>
            {!rows.length ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>
                Aucune mesure disponible pour ce lot.
              </p>
            ) : (
              <div className="simple-table-wrap">
                <table className="simple-table">
                  <thead>
                    <tr>
                      <th>Horodatage</th>
                      <th>Temperature</th>
                      <th>Humidite</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((m) => (
                      <tr key={`${m.timestamp}-${m.temperature}-${m.humidity}`}>
                        <td>{new Date(m.timestamp).toLocaleString('fr-FR')}</td>
                        <td>{Number(m.temperature).toFixed(1)} °C</td>
                        <td>{Number(m.humidity).toFixed(1)} %</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
