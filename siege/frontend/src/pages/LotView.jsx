import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'
import Charts from '../components/Charts'
import LotDetail from '../components/LotDetail'

export default function LotView() {
  const { lotId } = useParams()
  const { data: mesures } = useQuery({
    queryKey: ['mesures', lotId],
    queryFn: () => api.getMesures(lotId),
    refetchInterval: 30_000,
  })

  return (
    <div>
      <LotDetail lotId={lotId} />
      <Charts data={mesures} />
    </div>
  )
}
