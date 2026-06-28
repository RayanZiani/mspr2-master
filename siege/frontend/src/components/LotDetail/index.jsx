import { MapPin, Warehouse, Calendar, Clock, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react'
import SeuilsSummary from '../SeuilsSummary'

const PAYS_LABEL = {
  bresil:   'Brésil',
  equateur: 'Équateur',
  colombie: 'Colombie',
}

const STATUS_MAP = {
  conforme: { cls: 'badge-conforme', label: 'Conforme', Icon: CheckCircle2 },
  alerte:   { cls: 'badge-alerte',   label: 'Alerte',   Icon: AlertTriangle },
  perime:   { cls: 'badge-perime',   label: 'Périmé',   Icon: XCircle },
}

function formatDateTime(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('fr-FR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function daysInStock(dateStr) {
  if (!dateStr) return null
  return Math.floor((Date.now() - new Date(dateStr).getTime()) / 86_400_000)
}

export default function LotDetail({ lot, seuilsBySlug, latestMesure }) {
  if (!lot) {
    return (
      <div className="card mb-2">
        <p style={{ color: 'var(--text-muted)' }}>Informations du lot indisponibles.</p>
      </div>
    )
  }

  const days   = daysInStock(lot.date_stockage)
  const status = STATUS_MAP[lot.statut] || STATUS_MAP.conforme
  const daysClass = days > 365 ? 'danger' : days > 300 ? 'warning' : ''

  return (
    <div className="card mb-2">
      <div className="lot-detail-header">
        <span className="lot-detail-id">
          Lot{' '}
          <code style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontFamily: 'Consolas, monospace' }}>
            {lot.id}
          </code>
        </span>
        <span className={`badge ${status.cls}`}>
          <status.Icon size={10} />
          {status.label}
        </span>
      </div>

      <div className="lot-detail-grid">
        <div className="lot-detail-field">
          <span className="lot-field-label"><MapPin size={10} /> Pays</span>
          <span className="lot-field-value">{PAYS_LABEL[lot.pays] || lot.pays || '-'}</span>
        </div>
        <div className="lot-detail-field">
          <span className="lot-field-label"><MapPin size={10} /> Exploitation</span>
          <span className="lot-field-value">{lot.exploitation || '-'}</span>
        </div>
        <div className="lot-detail-field">
          <span className="lot-field-label"><Warehouse size={10} /> Entrepôt</span>
          <span className="lot-field-value">{lot.entrepot || '-'}</span>
        </div>
        <div className="lot-detail-field">
          <span className="lot-field-label"><Calendar size={10} /> Date de stockage</span>
          <span className="lot-field-value">{formatDateTime(lot.date_stockage)}</span>
        </div>
        <div className="lot-detail-field">
          <span className="lot-field-label"><Clock size={10} /> Durée en stock</span>
          <span className={`lot-field-value ${daysClass}`}>
            {days == null ? '-' : `${days} jours`}
            {days > 365 && ' (périmé)'}
            {days > 300 && days <= 365 && ' (proche péremption)'}
          </span>
        </div>
      </div>

      {lot.statut === 'alerte' && (
        <SeuilsSummary
          lot={lot}
          seuilsBySlug={seuilsBySlug}
          latestMesure={latestMesure}
          variant="detailed"
        />
      )}
    </div>
  )
}
