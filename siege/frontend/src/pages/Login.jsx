import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, Coffee, User, Lock, Eye, EyeOff, ShieldCheck } from 'lucide-react'
import { api } from '../services/api'
import { setProfile, setSession } from '../auth/session'

const COUNTRIES = ['Brésil', 'Équateur', 'Colombie']

export default function Login() {
  const nav = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
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
      setError('Identifiants invalides ou service indisponible.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-screen">
      {/* Panneau de marque */}
      <aside className="login-brand">
        <div className="login-brand-top">
          <span className="login-logo"><Coffee size={20} /></span>
          <span className="login-logo-text">FutureKawa</span>
        </div>

        <div className="login-brand-body">
          <span className="login-kicker">Supervision logistique</span>
          <h1 className="login-headline">
            Du grain de café à l'expédition, sous contrôle.
          </h1>
          <p className="login-lede">
            Suivi des stocks, traçabilité des lots et conditions de conservation
            consolidés en temps réel pour l'ensemble des exploitations.
          </p>

          <div className="login-countries">
            {COUNTRIES.map((c) => (
              <span key={c} className="login-chip">
                <span className="login-chip-dot" />
                {c}
              </span>
            ))}
          </div>
        </div>

        <div className="login-brand-foot">
          <div className="login-feature">
            <span className="login-feature-k">3</span>
            <span className="login-feature-v">Pays supervisés</span>
          </div>
          <div className="login-feature">
            <span className="login-feature-k">IoT</span>
            <span className="login-feature-v">Relevés automatisés</span>
          </div>
          <div className="login-feature">
            <span className="login-feature-k">24/7</span>
            <span className="login-feature-v">Surveillance continue</span>
          </div>
        </div>
      </aside>

      {/* Panneau formulaire */}
      <main className="login-panel">
        <div className="login-form-wrap">
          <div className="login-form-head">
            <h2 className="login-form-title">Connexion au siège</h2>
            <p className="login-form-sub">Accès réservé au personnel autorisé.</p>
          </div>

          <form onSubmit={onSubmit} className="login-form">
            <label className="login-label">
              Identifiant
              <div className="login-field">
                <User size={16} className="login-field-icon" />
                <input
                  className="login-input"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  autoComplete="username"
                  placeholder="prenom.nom"
                  required
                  autoFocus
                />
              </div>
            </label>

            <label className="login-label">
              Mot de passe
              <div className="login-field">
                <Lock size={16} className="login-field-icon" />
                <input
                  className="login-input"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                  placeholder="Votre mot de passe"
                  required
                />
                <button
                  type="button"
                  className="login-reveal"
                  onClick={() => setShowPassword((v) => !v)}
                  aria-label={showPassword ? 'Masquer le mot de passe' : 'Afficher le mot de passe'}
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </label>

            {error && (
              <div className="login-error" role="alert">
                <ShieldCheck size={15} />
                {error}
              </div>
            )}

            <button className="login-btn" disabled={loading}>
              <span>{loading ? 'Connexion en cours' : 'Se connecter'}</span>
              {!loading && <ArrowRight size={16} className="btn-arrow" />}
            </button>
          </form>

          <p className="login-foot-note">
            <ShieldCheck size={14} />
            Connexion sécurisée, sessions tracées.
          </p>
        </div>
      </main>
    </div>
  )
}
