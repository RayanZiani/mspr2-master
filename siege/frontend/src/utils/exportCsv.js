function escapeCsv(value) {
  const str = value == null ? '' : String(value)
  if (str.includes('"') || str.includes(',') || str.includes('\n')) {
    return `"${str.replace(/"/g, '""')}"`
  }
  return str
}

function toCsv(rows) {
  if (!rows.length) return ''
  const headers = Object.keys(rows[0])
  const lines = [headers.map(escapeCsv).join(',')]

  rows.forEach((row) => {
    lines.push(headers.map((h) => escapeCsv(row[h])).join(','))
  })

  return lines.join('\n')
}

function downloadCsv(filename, content) {
  const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

export function exportLotsCsv(lots, prefix = 'stocks') {
  const rows = (lots || []).map((lot) => {
    const days = lot.date_stockage
      ? Math.floor((Date.now() - new Date(lot.date_stockage).getTime()) / 86_400_000)
      : ''

    return {
      id: lot.id || '',
      pays: lot.pays || '',
      exploitation: lot.exploitation || '',
      entrepot: lot.entrepot || '',
      statut: lot.statut || '',
      date_stockage: lot.date_stockage || '',
      jours_en_stock: days,
    }
  })

  const csv = toCsv(rows)
  const stamp = new Date().toISOString().replace(/[:.]/g, '-')
  downloadCsv(`${prefix}-${stamp}.csv`, csv)
}
