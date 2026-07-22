import { useEffect } from 'react'
import styles from './Toast.module.css'

export type ToastType = 'success' | 'error'

export interface ToastItem {
  id: string
  type: ToastType
  message: string
}

interface ToastProps {
  toast: ToastItem
  onDismiss: (id: string) => void
  durationMs?: number
}

export function Toast({ toast, onDismiss, durationMs = 4000 }: ToastProps) {
  useEffect(() => {
    const timer = window.setTimeout(() => onDismiss(toast.id), durationMs)
    return () => window.clearTimeout(timer)
  }, [toast.id, durationMs, onDismiss])

  return (
    <div
      className={`${styles.toast} ${toast.type === 'success' ? styles.success : styles.error}`}
      role="status"
      aria-live="polite"
    >
      <span className={styles.message}>{toast.message}</span>
      <button
        type="button"
        className={styles.dismiss}
        onClick={() => onDismiss(toast.id)}
        aria-label="Dismiss notification"
      >
        ×
      </button>
    </div>
  )
}
