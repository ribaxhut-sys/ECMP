import { useEffect, useId, useRef } from 'react'
import styles from './ConfirmDialog.module.css'

interface ConfirmDialogProps {
  title: string
  message: string
  confirmLabel?: string
  cancelLabel?: string
  onConfirm: () => void
  onCancel: () => void
  isPending?: boolean
  open: boolean
}

export function ConfirmDialog({
  title,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  onConfirm,
  onCancel,
  isPending = false,
  open,
}: ConfirmDialogProps) {
  const titleId = useId()
  const descId = useId()
  const confirmRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    if (open) {
      confirmRef.current?.focus()
    }
  }, [open])

  useEffect(() => {
    if (!open) return
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && !isPending) {
        onCancel()
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [open, isPending, onCancel])

  if (!open) return null

  return (
    <div className={styles.backdrop} role="presentation">
      <div
        className={styles.dialog}
        role="alertdialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={descId}
      >
        <h2 id={titleId} className={styles.title}>
          {title}
        </h2>
        <p id={descId} className={styles.message}>
          {message}
        </p>
        <div className={styles.actions}>
          <button
            type="button"
            className={styles.cancel}
            onClick={onCancel}
            disabled={isPending}
          >
            {cancelLabel}
          </button>
          <button
            ref={confirmRef}
            type="button"
            className={styles.confirm}
            onClick={onConfirm}
            disabled={isPending}
            aria-busy={isPending}
          >
            {isPending ? 'Working…' : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}
