import { Globe } from 'lucide-react'
import { UserPermissions } from '../../auth/permissions'

const COUNTRIES = [
  { value: '', label: 'Tous les pays' },
  { value: 'bresil', label: 'Brésil' },
  { value: 'equateur', label: 'Équateur' },
  { value: 'colombie', label: 'Colombie' },
]

export default function CountrySelector({ value, onChange }) {
  const perms = UserPermissions()
  const allowed = perms.allowedPaysSlugs()
  const countries = allowed == null ? COUNTRIES : COUNTRIES.filter(c => c.value && allowed.has(c.value))

  return (
    <div className="tabs">
      {countries.map(c => (
        <button
          key={c.value}
          className={`tab${value === c.value ? ' active' : ''}`}
          onClick={() => onChange(c.value)}
        >
          {c.value === '' && <Globe size={12} />}
          {c.label}
        </button>
      ))}
    </div>
  )
}
