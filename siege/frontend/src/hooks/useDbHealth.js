import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'

export function useDbHealth() {
  return useQuery({
    queryKey: ['health', 'db'],
    // Stabilise l'UI: on sonde 1x/min et on ne "flip" pas en erreur transitoire.
    queryFn: async () => {
      try {
        return await api.getDbHealth()
      } catch {
        return { ok: false }
      }
    },
    refetchInterval: 60_000,
    retry: 0,
    refetchOnWindowFocus: false,
  })
}

