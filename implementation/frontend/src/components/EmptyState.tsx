import styles from './EmptyState.module.css'

interface EmptyStateProps {
  title: string
  message: string
  action?: {
    label: string
    onClick: () => void
  }
}

/** Shared full-panel empty state (Sprint-05 Case Queue). */
export function EmptyState({ title, message, action }: EmptyStateProps) {
  return (
    <div className={styles.root} role="status" data-testid="empty-state">
      <h2 className={styles.title}>{title}</h2>
      <p className={styles.message}>{message}</p>
      {action ? (
        <button type="button" className={styles.action} onClick={action.onClick}>
          {action.label}
        </button>
      ) : null}
    </div>
  )
}
