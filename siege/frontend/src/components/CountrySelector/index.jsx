export default function CountrySelector({ onChange }) {
  return (
    <select onChange={(e) => onChange?.(e.target.value)}>
      <option value="">Tous les pays</option>
      <option value="bresil">Brésil</option>
      <option value="equateur">Équateur</option>
      <option value="colombie">Colombie</option>
    </select>
  )
}
