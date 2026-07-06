import { useMemo, useState } from 'react'
import { Thermometer, Droplets, BarChart2 } from 'lucide-react'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine, ReferenceArea,
} from 'recharts'

// Seuils dynamiques via API /config/seuils (prop seuilsBySlug).

const MAX_POINTS = 140

const DAY = 86_400_000
const RANGES = [
  { id: '24h', label: '24 h', ms: DAY },
  { id: '7d',  label: '7 j',  ms: 7 * DAY },
  { id: '30d', label: '30 j', ms: 30 * DAY },
  { id: 'all', label: 'Tout', ms: Infinity },
]

const SERIES = {
  temp: {
    key: 'temperature', label: 'Température', unit: '°C',
    rawColor: '#FB923C', Icon: Thermometer, iconCls: 'temp',
  },
  humidity: {
    key: 'humidity', label: 'Humidité', unit: '%',
    rawColor: '#38BDF8', Icon: Droplets, iconCls: 'humidity',
  },
}

function formatTime(ts, withYear) {
  if (!ts) return ''
  return new Date(ts).toLocaleString('fr-FR', {
    day: '2-digit', month: '2-digit',
    ...(withYear ? {} : { hour: '2-digit', minute: '2-digit' }),
  })
}

// Agrégation par buckets temporels : moyenne sur chaque tranche.
function downsample(rows, maxPoints) {
  if (rows.length <= maxPoints) return rows
  const size = Math.ceil(rows.length / maxPoints)
  const out = []
  for (let i = 0; i < rows.length; i += size) {
    const slice = rows.slice(i, i + size)
    const avg = (k) => {
      const v = slice.map((r) => r[k]).filter((x) => x != null && !Number.isNaN(x))
      return v.length ? v.reduce((a, b) => a + b, 0) / v.length : null
    }
    const mid = slice[Math.floor(slice.length / 2)]
    out.push({ ...mid, temperature: avg('temperature'), humidity: avg('humidity') })
  }
  return out
}

function statsFor(rows, key) {
  const v = rows.map((r) => r[key]).filter((x) => x != null && !Number.isNaN(x))
  if (!v.length) return null
  return { latest: v[v.length - 1], min: Math.min(...v), max: Math.max(...v) }
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip-label">{label}</div>
      {payload.map((p) => (
        <div key={p.name} className="chart-tooltip-row" style={{ color: p.stroke }}>
          <span className="chart-tooltip-dot" style={{ background: p.stroke }} />
          {p.name} : {Number(p.value).toFixed(1)}{p.unit}
        </div>
      ))}
    </div>
  )
}

function MetricChart({ cfg, rows, band, stats, animate }) {
  const gid = `grad-${cfg.key}`
  const lo = band?.min == null ? stats?.min : Math.min(stats?.min ?? band.min, band.min)
  const hi = band?.max == null ? stats?.max : Math.max(stats?.max ?? band.max, band.max)
  const pad = Math.max(1, ((hi ?? 0) - (lo ?? 0)) * 0.15)

  return (
    <div className="chart-card">
      <div className="chart-head">
        <div className="chart-title">
          <span className={`chart-title-icon ${cfg.iconCls}`}><cfg.Icon size={15} /></span>
          {cfg.label} ({cfg.unit})
        </div>
        {stats && (
          <div className="chart-stat">
            <span className="chart-stat-value">{stats.latest.toFixed(1)}</span>
            <span className="chart-stat-unit">{cfg.unit}</span>
            <span className="chart-stat-range">min {stats.min.toFixed(1)} · max {stats.max.toFixed(1)}</span>
          </div>
        )}
      </div>

      <ResponsiveContainer width="100%" height={236}>
        <AreaChart data={rows} margin={{ top: 6, right: 18, left: -8, bottom: 4 }}>
          <defs>
            <linearGradient id={gid} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={cfg.rawColor} stopOpacity={0.3} />
              <stop offset="100%" stopColor={cfg.rawColor} stopOpacity={0} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" vertical={false} />
          <XAxis
            dataKey="time"
            tick={{ fontSize: 10, fill: 'var(--text-muted)' }}
            tickLine={false}
            axisLine={{ stroke: 'var(--border)' }}
            interval="preserveStartEnd"
            minTickGap={48}
          />
          <YAxis
            tick={{ fontSize: 10, fill: 'var(--text-muted)' }}
            tickLine={false}
            axisLine={false}
            domain={[Math.floor((lo ?? 0) - pad), Math.ceil((hi ?? 0) + pad)]}
            width={42}
            allowDecimals={false}
          />

          {band && band.min != null && band.max != null && (
            <>
              <ReferenceArea
                y1={band.min}
                y2={band.max}
                fill="var(--accent)"
                fillOpacity={0.07}
                stroke="var(--accent-border)"
                strokeOpacity={0.22}
                strokeDasharray="4 4"
              />
              {band.ideal != null && (
                <ReferenceLine
                  y={band.ideal}
                  stroke="var(--accent)"
                  strokeDasharray="6 4"
                  strokeOpacity={0.65}
                  label={{
                    value: `Ideal ${band.ideal}${cfg.unit}`,
                    fill: 'var(--accent)', fontSize: 10, position: 'insideTopRight',
                  }}
                />
              )}
            </>
          )}

          <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'var(--border-strong)', strokeWidth: 1 }} />
          <Area
            type="monotone"
            dataKey={cfg.key}
            name={cfg.label}
            unit={cfg.unit}
            stroke={cfg.rawColor}
            strokeWidth={2}
            fill={`url(#${gid})`}
            dot={false}
            activeDot={{ r: 4, strokeWidth: 0 }}
            connectNulls
            isAnimationActive={animate}
            animationDuration={500}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

