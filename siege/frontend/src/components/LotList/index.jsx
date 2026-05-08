import { AgGridReact } from 'ag-grid-react'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-alpine.css'

const columns = [
  { field: 'id', headerName: 'ID' },
  { field: 'pays', headerName: 'Pays' },
  { field: 'exploitation', headerName: 'Exploitation' },
  { field: 'entrepot', headerName: 'Entrepôt' },
  { field: 'date_stockage', headerName: 'Date stockage' },
  { field: 'statut', headerName: 'Statut' },
]

export default function LotList({ lots }) {
  return (
    <div className="ag-theme-alpine" style={{ height: 400 }}>
      <AgGridReact rowData={lots ?? []} columnDefs={columns} />
    </div>
  )
}
