const PAYS_LABEL = {
  bresil: 'Brésil',
  equateur: 'Équateur',
  colombie: 'Colombie',
}

function originKey(lot) {
  return `${lot.pays || ''}|${lot.exploitation || '-'}|${lot.entrepot || '-'}`
}

function originLabel(lot, includePays) {
  const location = `${lot.exploitation || '-'} / ${lot.entrepot || '-'}`
  if (includePays && lot.pays) {
    return `${PAYS_LABEL[lot.pays] || lot.pays} · ${location}`
  }
  return location
}

export function groupLotsByOrigin(lots, { includePays = false } = {}) {
  const groups = new Map()

  for (const lot of lots) {
    const key = originKey(lot)
    if (!groups.has(key)) {
      groups.set(key, { key, label: originLabel(lot, includePays), lots: [] })
    }
    groups.get(key).lots.push(lot)
  }

  return [...groups.values()]
}
