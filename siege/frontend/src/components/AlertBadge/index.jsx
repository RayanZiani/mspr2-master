const colors = {
  conforme: '#2ecc71',
  alerte: '#e67e22',
  perime: '#e74c3c',
}

export default function AlertBadge({ alerte }) {
  const statut = alerte?.statut ?? 'conforme'
  return (
    <span style={{ background: colors[statut], color: '#fff', padding: '2px 8px', borderRadius: 4 }}>
      {statut}
    </span>
  )
}