export default function Charts({ data, pays, seuilsBySlug }) {
  const [range, setRange] = useState('all')

  const allRows = useMemo(() => {
    if (!data) return []
    const flat = Array.isArray(data) && data.length > 0 && data[0]?.data
      ? data.flatMap((p) => p.data || [])
      : (Array.isArray(data) ? data : [])
    return flat
      .map((m) => ({
        temperature: m.temperature == null ? null : Number(m.temperature),
        humidity: m.humidity == null ? null : Number(m.humidity),
        _t: new Date(m.timestamp).getTime(),
      }))
      .filter((m) => !Number.isNaN(m._t))
      .sort((a, b) => a._t - b._t)
  }, [data])

  // Filtre par période, relatif au dernier relevé.
  const filtered = useMemo(() => {
    if (!allRows.length) return []
    const r = RANGES.find((x) => x.id === range) || RANGES[3]
    if (!Number.isFinite(r.ms)) return allRows
    const lastT = allRows[allRows.length - 1]._t
    return allRows.filter((m) => m._t >= lastT - r.ms)
  }, [allRows, range])

  const view = useMemo(() => {
    const reduced = downsample(filtered, MAX_POINTS)
    const span = filtered.length ? filtered[filtered.length - 1]._t - filtered[0]._t : 0
    const withYear = span > 3 * DAY
    return reduced.map((m) => ({ ...m, time: formatTime(m._t, withYear) }))
  }, [filtered])

  const tempStats = useMemo(() => statsFor(filtered, 'temperature'), [filtered])
  const humStats = useMemo(() => statsFor(filtered, 'humidity'), [filtered])

  if (!allRows.length) {
    return (
      <div className="card empty-state">
        <BarChart2 size={36} className="empty-icon" />
        <p style={{ fontWeight: 600 }}>Aucune mesure disponible</p>
        <p style={{ fontSize: '0.82rem' }}>
          Les données apparaîtront dès réception des premiers relevés IoT.
        </p>
      </div>
    )
  }

  const seuil = seuilsBySlug?.[pays]
  const animate = view.length <= 60
  const tempBand = seuil
    ? { min: seuil.tempMin, max: seuil.tempMax, ideal: seuil.tempIdeal }
    : null
  const humBand = seuil
    ? { min: seuil.humMin, max: seuil.humMax, ideal: seuil.humIdeal }
    : null

  return (
    <div>
      <div className="chart-toolbar">
        <span className="chart-toolbar-info">
          {filtered.length} relevé{filtered.length > 1 ? 's' : ''}
          {filtered.length !== view.length && ` · ${view.length} points affichés`}
        </span>
        <div className="range-switch" role="tablist" aria-label="Période">
          {RANGES.map((r) => (
            <button
              key={r.id}
              role="tab"
              aria-selected={range === r.id}
              className={`range-btn${range === r.id ? ' active' : ''}`}
              onClick={() => setRange(r.id)}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>

      <div className="chart-grid-2">
        <MetricChart cfg={SERIES.temp} rows={view} band={tempBand} stats={tempStats} animate={animate} />
        <MetricChart cfg={SERIES.humidity} rows={view} band={humBand} stats={humStats} animate={animate} />
      </div>
    </div>
  )
}
