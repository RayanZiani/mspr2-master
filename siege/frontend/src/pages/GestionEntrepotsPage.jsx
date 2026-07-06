import { useMemo, useState } from 'react'
import { Warehouse } from 'lucide-react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../services/api'
import { useToast } from '../components/Toast'
import Select2Like from '../components/Select2Like'
import { UserPermissions } from '../auth/permissions'

const PAYS_SLUG_OPTIONS = [
  { value: 'bresil', label: 'Brésil' },
  { value: 'equateur', label: 'Équateur' },
  { value: 'colombie', label: 'Colombie' },
]

const PAYS_LABELS = Object.fromEntries(PAYS_SLUG_OPTIONS.map(o => [o.value, o.label]))

function defaultPaysSlug(perms) {
  const allowed = perms.allowedPaysSlugs()
  if (allowed && allowed.size === 1) return [...allowed][0]
  return 'bresil'
}

export default function GestionEntrepotsPage() {
  const toast = useToast()
  const qc = useQueryClient()
  const perms = UserPermissions()
  const multiPays = perms.canViewMultiPays()

  const { data, isLoading, isError } = useQuery({
    queryKey: ['gestion-entrepots'],
    queryFn: api.listGestionEntrepots,
    refetchInterval: 60_000,
  })

  const { data: exploitations } = useQuery({
    queryKey: ['gestion-exploitations'],
    queryFn: api.listGestionExploitations,
  })

  const rows = useMemo(() => (Array.isArray(data) ? data : []), [data])
  const exps = useMemo(() => (Array.isArray(exploitations) ? exploitations : []), [exploitations])

  const paysOptions = useMemo(() => {
    const allowed = perms.allowedPaysSlugs()
    if (allowed === null) return PAYS_SLUG_OPTIONS
    return PAYS_SLUG_OPTIONS.filter(o => allowed.has(o.value))
  }, [perms])

  const [createOpen, setCreateOpen] = useState(false)
  const [paysSlug, setPaysSlug] = useState(() => defaultPaysSlug(perms))
  const [nom, setNom] = useState('')
  const [adresse, setAdresse] = useState('')
  const [exploitationId, setExploitationId] = useState(null)
  const [saving, setSaving] = useState(false)

  const expOptions = exps
    .filter(e => e.pays === paysSlug)
    .map(e => ({ value: e.id, label: e.nom }))

  async function onCreate(e) {
    e.preventDefault()
    setSaving(true)
    try {
      await api.createGestionEntrepot({
        pays_slug: paysSlug,
        nom,
        adresse: adresse || null,
        exploitation_id: exploitationId,
      })
      toast('Entrepôt créé', 'success')
      setCreateOpen(false)
      setNom('')
      setAdresse('')
      setExploitationId(null)
      await qc.invalidateQueries({ queryKey: ['gestion-entrepots'] })
      await qc.invalidateQueries({ queryKey: ['stocks'] })
    } catch (err) {
      toast(err instanceof Error ? err.message : 'Création impossible', 'error')
    } finally {
      setSaving(false)
    }
  }

  async function removeEnt(ent) {
    if (!globalThis.confirm(`Supprimer l'entrepôt « ${ent.nom} » ?`)) return
    try {
      await api.deleteGestionEntrepot(ent.id)
      toast('Entrepôt supprimé', 'success')
      await qc.invalidateQueries({ queryKey: ['gestion-entrepots'] })
      await qc.invalidateQueries({ queryKey: ['stocks'] })
    } catch (err) {
      toast(err instanceof Error ? err.message : 'Suppression impossible', 'error')
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
        <div>Impossible de charger les entrepôts.</div>
      </div>
    )
  }

  return (
    <div>
      <div className="page-header users-header">
        <div>
          <h1 className="page-title">Gestion des entrepôts</h1>
          <p className="page-sub">
            {multiPays ? 'Tous les pays' : `Pays : ${PAYS_LABELS[paysSlug] || paysSlug}`}
          </p>
        </div>
        <button className="users-add" onClick={() => setCreateOpen(true)}>
          <Warehouse size={16} />
          Nouvel entrepôt
        </button>
      </div>

      <div className="card users-card">
        <div className="users-table gestion-entrepots-table">
          <div className="users-row users-head">
            <div>Pays</div>
            <div>Nom</div>
            <div>Exploitation</div>
            <div>Adresse</div>
            <div />
          </div>
          {rows.map(ent => (
            <div className="users-row" key={ent.id}>
              <div>{PAYS_LABELS[ent.pays] || ent.pays}</div>
              <div className="users-username">{ent.nom}</div>
              <div>{ent.exploitation_nom || '—'}</div>
              <div className="users-muted">{ent.adresse || '—'}</div>
              <div className="users-actions">
                <button type="button" className="users-btn" onClick={() => removeEnt(ent)}>
                  Supprimer
                </button>
              </div>
            </div>
          ))}
          {rows.length === 0 && (
            <div className="empty-state" style={{ padding: '2rem 1rem' }}>
              <div>Aucun entrepôt.</div>
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
            <div className="users-modal-title">Nouvel entrepôt</div>
            <form onSubmit={onCreate} className="users-form">
              {paysOptions.length > 1 && (
                <label className="users-label">
                  <span>Pays</span>
                  <Select2Like
                    className="users-select2 modal"
                    isSearchable={false}
                    isClearable={false}
                    value={paysOptions.find(o => o.value === paysSlug) || paysOptions[0]}
                    options={paysOptions}
                    onChange={opt => {
                      setPaysSlug(opt?.value || 'bresil')
                      setExploitationId(null)
                    }}
                  />
                </label>
              )}
              <label className="users-label">
                <span>Nom</span>
                <input className="users-input" value={nom} onChange={ev => setNom(ev.target.value)} required />
              </label>
              <label className="users-label">
                <span>Adresse</span>
                <input className="users-input" value={adresse} onChange={ev => setAdresse(ev.target.value)} />
              </label>
              <label className="users-label">
                <span>Exploitation</span>
                <Select2Like
                  className="users-select2 modal"
                  isSearchable
                  isClearable
                  value={expOptions.find(o => o.value === exploitationId) || null}
                  options={expOptions}
                  onChange={opt => setExploitationId(opt?.value ?? null)}
                  placeholder="Optionnel"
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
