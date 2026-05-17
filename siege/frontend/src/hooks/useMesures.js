import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'

export function useMesures(lotId) {
  return useQuery({
    queryKey: ['mesures', lotId],
    queryFn: () => api.getMesures(lotId),
    refetchInterval: 30_000,
    enabled: !!lotId,
  })
}
