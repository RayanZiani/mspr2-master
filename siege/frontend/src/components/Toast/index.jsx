import { createContext, useContext, useState, useCallback } from 'react'
import { AlertCircle, CheckCircle2, Info, X } from 'lucide-react'

const ToastCtx = createContext(null)

const ICON = {
  error:   { C: AlertCircle,   cls: 'toast-icon-error' },
  success: { C: CheckCircle2,  cls: 'toast-icon-success' },
  info:    { C: Info,          cls: 'toast-icon-info' },
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const toast = useCallback((message, type = 'info') => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 5000)
  }, [])

  const dismiss = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  return (
    <ToastCtx.Provider value={toast}>
      {children}
      <div className="toast-container">
        {toasts.map(t => {
          const { C: Icon, cls } = ICON[t.type] || ICON.info
          return (
            <div key={t.id} className={`toast toast-${t.type}`}>
              <Icon size={15} className={cls} />
              <span>{t.message}</span>
              <button className="toast-close" onClick={() => dismiss(t.id)}>
                <X size={13} />
              </button>
            </div>
          )
        })}
      </div>
    </ToastCtx.Provider>
  )
}

export const useToast = () => useContext(ToastCtx)
