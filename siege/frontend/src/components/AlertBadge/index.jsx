import { AlertTriangle, XCircle, Clock } from 'lucide-react'
import SeuilsSummary from '../SeuilsSummary'

const PAYS_LABEL = {
  bresil:   'Brésil',
  equateur: 'Équateur',
  colombie: 'Colombie',
}

const DESC = {
  perime: 'Plus de 365 jours en stockage, expédition prioritaire requise.',
  alerte: 'Conditions hors plage : température ou humidité déviante.',
}

export default function AlertBadge({ lot, onClick, seuilsBySlug }) {
  if (!lot?.statut || lot.statut === 'conforme') return null

  const statut   = lot.statut
  const isPerime = statut === 'perime'
  const Icon     = isPerime ? XCircle : AlertTriangle

  return (
    <button type="button" className={`alert-card ${statut}`} onClick={onClick}>
      <div className={`alert-icon ${statut}`}>
        <Icon size={16} />
      </div>
      <div className="alert-info">
        <div className="alert-lot-id">{lot.id}</div>
        <div className="alert-lot-title">
          {PAYS_LABEL[lot.pays] || lot.pays} · {lot.exploitation} / {lot.entrepot}
        </div>
        <div className="alert-lot-desc">{DESC[statut]}</div>
        {isPerime ? (
          <div className="alert-lot-seuils">
            <Clock size={11} aria-hidden="true" />
            <span>Seuil de péremption : 365 jours en stock</span>
          </div>
        ) : (
          <SeuilsSummary lot={lot} seuilsBySlug={seuilsBySlug} variant="compact" />
        )}
      </div>
      <span className={`badge badge-${statut}`}>
        <Icon size={10} />
        {isPerime ? 'Périmé' : 'Alerte'}
      </span>
    </button>
  )
}
