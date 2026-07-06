import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { PackagePlus } from 'lucide-react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../services/api'
import { useToast } from '../components/Toast'
import Select2Like from '../components/Select2Like'

const PAYS_LABELS = {
  bresil: 'Brésil',
  equateur: 'Équateur',
  colombie: 'Colombie',
}

const STATUT_OPTIONS = [
  { value: 'conforme', label: 'Conforme' },
  { value: 'alerte', label: 'Alerte' },
  { value: 'perime', label: 'Périmé' },
]

function paysLabel(slug) {
  return PAYS_LABELS[slug] || slug
}

export default function GestionLotsPage() {
  const toast = useToast()
  const qc = useQueryClient()

  const { data: lots, isLoading, isError } = useQuery({
    queryKey: ['gestion-lots'],
    queryFn: api.listGestionLots,
    refetchInterval: 60_000,
  })

  const { data: exploitations } = useQuery({
    queryKey: ['gestion-exploitations'],
    queryFn: api.listGestionExploitations,
  })

  const { data: entrepots } = useQuery({
    queryKey: ['gestion-entrepots'],
    queryFn: api.listGestionEntrepots,
  })

  const rows = useMemo(() => (Array.isArray(lots) ? lots : []), [lots])
  const exps = useMemo(() => (Array.isArray(exploitations) ? exploitations : []), [exploitations])
  const ents = useMemo(() => (Array.isArray(entrepots) ? entrepots : []), [entrepots])

  const [createOpen, setCreateOpen] = useState(false)
  const [exploitationId, setExploitationId] = useState(null)
  const [entrepotId, setEntrepotId] = useState(null)
  const [saving, setSaving] = useState(false)

  const expOptions = exps.map(e => ({
    value: e.id,
    label: `${paysLabel(e.pays)} — ${e.nom}`,
  }))

  const entOptions = ents
    .filter(e => !exploitationId || e.exploitation_id === exploitationId || e.exploitation_id == null)
    .map(e => ({
      value: e.id,
      label: `${paysLabel(e.pays)} — ${e.nom}`,
    }))

  async function onCreate(e) {
    e.preventDefault()
    if (!exploitationId || !entrepotId) {
      toast('Sélectionnez une exploitation et un entrepôt', 'error')
      return
    }
    setSaving(true)
    try {
      await api.createGestionLot({ exploitation_id: exploitationId, entrepot_id: entrepotId })
      toast('Lot créé', 'success')
      setCreateOpen(false)
      setExploitationId(null)
      setEntrepotId(null)
      await qc.invalidateQueries({ queryKey: ['gestion-lots'] })
      await qc.invalidateQueries({ queryKey: ['stocks'] })
    } catch (err) {
      toast(err instanceof Error ? err.message : 'Création impossible', 'error')
    } finally {
      setSaving(false)
    }
  }

  async function changeStatut(lot, statut) {
    try {
      await api.updateGestionLot(lot.id, { statut })
      await qc.invalidateQueries({ queryKey: ['gestion-lots'] })
      await qc.invalidateQueries({ queryKey: ['stocks'] })
    } catch {
      toast('Impossible de modifier le statut', 'error')
    }
  }

  async function expedier(lot) {
    if (!globalThis.confirm(`Expédier le lot ${lot.id} ?`)) return
    try {
      await api.updateGestionLot(lot.id, { expedier: true })
      toast('Lot expédié', 'success')
      await qc.invalidateQueries({ queryKey: ['gestion-lots'] })
      await qc.invalidateQueries({ queryKey: ['stocks'] })
    } catch {
      toast('Expédition impossible', 'error')
    }
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
      <div className="card">
        <div style={{ fontWeight: 700, marginBottom: 6 }}>Erreur</div>
        <div>Impossible de charger les lots.</div>
      </div>
    )
  }

  return (
    <div>
      <div className="page-header users-header">
        <div>
          <h1 className="page-title">Gestion des lots</h1>
          <p className="page-sub">Création, statut et expédition des lots en stock</p>
        </div>
        <button className="users-add" onClick={() => setCreateOpen(true)}>
          <PackagePlus size={16} />
          Nouveau lot
        </button>
      </div>

      <div className="card users-card">
        <div className="users-table gestion-lots-table">
          <div className="users-row users-head">
            <div>ID</div>
            <div>Pays</div>
            <div>Exploitation</div>
            <div>Entrepôt</div>
            <div>Entrée</div>
            <div>Statut</div>
            <div />
          </div>
          {rows.map(lot => (
            <div className="users-row" key={lot.id}>
              <div>
                <Link to={`/lots/${lot.id}`} className="users-username">
                  {lot.id.slice(0, 8)}…
                </Link>
              </div>
              <div>{paysLabel(lot.pays)}</div>
              <div>{lot.exploitation}</div>
              <div>{lot.entrepot}</div>
              <div className="users-muted">
                {lot.date_stockage ? new Date(lot.date_stockage).toLocaleString('fr-FR') : '—'}
              </div>
              <div>
                <Select2Like
                  className="users-select2"
                  isSearchable={false}
                  isClearable={false}
                  value={STATUT_OPTIONS.find(o => o.value === lot.statut) || STATUT_OPTIONS[0]}
                  options={STATUT_OPTIONS}
                  onChange={opt => changeStatut(lot, opt?.value || 'conforme')}
                />
              </div>
              <div className="users-actions">
                <button type="button" className="users-btn" onClick={() => expedier(lot)}>
                  Expédier
                </button>
              </div>
            </div>
          ))}
          {rows.length === 0 && (
            <div className="empty-state" style={{ padding: '2rem 1rem' }}>
              <div>Aucun lot en stock.</div>
            </div>
          )}
        </div>
      </div>

      {createOpen && (
        <div
          className="users-modal-backdrop"
          onMouseDown={() => {
            if (!saving) setCreateOpen(false)
          }}
        >
          <div className="users-modal" role="dialog" aria-modal="true" onMouseDown={ev => ev.stopPropagation()}>
            <div className="users-modal-title">Nouveau lot</div>
            <form onSubmit={onCreate} className="users-form">
              <label className="users-label">
                <span>Exploitation</span>
                <Select2Like
                  className="users-select2 modal"
                  isSearchable
                  isClearable={false}
                  value={expOptions.find(o => o.value === exploitationId) || null}
                  options={expOptions}
                  onChange={opt => {
                    setExploitationId(opt?.value ?? null)
                    setEntrepotId(null)
                  }}
                  placeholder="Choisir…"
                />
              </label>
              <label className="users-label">
                <span>Entrepôt</span>
                <Select2Like
                  className="users-select2 modal"
                  isSearchable
                  isClearable={false}
                  value={entOptions.find(o => o.value === entrepotId) || null}
                  options={entOptions}
                  onChange={opt => setEntrepotId(opt?.value ?? null)}
                  placeholder="Choisir…"
                />
              </label>
              <div className="users-modal-actions">
                <button type="button" className="users-btn secondary" onClick={() => setCreateOpen(false)} disabled={saving}>
                  Annuler
                </button>
                <button className="users-btn primary" disabled={saving}>
                  {saving ? 'Création…' : 'Créer'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
