import { useAlerts } from '../hooks/useAlerts'
import AlertBadge from '../components/AlertBadge'

export default function AlertsPage() {
  const { data: alertes, isLoading } = useAlerts()

  if (isLoading) return <p>Chargement…</p>

  return (
    <div>
      <h1>Alertes</h1>
      {alertes?.map((a, i) => <AlertBadge key={i} alerte={a} />)}
    </div>
  )
}
