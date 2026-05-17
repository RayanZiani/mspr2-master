import { useMemo } from 'react'
import { Thermometer, Droplets, BarChart2 } from 'lucide-react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer, ReferenceLine,
} from 'recharts'

const SEUILS = {
  bresil:   { temp: 29, humidity: 55 },
  equateur: { temp: 31, humidity: 60 },
  colombie: { temp: 26, humidity: 80 },
}

function formatTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  return d.toLocaleString('fr-FR', {
    month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
  })
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background: '#fff',
      border: '1px solid var(--color-border)',
      borderRadius: 6,
      padding: '8px 12px',
      fontSize: 12,
      boxShadow: 'var(--shadow)',
    }}>
      <p style={{ color: 'var(--color-text-muted)', marginBottom: 4, fontSize: 11 }}>{label}</p>
      {payload.map(p => (
        <p key={p.name} style={{ color: p.color, fontWeight: 600 }}>
          {p.name} : {p.value?.toFixed(1)}{p.unit}
        </p>
      ))}
    </div>
  )
}

export default function Charts({ data, pays }) {
  const chartData = useMemo(() => {
    if (!data) return []
    const flat = Array.isArray(data) && data.length > 0 && data[0]?.data
      ? data.flatMap(p => p.data || [])
      : (Array.isArray(data) ? data : [])
    return flat
      .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
      .map(m => ({ ...m, time: formatTime(m.timestamp) }))
  }, [data])

  if (!chartData.length) {
    return (
      <div className="card empty-state">
        <BarChart2 size={36} className="empty-icon" />
        <p style={{ fontWeight: 500 }}>Aucune mesure disponible</p>
        <p style={{ fontSize: '0.8rem' }}>Les données apparaîtront dès que des relevés IoT seront reçus.</p>
      </div>
    )
  }

  const seuil = SEUILS[pays]

  return (
    <div>
      <div className="chart-card">
        <div className="chart-title">
          <Thermometer size={14} />
          Température (°C)
        </div>
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={chartData} margin={{ top: 4, right: 16, left: -12, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
            <XAxis
              dataKey="time"
              tick={{ fontSize: 10, fill: 'var(--color-text-muted)' }}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fontSize: 10, fill: 'var(--color-text-muted)' }}
              domain={['auto', 'auto']}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            {seuil && (
              <>
                <ReferenceLine
                  y={seuil.temp}
                  stroke="var(--color-accent)"
                  strokeDasharray="5 3"
                  label={{ value: `Seuil ${seuil.temp}°C`, fill: 'var(--color-accent)', fontSize: 10, position: 'insideTopRight' }}
                />
                <ReferenceLine y={seuil.temp + 3} stroke="var(--color-danger-mid)" strokeDasharray="2 5" strokeOpacity={0.5} />
                <ReferenceLine y={seuil.temp - 3} stroke="var(--color-danger-mid)" strokeDasharray="2 5" strokeOpacity={0.5} />
              </>
            )}
            <Line
              type="monotone"
              dataKey="temperature"
              stroke="#DC2626"
              name="Température"
              unit="°C"
              dot={false}
              strokeWidth={2}
              activeDot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-card">
        <div className="chart-title">
          <Droplets size={14} />
          Humidité (%)
        </div>
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={chartData} margin={{ top: 4, right: 16, left: -12, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
            <XAxis
              dataKey="time"
              tick={{ fontSize: 10, fill: 'var(--color-text-muted)' }}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fontSize: 10, fill: 'var(--color-text-muted)' }}
              domain={['auto', 'auto']}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            {seuil && (
              <>
                <ReferenceLine
                  y={seuil.humidity}
                  stroke="#2563EB"
                  strokeDasharray="5 3"
                  label={{ value: `Seuil ${seuil.humidity}%`, fill: '#2563EB', fontSize: 10, position: 'insideTopRight' }}
                />
                <ReferenceLine y={seuil.humidity + 2} stroke="#1D4ED8" strokeDasharray="2 5" strokeOpacity={0.5} />
                <ReferenceLine y={seuil.humidity - 2} stroke="#1D4ED8" strokeDasharray="2 5" strokeOpacity={0.5} />
              </>
            )}
            <Line
              type="monotone"
              dataKey="humidity"
              stroke="#2563EB"
              name="Humidité"
              unit="%"
              dot={false}
              strokeWidth={2}
              activeDot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
