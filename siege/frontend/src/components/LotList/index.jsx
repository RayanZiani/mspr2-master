import { useMemo, useState } from 'react'
import {
  CheckCircle2, AlertTriangle, XCircle, ChevronUp, ChevronDown,
  ChevronLeft, ChevronRight, Inbox,
} from 'lucide-react'

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

const STATUS_ORDER = { perime: 0, alerte: 1, conforme: 2 }
const PAGE_SIZE = 12

function daysInStock(dateStr) {
  if (!dateStr) return null
  return Math.floor((Date.now() - new Date(dateStr).getTime()) / 86_400_000)
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('fr-FR')
}

const COLUMNS = [
  { key: 'id',           label: 'ID Lot',        sortable: true,  align: 'left' },
  { key: 'pays',         label: 'Pays',          sortable: true,  align: 'left' },
  { key: 'exploitation', label: 'Exploitation',  sortable: true,  align: 'left' },
  { key: 'entrepot',     label: 'Entrepôt',      sortable: true,  align: 'left' },
  { key: 'date_stockage', label: 'Date stockage', sortable: true, align: 'left' },
  { key: 'days',         label: 'En stock',      sortable: true,  align: 'right' },
  { key: 'statut',       label: 'Statut',        sortable: true,  align: 'left' },
]

export default function LotList({ lots, onSelect }) {
  const [sortKey, setSortKey] = useState('date_stockage')
  const [sortDir, setSortDir] = useState('asc') // FIFO par défaut : plus ancien en premier
  const [page, setPage] = useState(0)

  const sorted = useMemo(() => {
    const rows = [...(lots ?? [])]
    const dir = sortDir === 'asc' ? 1 : -1
    rows.sort((a, b) => {
      let va, vb
      switch (sortKey) {
        case 'days':
        case 'date_stockage':
          va = a.date_stockage ? new Date(a.date_stockage).getTime() : 0
          vb = b.date_stockage ? new Date(b.date_stockage).getTime() : 0
          break
        case 'statut':
          va = STATUS_ORDER[a.statut] ?? 9
          vb = STATUS_ORDER[b.statut] ?? 9
          break
        default:
          va = String(a[sortKey] ?? '').toLowerCase()
          vb = String(b[sortKey] ?? '').toLowerCase()
      }
      if (va < vb) return -1 * dir
      if (va > vb) return 1 * dir
      return 0
    })
    return rows
  }, [lots, sortKey, sortDir])

  const pageCount = Math.max(1, Math.ceil(sorted.length / PAGE_SIZE))
  const safePage = Math.min(page, pageCount - 1)
  const pageRows = sorted.slice(safePage * PAGE_SIZE, safePage * PAGE_SIZE + PAGE_SIZE)

  function toggleSort(key) {
    if (key === sortKey) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortKey(key)
      setSortDir(key === 'date_stockage' ? 'asc' : 'asc')
    }
    setPage(0)
  }

  if (!sorted.length) {
    return (
      <div className="empty-state" style={{ borderRadius: 'var(--radius)' }}>
        <Inbox size={34} className="empty-icon" />
        <p style={{ fontWeight: 600 }}>Aucun lot à afficher</p>
        <p style={{ fontSize: '0.82rem' }}>Ajustez les filtres ou la recherche.</p>
      </div>
    )
  }

  return (
    <div className="data-table-wrap">
      <div className="data-table-scroll">
        <table className="data-table">
          <thead>
            <tr>
              {COLUMNS.map((c) => {
                const active = c.key === sortKey
                return (
                  <th
                    key={c.key}
                    className={`${c.align === 'right' ? 'ta-right' : ''}${c.sortable ? ' sortable' : ''}${active ? ' active' : ''}`}
                    onClick={c.sortable ? () => toggleSort(c.key) : undefined}
                  >
                    <span className="th-inner">
                      {c.label}
                      {c.sortable && (
                        <span className="th-sort">
                          {active ? (
                            sortDir === 'asc' ? <ChevronUp size={13} /> : <ChevronDown size={13} />
                          ) : (
                            <ChevronDown size={13} style={{ opacity: 0.25 }} />
                          )}
                        </span>
                      )}
                    </span>
                  </th>
                )
              })}
            </tr>
          </thead>
          <tbody>
            {pageRows.map((lot) => {
              const s = STATUS_MAP[lot.statut] || STATUS_MAP.conforme
              const days = daysInStock(lot.date_stockage)
              return (
                <tr key={lot.id} onClick={() => onSelect?.(lot)}>
                  <td><code className="cell-id">{lot.id ? `${String(lot.id).slice(0, 8)}…` : '-'}</code></td>
                  <td>{PAYS_LABEL[lot.pays] || lot.pays || '-'}</td>
                  <td>{lot.exploitation || '-'}</td>
                  <td>{lot.entrepot || '-'}</td>
                  <td className="cell-num">{formatDate(lot.date_stockage)}</td>
                  <td className="ta-right cell-num">{days != null ? `${days} j` : '-'}</td>
                  <td>
                    <span className={`badge ${s.cls}`}>
                      <s.Icon size={10} />
                      {s.label}
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      <div className="data-table-foot">
        <span className="data-table-count">
          {sorted.length} lot{sorted.length > 1 ? 's' : ''}
        </span>
        <div className="data-table-pager">
          <button
            className="pager-btn"
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={safePage === 0}
            aria-label="Page précédente"
          >
            <ChevronLeft size={15} />
          </button>
          <span className="pager-info">{safePage + 1} / {pageCount}</span>
          <button
            className="pager-btn"
            onClick={() => setPage((p) => Math.min(pageCount - 1, p + 1))}
            disabled={safePage >= pageCount - 1}
            aria-label="Page suivante"
          >
            <ChevronRight size={15} />
          </button>
        </div>
      </div>
    </div>
  )
}
