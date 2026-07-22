import styles from './LoadingSkeleton.module.css'

interface LoadingSkeletonProps {
  variant: 'header' | 'panel' | 'table'
}

export function LoadingSkeleton({ variant }: LoadingSkeletonProps) {
  if (variant === 'header') {
    return (
      <div
        className={`${styles.skeleton} ${styles.header}`}
        aria-hidden="true"
        data-testid="skeleton-header"
      >
        <div className={`${styles.bar} ${styles.barSm}`} />
        <div className={`${styles.bar} ${styles.barMd}`} />
        <div className={styles.badgeRow}>
          <div className={`${styles.bar} ${styles.badge}`} />
          <div className={`${styles.bar} ${styles.badge}`} />
        </div>
      </div>
    )
  }

  if (variant === 'table') {
    return (
      <div
        className={`${styles.skeleton} ${styles.table}`}
        aria-hidden="true"
        data-testid="skeleton-table"
      >
        <div className={styles.tableHeader}>
          <div className={`${styles.bar} ${styles.colId}`} />
          <div className={`${styles.bar} ${styles.colSubject}`} />
          <div className={`${styles.bar} ${styles.colStatus}`} />
          <div className={`${styles.bar} ${styles.colPriority}`} />
          <div className={`${styles.bar} ${styles.colType}`} />
          <div className={`${styles.bar} ${styles.colAssignee}`} />
          <div className={`${styles.bar} ${styles.colDate}`} />
        </div>
        {Array.from({ length: 6 }, (_, i) => (
          <div key={i} className={styles.tableRow}>
            <div className={`${styles.bar} ${styles.colId}`} />
            <div className={`${styles.bar} ${styles.colSubject}`} />
            <div className={`${styles.bar} ${styles.colStatus}`} />
            <div className={`${styles.bar} ${styles.colPriority}`} />
            <div className={`${styles.bar} ${styles.colType}`} />
            <div className={`${styles.bar} ${styles.colAssignee}`} />
            <div className={`${styles.bar} ${styles.colDate}`} />
          </div>
        ))}
      </div>
    )
  }

  return (
    <div
      className={`${styles.skeleton} ${styles.panel}`}
      aria-hidden="true"
      data-testid="skeleton-panel"
    >
      <div className={`${styles.bar} ${styles.barLg}`} />
      <div className={`${styles.bar} ${styles.barFull}`} />
      <div className={`${styles.bar} ${styles.barFull}`} />
      <div className={`${styles.bar} ${styles.barMd}`} />
    </div>
  )
}
