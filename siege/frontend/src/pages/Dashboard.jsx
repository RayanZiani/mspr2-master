import { useStocks } from '../hooks/useStocks'
import CountrySelector from '../components/CountrySelector'
import LotList from '../components/LotList'

export default function Dashboard() {
  const { data, isLoading } = useStocks()

  if (isLoading) return <p>Chargement…</p>

  return (
    <div>
      <h1>FutureKawa — Dashboard</h1>
      <CountrySelector />
      <LotList lots={data} />
    </div>
  )
}
