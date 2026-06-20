import { useEffect, useMemo, useState } from 'react'
import { Settings2, Send } from 'lucide-react'
import { useQueryClient } from '@tanstack/react-query'
import { api } from '../services/api'
import { useToast } from '../components/Toast'
import { useSeuils } from '../hooks/useSeuils'
import { UserPermissions } from '../auth/permissions'

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

function formFor(row, forms) {
  const base = emptyForm(row)
  const saved = forms[row.code]
  if (!saved) return base
  return {
    temperature_min: saved.temperature_min !== '' ? saved.temperature_min : base.temperature_min,
    temperature_max: saved.temperature_max !== '' ? saved.temperature_max : base.temperature_max,
    humidity_min: saved.humidity_min !== '' ? saved.humidity_min : base.humidity_min,
    humidity_max: saved.humidity_max !== '' ? saved.humidity_max : base.humidity_max,
  }
}

export default function CapteursConfigPage() {
  const toast = useToast()
  const qc = useQueryClient()
  const perms = UserPermissions()
  const { list, isLoading, isError } = useSeuils()
  const [forms, setForms] = useState({})
  const [saving, setSaving] = useState(null)
  const [testingWebhook, setTestingWebhook] = useState(false)
  const [discordOk, setDiscordOk] = useState(null)

  useEffect(() => {
    if (!perms.canManageGlobalWebhook()) return
    api.getWebhookStatus()
      .then(r => setDiscordOk(r.discord_configured))
      .catch(() => setDiscordOk(false))
  }, [perms])

  useEffect(() => {
    const next = {}
    for (const row of list) {
      next[row.code] = emptyForm(row)
    }
    setForms(next)
  }, [list])

  const rows = useMemo(() => {
    const sorted = list.slice().sort((a, b) => a.code.localeCompare(b.code))
    return sorted.filter(row => perms.canConfigThresholdsFor(row.code))
  }, [list, perms])

  function setField(code, field, value) {
    setForms(prev => ({
      ...prev,
      [code]: { ...prev[code], [field]: value },
    }))
  }

  async function onSave(code) {
    const f = formFor(rows.find(r => r.code === code) || {}, forms)
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
      setDiscordOk(true)
      toast('Message de validation envoye sur Discord', 'success')
    } catch {
      setDiscordOk(false)
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

      {perms.canManageGlobalWebhook() && (
      <div className="card mb-2 config-webhook-bar">
        <div className="config-webhook-info">
          <strong>Discord — validation webhook</strong>
          <p className="config-webhook-status">
            {discordOk === true && 'Webhook configure (DISCORD_WEBHOOK_URL) — reserve au super administrateur'}
            {discordOk === false && 'Webhook non configure cote API — ajoutez DISCORD_WEBHOOK_URL sur Render'}
            {discordOk === null && 'Verification…'}
          </p>
        </div>
        <button type="button" className="btn config-webhook-btn" onClick={onTestWebhook} disabled={testingWebhook || discordOk === false}>
          <Send size={14} />
          {testingWebhook ? 'Envoi…' : 'Valider sur Discord'}
        </button>
      </div>
      )}

      {rows.length === 0 && (
        <div className="card empty-state">
          <p>Aucun pays configurable pour votre compte.</p>
        </div>
      )}

      <div className={`config-grid${rows.length === 1 ? ' config-grid-single' : ''}`}>
        {rows.map(row => {
          const f = formFor(row, forms)
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
                <div className="config-section">
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
                </div>

                <div className="config-section">
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
              </div>

              <button
                type="button"
                className="btn config-save-btn"
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
