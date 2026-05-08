import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'

export function useAlerts() {
  return useQuery({
    queryKey: ['alertes'],
    queryFn: api.getAlertes,
    refetchInterval: 15_000,
  })
}
