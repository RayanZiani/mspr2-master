export function getSeuilForLot(seuilsBySlug, lot) {
  if (!lot?.pays || !seuilsBySlug) return null
  return seuilsBySlug[lot.pays] || null
}

export function formatSeuilsRange(seuil) {
  if (!seuil) return null
  return `${seuil.tempMin}–${seuil.tempMax} °C · ${seuil.humMin}–${seuil.humMax} %`
}

export function isTempOutOfRange(seuil, temperature) {
  if (!seuil || temperature == null || Number.isNaN(Number(temperature))) return false
  const t = Number(temperature)
  return t < seuil.tempMin || t > seuil.tempMax
}

export function isHumOutOfRange(seuil, humidity) {
  if (!seuil || humidity == null || Number.isNaN(Number(humidity))) return false
  const h = Number(humidity)
  return h < seuil.humMin || h > seuil.humMax
}
