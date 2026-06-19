import { createContext, useContext, useState, useCallback } from 'react'
import { AlertCircle, CheckCircle2, Info, X } from 'lucide-react'

const ToastCtx = createContext(null)

const ICON = {
  error:   { C: AlertCircle,   cls: 'toast-icon-error' },
  success: { C: CheckCircle2,  cls: 'toast-icon-success' },
  info:    { C: Info,          cls: 'toast-icon-info' },
}

function ToastItem({ toast, onDismiss }) {
  const { C: Icon, cls } = ICON[toast.type] || ICON.info

  function handleDismiss() {
    onDismiss(toast.id)
  }

  return (
    <div className={`toast toast-${toast.type}`}>
      <Icon size={15} className={cls} />
      <span>{toast.message}</span>
      <button type="button" className="toast-close" onClick={handleDismiss}>
        <X size={13} />
      </button>
    </div>
  )
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((item) => item.id !== id))
  }, [])

  const toast = useCallback((message, type = 'info') => {
    const id = Date.now()
    setToasts((prev) => [...prev, { id, message, type }])
    setTimeout(() => removeToast(id), 5000)
  }, [removeToast])

  return (
    <ToastCtx.Provider value={toast}>
      {children}
      <div className="toast-container">
        {toasts.map((item) => (
          <ToastItem key={item.id} toast={item} onDismiss={removeToast} />
        ))}
      </div>
    </ToastCtx.Provider>
  )
}

export const useToast = () => useContext(ToastCtx)
