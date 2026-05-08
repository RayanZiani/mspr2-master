import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'

export function useStocks() {
  return useQuery({
    queryKey: ['stocks'],
    queryFn: api.getStocks,
    refetchInterval: 30_000,
  })
}
