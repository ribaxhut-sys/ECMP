import styles from './ActivityTimelinePlaceholder.module.css'

/**
 * Activity Timeline placeholder (Screen Spec Gap #2).
 * No audit-log read API exists — do not invent one.
 */
export function ActivityTimelinePlaceholder() {
  return (
    <section
      className={styles.panel}
      aria-labelledby="activity-timeline-heading"
    >
      <h2 id="activity-timeline-heading" className={styles.title}>
        Activity
      </h2>
      <p className={styles.empty}>Activity history isn&apos;t available yet</p>
    </section>
  )
}
