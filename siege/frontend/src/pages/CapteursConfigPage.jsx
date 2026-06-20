import { useEffect, useMemo, useState } from 'react'
import { Settings2, Send } from 'lucide-react'
import { useQueryClient } from '@tanstack/react-query'
import { api } from '../services/api'
import { useToast } from '../components/Toast'
import { useSeuils } from '../hooks/useSeuils'

const PAYS_LABEL = {
  BR: 'Bresil',
  EC: 'Equateur',
  CO: 'Colombie',
}

function emptyForm(row) {
  return {
    temperature_min: row?.temperature?.min ?? '',
    temperature_max: row?.temperature?.max ?? '',
    humidity_min: row?.humidity?.min ?? '',
    humidity_max: row?.humidity?.max ?? '',
  }
}

export default function CapteursConfigPage() {
  const toast = useToast()
  const qc = useQueryClient()
  const { list, isLoading, isError } = useSeuils()
  const [forms, setForms] = useState({})
  const [saving, setSaving] = useState(null)
  const [testingWebhook, setTestingWebhook] = useState(false)
  const [discordOk, setDiscordOk] = useState(null)

  useEffect(() => {
    api.getWebhookStatus()
      .then(r => setDiscordOk(r.discord_configured))
      .catch(() => setDiscordOk(false))
  }, [])

  useEffect(() => {
    const next = {}
    for (const row of list) {
      next[row.code] = emptyForm(row)
    }
    setForms(next)
  }, [list])

  const rows = useMemo(() => list.slice().sort((a, b) => a.code.localeCompare(b.code)), [list])

  function setField(code, field, value) {
    setForms(prev => ({
      ...prev,
      [code]: { ...prev[code], [field]: value },
    }))
  }

  async function onSave(code) {
    const f = forms[code]
    setSaving(code)
    try {
      await api.updateSeuils(code, {
        temperature_min: Number(f.temperature_min),
        temperature_max: Number(f.temperature_max),
        humidity_min: Number(f.humidity_min),
        humidity_max: Number(f.humidity_max),
      })
      toast(`Seuils ${PAYS_LABEL[code] || code} enregistres`, 'success')
      await qc.invalidateQueries({ queryKey: ['seuils'] })
      await qc.invalidateQueries({ queryKey: ['stocks'] })
      await qc.invalidateQueries({ queryKey: ['alertes'] })
    } catch {
      toast('Enregistrement impossible', 'error')
    } finally {
      setSaving(null)
    }
  }

  async function onTestWebhook() {
    setTestingWebhook(true)
    try {
      await api.testWebhook()
      toast('Webhook Discord envoye', 'success')
    } catch {
      toast('Echec envoi Discord (URL configuree ?)', 'error')
    } finally {
      setTestingWebhook(false)
    }
  }

  if (isLoading) {
    return (
      <div className="loading">
        <div className="spinner" />
        <span>Chargement configuration…</span>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="card empty-state error-state">
        <p style={{ fontWeight: 700 }}>Impossible de charger les seuils</p>
      </div>
    )
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Configuration capteurs</h1>
        <p className="page-sub">
          Seuils min / max par pays. Un releve hors plage declenche une alerte lot + notification Discord.
        </p>
      </div>

      <div className="card mb-2 config-webhook-bar">
        <div>
          <strong>Discord</strong>
          <p className="page-sub" style={{ marginTop: 4 }}>
            {discordOk === true && 'Webhook configure (DISCORD_WEBHOOK_URL)'}
            {discordOk === false && 'Webhook non configure cote API'}
            {discordOk === null && 'Verification…'}
          </p>
        </div>
        <button type="button" className="btn" onClick={onTestWebhook} disabled={testingWebhook}>
          <Send size={14} />
          {testingWebhook ? 'Envoi…' : 'Tester Discord'}
        </button>
      </div>

      <div className="config-grid">
        {rows.map(row => {
          const f = forms[row.code] || emptyForm(row)
          return (
            <div key={row.code} className="card config-card">
              <div className="config-card-head">
                <Settings2 size={16} />
                <div>
                  <div className="config-card-title">{row.nom}</div>
                  <div className="config-card-sub">{row.code} · {row.slug}</div>
                </div>
              </div>

              <div className="config-fields">
                <span className="config-section-label">Temperature (C)</span>
                <div className="config-row-2">
                  <label className="config-field">
                    <span>Min</span>
                    <input
                      type="number"
                      className="users-input"
                      step="0.1"
                      value={f.temperature_min}
                      onChange={e => setField(row.code, 'temperature_min', e.target.value)}
                    />
                  </label>
                  <label className="config-field">
                    <span>Max</span>
                    <input
                      type="number"
                      className="users-input"
                      step="0.1"
                      value={f.temperature_max}
                      onChange={e => setField(row.code, 'temperature_max', e.target.value)}
                    />
                  </label>
                </div>
                <p className="config-hint">
                  Ideal actuel : {row.temperature.ideal} C
                </p>

                <span className="config-section-label">Humidite (%)</span>
                <div className="config-row-2">
                  <label className="config-field">
                    <span>Min</span>
                    <input
                      type="number"
                      className="users-input"
                      step="0.1"
                      min="0"
                      max="100"
                      value={f.humidity_min}
                      onChange={e => setField(row.code, 'humidity_min', e.target.value)}
                    />
                  </label>
                  <label className="config-field">
                    <span>Max</span>
                    <input
                      type="number"
                      className="users-input"
                      step="0.1"
                      min="0"
                      max="100"
                      value={f.humidity_max}
                      onChange={e => setField(row.code, 'humidity_max', e.target.value)}
                    />
                  </label>
                </div>
                <p className="config-hint">
                  Ideal actuel : {row.humidity.ideal} %
                </p>
              </div>

              <button
                type="button"
                className="btn"
                onClick={() => onSave(row.code)}
                disabled={saving === row.code}
              >
                {saving === row.code ? 'Enregistrement…' : 'Enregistrer'}
              </button>
            </div>
          )
        })}
      </div>
    </div>
  )
}
