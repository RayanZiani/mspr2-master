import { useMemo, useState } from 'react'
import { UserPlus } from 'lucide-react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../services/api'
import { useToast } from '../components/Toast'
import Select2Like from '../components/Select2Like'
import { roleLabel } from '../auth/permissions'
import { getSession } from '../auth/session'

function passwordNotice() {
  return "Créer / reset le mot de passe directement (hash côté serveur)."
}

function fmtDate(d) {
  if (!d) return 'Jamais'
  try {
    const dt = new Date(d)
    if (Number.isNaN(dt.getTime())) return 'Jamais'
    return dt.toLocaleString('fr-FR')
  } catch {
    return 'Jamais'
  }
}

const ROLE_OPTIONS = [
  { value: 'USER', label: 'Utilisateur' },
  { value: 'ADMIN', label: 'Administrateur' },
  { value: 'SUPER_ADMIN', label: 'Super Admin' },
]

const PAYS_OPTIONS = [
  { value: '', label: 'Aucun' },
  { value: 'SIEGE', label: 'SIEGE' },
  { value: 'BRESIL', label: 'BRESIL' },
  { value: 'EQUATEUR', label: 'EQUATEUR' },
  { value: 'COLOMBIE', label: 'COLOMBIE' },
]

export default function UsersPage() {
  const toast = useToast()
  const qc = useQueryClient()
  const { username: currentUsername } = getSession()
  const { data, isLoading, isError } = useQuery({
    queryKey: ['users'],
    queryFn: api.listUsers,
    refetchInterval: 60_000,
  })

  const users = useMemo(() => (Array.isArray(data) ? data : []), [data])

  const [createOpen, setCreateOpen] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('USER')
  const [paysCode, setPaysCode] = useState('SIEGE')
  const [email, setEmail] = useState('')
  const [saving, setSaving] = useState(false)

  async function onCreate(e) {
    e.preventDefault()
    setSaving(true)
    try {
      await api.createUser({ username, password, role, pays_code: paysCode, email: email || null })
      toast('Utilisateur créé', 'success')
      setCreateOpen(false)
      setUsername('')
      setPassword('')
      setRole('USER')
      setPaysCode('SIEGE')
      setEmail('')
      await qc.invalidateQueries({ queryKey: ['users'] })
    } catch (err) {
      const detail = err instanceof Error ? err.message : "Impossible de créer l'utilisateur"
      toast(detail, 'error')
    } finally {
      setSaving(false)
    }
  }

  async function toggleActive(u) {
    try {
      await api.updateUser(u.username, { active: !u.active })
      await qc.invalidateQueries({ queryKey: ['users'] })
    } catch {
      toast("Impossible de modifier l'utilisateur", 'error')
    }
  }

  async function changeRole(u, nextRole) {
    if (u.role === 'SUPER_ADMIN' && u.username !== currentUsername) {
      toast('Impossible de modifier un autre Super Admin', 'error')
      return
    }
    try {
      await api.updateUser(u.username, { role: nextRole })
      await qc.invalidateQueries({ queryKey: ['users'] })
    } catch {
      toast("Impossible de modifier le rôle", 'error')
    }
  }

  async function changePays(u, nextPays) {
    try {
      await api.updateUser(u.username, { pays_code: nextPays || null })
      await qc.invalidateQueries({ queryKey: ['users'] })
    } catch {
      toast("Impossible de modifier le pays", 'error')
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
        <div>Impossible de charger la liste des utilisateurs.</div>
      </div>
    )
  }

  return (
    <div>
      <div className="page-header users-header">
        <div>
          <h1 className="page-title">Gestion des utilisateurs</h1>
          <p className="page-sub">Super Admin uniquement · {passwordNotice()}</p>
        </div>
        <button className="users-add" onClick={() => setCreateOpen(true)}>
          <UserPlus size={16} />
          Nouvel utilisateur
        </button>
      </div>

      <div className="card users-card">
        <div className="users-table">
          <div className="users-row users-head">
            <div>Username</div>
            <div>Rôle</div>
            <div>Actif</div>
            <div>Pays</div>
            <div>Dernière connexion</div>
            <div />
          </div>
          {users.map(u => (
            <div className="users-row" key={u.username}>
              <div className="users-username">{u.username}</div>
              <div>
                {u.role === 'SUPER_ADMIN' && u.username !== currentUsername ? (
                  <span className="users-pill ok">{roleLabel(u.role)}</span>
                ) : (
                  <Select2Like
                    className="users-select2"
                    isSearchable
                    isClearable={false}
                    value={ROLE_OPTIONS.find(o => o.value === u.role) || ROLE_OPTIONS[0]}
                    options={ROLE_OPTIONS}
                    onChange={opt => changeRole(u, opt?.value || 'USER')}
                  />
                )}
              </div>
              <div>
                <span className={`users-pill ${u.active ? 'ok' : 'ko'}`}>
                  {u.active ? 'Oui' : 'Non'}
                </span>
              </div>
              <div>
                <Select2Like
                  className="users-select2"
                  isSearchable
                  isClearable
                  value={PAYS_OPTIONS.find(o => o.value === (u.pays_code || '')) || PAYS_OPTIONS[0]}
                  options={PAYS_OPTIONS}
                  onChange={opt => changePays(u, opt?.value || '')}
                />
              </div>
              <div className="users-muted">{fmtDate(u.last_login_at)}</div>
              <div className="users-actions">
                <button className="users-btn" onClick={() => toggleActive(u)}>
                  {u.active ? 'Désactiver' : 'Activer'}
                </button>
              </div>
            </div>
          ))}
          {users.length === 0 && (
            <div className="empty-state" style={{ padding: '2rem 1rem' }}>
              <div>Aucun utilisateur.</div>
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
          <div className="users-modal" role="dialog" aria-modal="true" onMouseDown={e => e.stopPropagation()}>
            <div className="users-modal-title">Créer un utilisateur</div>
            <form onSubmit={onCreate} className="users-form">
              <label className="users-label">
                <span>Username</span>
                <input className="users-input" value={username} onChange={e => setUsername(e.target.value)} required />
              </label>

              <label className="users-label">
                <span>Mot de passe</span>
                <input
                  type="password"
                  className="users-input"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                />
              </label>

              <label className="users-label">
                <span>Email (optionnel)</span>
                <input
                  className="users-input"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="nom@domaine.com"
                />
              </label>

              <label className="users-label">
                <span>Rôle</span>
                <Select2Like
                  className="users-select2 modal"
                  isSearchable={false}
                  isClearable={false}
                  value={ROLE_OPTIONS.find(o => o.value === role) || ROLE_OPTIONS[0]}
                  options={ROLE_OPTIONS}
                  onChange={opt => setRole(opt?.value || 'USER')}
                />
              </label>

              <label className="users-label">
                Pays associé
                <Select2Like
                  className="users-select2 modal"
                  isSearchable
                  isClearable={false}
                  value={PAYS_OPTIONS.find(o => o.value === paysCode) || PAYS_OPTIONS[1]}
                  options={PAYS_OPTIONS.filter(o => o.value !== '')}
                  onChange={opt => setPaysCode(opt?.value || 'SIEGE')}
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

