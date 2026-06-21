import { Building2, Warehouse } from 'lucide-react'
import CountrySelector from '../CountrySelector'

export default function LocationFilters({
  selectedPays,
  onPaysChange,
  selectedExploitation,
  onExploitationChange,
  selectedEntrepot,
  onEntrepotChange,
  exploitationOptions = [],
  entrepotOptions = [],
}) {
  return (
    <div className="location-filters mb-2">
      <CountrySelector value={selectedPays} onChange={onPaysChange} />
      <div className="toolbar location-filters-row">
        <label className="filter-item" htmlFor="exploitation-filter">
          <Building2 size={14} aria-hidden="true" />
          Exploitation
        </label>
        <select
          id="exploitation-filter"
          className="input location-filter-select"
          value={selectedExploitation}
          onChange={(e) => onExploitationChange(e.target.value)}
          disabled={exploitationOptions.length === 0}
        >
          <option value="">Toutes les exploitations</option>
          {exploitationOptions.map((name) => (
            <option key={name} value={name}>{name}</option>
          ))}
        </select>

        <label className="filter-item" htmlFor="entrepot-filter">
          <Warehouse size={14} aria-hidden="true" />
          Entrepôt
        </label>
        <select
          id="entrepot-filter"
          className="input location-filter-select"
          value={selectedEntrepot}
          onChange={(e) => onEntrepotChange(e.target.value)}
          disabled={entrepotOptions.length === 0}
        >
          <option value="">Tous les entrepôts</option>
          {entrepotOptions.map((name) => (
            <option key={name} value={name}>{name}</option>
          ))}
        </select>
      </div>
    </div>
  )
}
