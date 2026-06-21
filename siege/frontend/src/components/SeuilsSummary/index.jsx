import { Thermometer, Droplets } from 'lucide-react'
import {
  formatSeuilsRange,
  getSeuilForLot,
  isHumOutOfRange,
  isTempOutOfRange,
} from '../../utils/formatSeuils'

export default function SeuilsSummary({ lot, seuilsBySlug, latestMesure, variant = 'compact' }) {
  const seuil = getSeuilForLot(seuilsBySlug, lot)
  if (!seuil) return null

  const temp = latestMesure?.temperature
  const hum = latestMesure?.humidity
  const tempAlert = isTempOutOfRange(seuil, temp)
  const humAlert = isHumOutOfRange(seuil, hum)

  if (variant === 'compact') {
    return (
      <div className="seuils-summary compact">
        <Thermometer size={11} aria-hidden="true" />
        <span>Seuils : {formatSeuilsRange(seuil)}</span>
      </div>
    )
  }

  return (
    <div className="seuils-summary detailed">
      <div className="seuils-summary-title">Seuils du pays</div>
      <div className="seuils-summary-grid">
        <div className={`seuils-metric${tempAlert ? ' out-of-range' : ''}`}>
          <span className="seuils-metric-label">
            <Thermometer size={11} aria-hidden="true" />
            Température
          </span>
          <span className="seuils-metric-range">
            {seuil.tempMin}–{seuil.tempMax} °C (idéal {seuil.tempIdeal} °C)
          </span>
          {temp != null && (
            <span className={`seuils-metric-value${tempAlert ? ' danger' : ''}`}>
              Dernière mesure : {Number(temp).toFixed(1)} °C
            </span>
          )}
        </div>
        <div className={`seuils-metric${humAlert ? ' out-of-range' : ''}`}>
          <span className="seuils-metric-label">
            <Droplets size={11} aria-hidden="true" />
            Humidité
          </span>
          <span className="seuils-metric-range">
            {seuil.humMin}–{seuil.humMax} % (idéal {seuil.humIdeal} %)
          </span>
          {hum != null && (
            <span className={`seuils-metric-value${humAlert ? ' danger' : ''}`}>
              Dernière mesure : {Number(hum).toFixed(1)} %
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
