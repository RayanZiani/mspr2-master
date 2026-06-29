import { useMemo, useState } from 'react'
import { Building2, Warehouse } from 'lucide-react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../services/api'
import { useToast } from '../components/Toast'
import Select2Like from '../components/Select2Like'

const PAYS_SLUG_OPTIONS = [
  { value: 'bresil', label: 'Brésil' },
  { value: 'equateur', label: 'Équateur' },
  { value: 'colombie', label: 'Colombie' },
]

const PAYS_LABELS = Object.fromEntries(PAYS_SLUG_OPTIONS.map(o => [o.value, o.label]))

const TABS = [
  { id: 'exploitations', label: 'Exploitations', Icon: Building2 },
  { id: 'entrepots', label: 'Entrepôts', Icon: Warehouse },
]

export default function GestionReferentielsPage() {
  const toast = useToast()
  const qc = useQueryClient()
  const [tab, setTab] = useState('exploitations')

  const { data: exploitations, isLoading: loadExp, isError: errExp } = useQuery({
    queryKey: ['gestion-exploitations'],
    queryFn: api.listGestionExploitations,
    refetchInterval: 60_000,
  })

  const { data: entrepots, isLoading: loadEnt, isError: errEnt } = useQuery({
    queryKey: ['gestion-entrepots'],
    queryFn: api.listGestionEntrepots,
    refetchInterval: 60_000,
  })

  const exps = useMemo(() => (Array.isArray(exploitations) ? exploitations : []), [exploitations])
  const ents = useMemo(() => (Array.isArray(entrepots) ? entrepots : []), [entrepots])

  const [expOpen, setExpOpen] = useState(false)
  const [expPays, setExpPays] = useState('bresil')
  const [expNom, setExpNom] = useState('')
  const [entOpen, setEntOpen] = useState(false)
  const [entPays, setEntPays] = useState('bresil')
  const [entNom, setEntNom] = useState('')
  const [entAdresse, setEntAdresse] = useState('')
  const [entExploitationId, setEntExploitationId] = useState(null)
  const [saving, setSaving] = useState(false)

  const expOptionsForEnt = exps
    .filter(e => e.pays === entPays)
    .map(e => ({ value: e.id, label: e.nom }))

  async function createExploitation(e) {
    e.preventDefault()
    setSaving(true)
    try {
      await api.createGestionExploitation({ pays_slug: expPays, nom: expNom })
      toast('Exploitation créée', 'success')
      setExpOpen(false)
      setExpNom('')
      await qc.invalidateQueries({ queryKey: ['gestion-exploitations'] })
      await qc.invalidateQueries({ queryKey: ['stocks'] })
    } catch (err) {
      toast(err instanceof Error ? err.message : 'Création impossible', 'error')
    } finally {
      setSaving(false)
    }
  }

  async function deleteExploitation(exp) {
    if (!globalThis.confirm(`Supprimer « ${exp.nom} » ?`)) return
    try {
      await api.deleteGestionExploitation(exp.id)
      toast('Exploitation supprimée', 'success')
      await qc.invalidateQueries({ queryKey: ['gestion-exploitations'] })
    } catch (err) {
      toast(err instanceof Error ? err.message : 'Suppression impossible', 'error')
    }
  }

  async function createEntrepot(e) {
    e.preventDefault()
    setSaving(true)
    try {
      await api.createGestionEntrepot({
        pays_slug: entPays,
        nom: entNom,
        adresse: entAdresse || null,
        exploitation_id: entExploitationId,
      })
      toast('Entrepôt créé', 'success')
      setEntOpen(false)
      setEntNom('')
      setEntAdresse('')
      setEntExploitationId(null)
      await qc.invalidateQueries({ queryKey: ['gestion-entrepots'] })
      await qc.invalidateQueries({ queryKey: ['stocks'] })
    } catch (err) {
      toast(err instanceof Error ? err.message : 'Création impossible', 'error')
    } finally {
      setSaving(false)
    }
  }

  async function deleteEntrepot(ent) {
    if (!globalThis.confirm(`Supprimer « ${ent.nom} » ?`)) return
    try {
      await api.deleteGestionEntrepot(ent.id)
      toast('Entrepôt supprimé', 'success')
      await qc.invalidateQueries({ queryKey: ['gestion-entrepots'] })
    } catch (err) {
      toast(err instanceof Error ? err.message : 'Suppression impossible', 'error')
    }
  }

  const isLoading = tab === 'exploitations' ? loadExp : loadEnt
  const isError = tab === 'exploitations' ? errExp : errEnt

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
        <div>Impossible de charger les référentiels.</div>
      </div>
    )
  }

  return (
    <div>
      <div className="page-header users-header">
        <div>
          <h1 className="page-title">Référentiels</h1>
          <p className="page-sub">Super Admin — exploitations et entrepôts (tous pays)</p>
        </div>
        <button
          className="users-add"
          onClick={() => (tab === 'exploitations' ? setExpOpen(true) : setEntOpen(true))}
        >
          {tab === 'exploitations' ? <Building2 size={16} /> : <Warehouse size={16} />}
          {tab === 'exploitations' ? 'Nouvelle exploitation' : 'Nouvel entrepôt'}
        </button>
      </div>

      <div className="gestion-tabs">
        {TABS.map(({ id, label, Icon }) => (
          <button
            key={id}
            type="button"
            className={`gestion-tab${tab === id ? ' active' : ''}`}
            onClick={() => setTab(id)}
          >
            <Icon size={15} />
            <span>{label}</span>
          </button>
        ))}
      </div>

      {tab === 'exploitations' && (
        <div className="card users-card">
          <div className="users-table gestion-exploitations-table">
            <div className="users-row users-head">
              <div>Pays</div>
              <div>Nom</div>
              <div>Créé le</div>
              <div />
            </div>
            {exps.map(exp => (
              <div className="users-row" key={exp.id}>
                <div>{PAYS_LABELS[exp.pays] || exp.pays}</div>
                <div className="users-username">{exp.nom}</div>
                <div className="users-muted">
                  {exp.cree_le ? new Date(exp.cree_le).toLocaleString('fr-FR') : '—'}
                </div>
                <div className="users-actions">
                  <button type="button" className="users-btn" onClick={() => deleteExploitation(exp)}>
                    Supprimer
                  </button>
                </div>
              </div>
            ))}
            {exps.length === 0 && (
              <div className="empty-state" style={{ padding: '2rem 1rem' }}>
                <div>Aucune exploitation.</div>
              </div>
            )}
          </div>
        </div>
      )}

      {tab === 'entrepots' && (
        <div className="card users-card">
          <div className="users-table gestion-entrepots-table">
            <div className="users-row users-head">
              <div>Pays</div>
              <div>Nom</div>
              <div>Exploitation</div>
              <div>Adresse</div>
              <div />
            </div>
            {ents.map(ent => (
              <div className="users-row" key={ent.id}>
                <div>{PAYS_LABELS[ent.pays] || ent.pays}</div>
                <div className="users-username">{ent.nom}</div>
                <div>{ent.exploitation_nom || '—'}</div>
                <div className="users-muted">{ent.adresse || '—'}</div>
                <div className="users-actions">
                  <button type="button" className="users-btn" onClick={() => deleteEntrepot(ent)}>
                    Supprimer
                  </button>
                </div>
              </div>
            ))}
            {ents.length === 0 && (
              <div className="empty-state" style={{ padding: '2rem 1rem' }}>
                <div>Aucun entrepôt.</div>
              </div>
            )}
          </div>
        </div>
      )}

      {expOpen && (
        <div className="users-modal-backdrop" onMouseDown={() => { if (!saving) setExpOpen(false) }}>
          <div className="users-modal" role="dialog" aria-modal="true" onMouseDown={ev => ev.stopPropagation()}>
            <div className="users-modal-title">Nouvelle exploitation</div>
            <form onSubmit={createExploitation} className="users-form">
              <label className="users-label">
                <span>Pays</span>
                <Select2Like
                  className="users-select2 modal"
                  isSearchable={false}
                  isClearable={false}
                  value={PAYS_SLUG_OPTIONS.find(o => o.value === expPays)}
                  options={PAYS_SLUG_OPTIONS}
                  onChange={opt => setExpPays(opt?.value || 'bresil')}
                />
              </label>
              <label className="users-label">
                <span>Nom</span>
                <input className="users-input" value={expNom} onChange={ev => setExpNom(ev.target.value)} required />
              </label>
              <div className="users-modal-actions">
                <button type="button" className="users-btn secondary" onClick={() => setExpOpen(false)} disabled={saving}>
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

      {entOpen && (
        <div className="users-modal-backdrop" onMouseDown={() => { if (!saving) setEntOpen(false) }}>
          <div className="users-modal" role="dialog" aria-modal="true" onMouseDown={ev => ev.stopPropagation()}>
            <div className="users-modal-title">Nouvel entrepôt</div>
            <form onSubmit={createEntrepot} className="users-form">
              <label className="users-label">
                <span>Pays</span>
                <Select2Like
                  className="users-select2 modal"
                  isSearchable={false}
                  isClearable={false}
                  value={PAYS_SLUG_OPTIONS.find(o => o.value === entPays)}
                  options={PAYS_SLUG_OPTIONS}
                  onChange={opt => {
                    setEntPays(opt?.value || 'bresil')
                    setEntExploitationId(null)
                  }}
                />
              </label>
              <label className="users-label">
                <span>Nom</span>
                <input className="users-input" value={entNom} onChange={ev => setEntNom(ev.target.value)} required />
              </label>
              <label className="users-label">
                <span>Adresse</span>
                <input className="users-input" value={entAdresse} onChange={ev => setEntAdresse(ev.target.value)} />
              </label>
              <label className="users-label">
                <span>Exploitation</span>
                <Select2Like
                  className="users-select2 modal"
                  isSearchable
                  isClearable
                  value={expOptionsForEnt.find(o => o.value === entExploitationId) || null}
                  options={expOptionsForEnt}
                  onChange={opt => setEntExploitationId(opt?.value ?? null)}
                  placeholder="Optionnel"
                />
              </label>
              <div className="users-modal-actions">
                <button type="button" className="users-btn secondary" onClick={() => setEntOpen(false)} disabled={saving}>
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
