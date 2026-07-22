import styles from './InlineFieldError.module.css'

interface InlineFieldErrorProps {
  message: string
  id?: string
}

export function InlineFieldError({ message, id }: InlineFieldErrorProps) {
  if (!message) return null
  return (
    <p id={id} className={styles.error} role="alert">
      {message}
    </p>
  )
}
