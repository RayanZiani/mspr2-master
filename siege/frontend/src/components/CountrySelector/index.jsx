import { Globe } from 'lucide-react'

const COUNTRIES = [
  { value: '', label: 'Tous les pays' },
  { value: 'bresil', label: 'Brésil' },
  { value: 'equateur', label: 'Équateur' },
  { value: 'colombie', label: 'Colombie' },
]

export default function CountrySelector({ value, onChange }) {
  return (
    <div className="tabs">
      {COUNTRIES.map(c => (
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
