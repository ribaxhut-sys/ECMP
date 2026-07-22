import styles from './ErrorBanner.module.css'

interface ErrorBannerProps {
  title: string
  message: string
  action?: {
    label: string
    onClick: () => void
  }
}

export function ErrorBanner({ title, message, action }: ErrorBannerProps) {
  return (
    <div className={styles.banner} role="alert" aria-live="assertive">
      <h1 className={styles.title}>{title}</h1>
      <p className={styles.message}>{message}</p>
      {action ? (
        <button type="button" className={styles.action} onClick={action.onClick}>
          {action.label}
        </button>
      ) : null}
    </div>
  )
}
