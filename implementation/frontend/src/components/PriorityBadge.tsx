import type { Priority } from '../api/types'
import styles from './PriorityBadge.module.css'

const LABEL: Record<Priority, string> = {
  LOW: 'Low',
  MEDIUM: 'Medium',
  HIGH: 'High',
  CRITICAL: 'Critical',
}

const TONE: Record<Priority, string> = {
  LOW: styles.low,
  MEDIUM: styles.medium,
  HIGH: styles.high,
  CRITICAL: styles.critical,
}

interface PriorityBadgeProps {
  priority: Priority
}

export function PriorityBadge({ priority }: PriorityBadgeProps) {
  return (
    <span
      className={`${styles.badge} ${TONE[priority]}`}
      aria-label={`Priority: ${LABEL[priority]}`}
    >
      {LABEL[priority]}
    </span>
  )
}
