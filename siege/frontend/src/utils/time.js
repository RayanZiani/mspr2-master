export function formatTimeAgo(timestampMs, nowMs = Date.now()) {
  const deltaSec = Math.max(0, Math.floor((nowMs - timestampMs) / 1000))
  if (deltaSec < 60) return `${deltaSec}s`

  const deltaMin = Math.floor(deltaSec / 60)
  if (deltaMin < 60) return `${deltaMin} min`

  const deltaHour = Math.floor(deltaMin / 60)
  if (deltaHour < 24) return `${deltaHour} h`

  const deltaDay = Math.floor(deltaHour / 24)
  return `${deltaDay} j`
}
