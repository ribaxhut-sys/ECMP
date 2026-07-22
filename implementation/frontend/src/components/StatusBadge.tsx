import type { CaseStatus } from '../api/types'
import styles from './StatusBadge.module.css'

const LABEL: Record<CaseStatus, string> = {
  REGISTERED: 'Registered',
  ASSIGNED: 'Assigned',
  IN_PROGRESS: 'In progress',
  PENDING_REVIEW: 'Pending review',
  CLOSED: 'Closed',
  REOPENED: 'Reopened',
}

const TONE: Record<CaseStatus, string> = {
  REGISTERED: styles.registered,
  ASSIGNED: styles.assigned,
  IN_PROGRESS: styles.inProgress,
  PENDING_REVIEW: styles.pendingReview,
  CLOSED: styles.closed,
  REOPENED: styles.reopened,
}

interface StatusBadgeProps {
  status: CaseStatus
}

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span
      className={`${styles.badge} ${TONE[status]}`}
      role="status"
      aria-label={`Status: ${LABEL[status]}`}
    >
      {LABEL[status]}
    </span>
  )
}
