import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'

export default function Charts({ data }) {
  if (!data?.length) return <p>Aucune mesure disponible.</p>

  return (
    <div>
      <h3>Température & Humidité</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="timestamp" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="temperature" stroke="#e74c3c" name="Temp (°C)" />
          <Line type="monotone" dataKey="humidity" stroke="#3498db" name="Humidité (%)" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
