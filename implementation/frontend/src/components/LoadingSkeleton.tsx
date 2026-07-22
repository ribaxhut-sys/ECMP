import styles from './LoadingSkeleton.module.css'

interface LoadingSkeletonProps {
  variant: 'header' | 'panel'
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
