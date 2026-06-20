import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'

const FALLBACK = {
  bresil: { tempIdeal: 29, tempMin: 26, tempMax: 32, humIdeal: 55, humMin: 53, humMax: 57 },
  equateur: { tempIdeal: 31, tempMin: 28, tempMax: 34, humIdeal: 60, humMin: 58, humMax: 62 },
  colombie: { tempIdeal: 26, tempMin: 23, tempMax: 29, humIdeal: 80, humMin: 78, humMax: 82 },
}

function mapSeuilsList(list) {
  const bySlug = { ...FALLBACK }
  for (const row of list || []) {
    bySlug[row.slug] = {
      tempIdeal: row.temperature.ideal,
      tempMin: row.temperature.min,
      tempMax: row.temperature.max,
      humIdeal: row.humidity.ideal,
      humMin: row.humidity.min,
      humMax: row.humidity.max,
      code: row.code,
      nom: row.nom,
    }
  }
  return bySlug
}

export function useSeuils() {
  const query = useQuery({
    queryKey: ['seuils'],
    queryFn: api.getSeuils,
    staleTime: 60_000,
  })

  return {
    ...query,
    list: Array.isArray(query.data) ? query.data : [],
    bySlug: mapSeuilsList(query.data),
  }
}

export { FALLBACK as SEUILS_FALLBACK }
