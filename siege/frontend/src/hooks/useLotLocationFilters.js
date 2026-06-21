import { useState, useMemo, useEffect } from 'react'

function uniqueSorted(values) {
  return [...new Set(values.filter(Boolean))].sort((a, b) => a.localeCompare(b, 'fr'))
}

export function useLotLocationFilters(allLots) {
  const [selectedPays, setSelectedPays] = useState('')
  const [selectedExploitation, setSelectedExploitation] = useState('')
  const [selectedEntrepot, setSelectedEntrepot] = useState('')

  const lotsByPays = useMemo(() => {
    if (!selectedPays) return allLots
    return allLots.filter((lot) => lot.pays === selectedPays)
  }, [allLots, selectedPays])

  const exploitationOptions = useMemo(
    () => uniqueSorted(lotsByPays.map((lot) => lot.exploitation)),
    [lotsByPays]
  )

  const lotsByExploitation = useMemo(() => {
    if (!selectedExploitation) return lotsByPays
    return lotsByPays.filter((lot) => lot.exploitation === selectedExploitation)
  }, [lotsByPays, selectedExploitation])

  const entrepotOptions = useMemo(
    () => uniqueSorted(lotsByExploitation.map((lot) => lot.entrepot)),
    [lotsByExploitation]
  )

  const locationFilteredLots = useMemo(() => {
    if (!selectedEntrepot) return lotsByExploitation
    return lotsByExploitation.filter((lot) => lot.entrepot === selectedEntrepot)
  }, [lotsByExploitation, selectedEntrepot])

  useEffect(() => {
    setSelectedExploitation('')
    setSelectedEntrepot('')
  }, [selectedPays])

  useEffect(() => {
    setSelectedEntrepot('')
  }, [selectedExploitation])

  useEffect(() => {
    if (selectedExploitation && !exploitationOptions.includes(selectedExploitation)) {
      setSelectedExploitation('')
    }
  }, [exploitationOptions, selectedExploitation])

  useEffect(() => {
    if (selectedEntrepot && !entrepotOptions.includes(selectedEntrepot)) {
      setSelectedEntrepot('')
    }
  }, [entrepotOptions, selectedEntrepot])

  return {
    selectedPays,
    setSelectedPays,
    selectedExploitation,
    setSelectedExploitation,
    selectedEntrepot,
    setSelectedEntrepot,
    exploitationOptions,
    entrepotOptions,
    locationFilteredLots,
    lotsByPays,
  }
}
