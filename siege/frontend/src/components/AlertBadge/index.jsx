import { AlertTriangle, XCircle } from 'lucide-react'

const PAYS_LABEL = {
  bresil:   'Brésil',
  equateur: 'Équateur',
  colombie: 'Colombie',
}

const DESC = {
  perime: 'Plus de 365 jours en stockage — expédition prioritaire requise.',
  alerte: 'Conditions hors plage — température ou humidité déviante.',
}

export default function AlertBadge({ lot, onClick }) {
  if (!lot?.statut || lot.statut === 'conforme') return null

  const statut   = lot.statut
  const isPerime = statut === 'perime'
  const Icon     = isPerime ? XCircle : AlertTriangle

  return (
    <div className={`alert-card ${statut}`} onClick={onClick}>
      <div className={`alert-icon ${statut}`}>
        <Icon size={16} />
      </div>
      <div className="alert-info">
        <div className="alert-lot-id">{lot.id}</div>
        <div className="alert-lot-title">
          {PAYS_LABEL[lot.pays] || lot.pays} — {lot.exploitation} / {lot.entrepot}
        </div>
        <div className="alert-lot-desc">{DESC[statut]}</div>
      </div>
      <span className={`badge badge-${statut}`}>
        <Icon size={10} />
        {isPerime ? 'Périmé' : 'Alerte'}
      </span>
    </div>
  )
}
