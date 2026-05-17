import { useCallback } from 'react'
import { AgGridReact } from 'ag-grid-react'
import { CheckCircle2, AlertTriangle, XCircle } from 'lucide-react'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-alpine.css'

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

function StatusRenderer({ value }) {
  const s = STATUS_MAP[value] || STATUS_MAP.conforme
  return (
    <span className={`badge ${s.cls}`}>
      <s.Icon size={10} />
      {s.label}
    </span>
  )
}

function IdRenderer({ value }) {
  if (!value) return null
  return (
    <code style={{ fontSize: 11, color: 'var(--color-text-muted)', letterSpacing: '0.3px' }}>
      {value.slice(0, 8)}…
    </code>
  )
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('fr-FR')
}

const columnDefs = [
  {
    field: 'id',
    headerName: 'ID Lot',
    width: 110,
    cellRenderer: IdRenderer,
    tooltipField: 'id',
  },
  {
    field: 'pays',
    headerName: 'Pays',
    width: 120,
    valueFormatter: ({ value }) => PAYS_LABEL[value] || value,
  },
  { field: 'exploitation', headerName: 'Exploitation', flex: 1, minWidth: 120 },
  { field: 'entrepot',     headerName: 'Entrepôt',     flex: 1, minWidth: 100 },
  {
    field: 'date_stockage',
    headerName: 'Date stockage',
    width: 125,
    valueFormatter: ({ value }) => formatDate(value),
    sort: 'asc',
  },
  {
    headerName: 'En stock',
    width: 88,
    valueGetter: ({ data }) => {
      if (!data?.date_stockage) return null
      return Math.floor((Date.now() - new Date(data.date_stockage).getTime()) / 86_400_000)
    },
    valueFormatter: ({ value }) => value != null ? `${value} j` : '-',
  },
  {
    field: 'statut',
    headerName: 'Statut',
    width: 118,
    cellRenderer: StatusRenderer,
  },
]

const defaultColDef = {
  sortable: true,
  resizable: true,
  suppressMovable: false,
}

export default function LotList({ lots, onSelect }) {
  const onRowClicked = useCallback(({ data }) => {
    if (data) onSelect?.(data)
  }, [onSelect])

  return (
    <div className="ag-theme-alpine" style={{ height: 500, width: '100%' }}>
      <AgGridReact
        rowData={lots ?? []}
        columnDefs={columnDefs}
        defaultColDef={defaultColDef}
        onRowClicked={onRowClicked}
        rowStyle={{ cursor: 'pointer' }}
        pagination
        paginationPageSize={20}
        tooltipShowDelay={300}
        animateRows
        suppressCellFocus
      />
    </div>
  )
}
