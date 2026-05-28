import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { api } from '../services/api'
import { setProfile, setSession } from '../auth/session'

export default function Login() {
  const nav = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await api.login(username, password)
      setSession({ token: res.access_token, role: res.role, username: res.username })
      setProfile({ pays_code: res.pays_code, email: res.email })
      nav('/', { replace: true })
    } catch (err) {
      setError("Identifiants invalides ou API indisponible.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-screen">
      <div className="login-stage">
        <div className="login-card">
          <div className="login-eyebrow">
            <span className="login-eyebrow-line" aria-hidden="true" />
            Accès siège
          </div>

          <h1 className="login-title">Connexion</h1>
          <p className="login-subtitle">Tableau de bord de supervision des plantations</p>

          <form onSubmit={onSubmit} className="login-form">
            <label className="login-label">
              Utilisateur
              <input
                className="login-input"
                value={username}
                onChange={e => setUsername(e.target.value)}
                autoComplete="username"
                required
              />
            </label>

            <label className="login-label">
              Mot de passe
              <input
                className="login-input"
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                autoComplete="current-password"
                required
              />
            </label>

            {error && <div className="login-error">{error}</div>}

            <button className="login-btn" disabled={loading}>
              <span>{loading ? 'Connexion…' : 'Se connecter'}</span>
              <ArrowRight size={16} />
            </button>
          </form>

          <div className="login-footer-note">Accès restreint — personnel autorisé uniquement</div>
        </div>
      </div>
    </div>
  )
}

