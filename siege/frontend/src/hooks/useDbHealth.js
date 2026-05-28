import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'

export function useDbHealth() {
  return useQuery({
    queryKey: ['health', 'db'],
    queryFn: api.getDbHealth,
    refetchInterval: 10_000,
    retry: 0,
  })
}

