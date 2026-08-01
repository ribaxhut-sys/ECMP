import type { QueueEntry } from '../../../api/types'
import type { CaseStatus } from '../../../api/types'
import styles from './DashboardQueuesPanel.module.css'

const STATUS_LABEL: Record<CaseStatus, string> = {
  REGISTERED: 'Registered',
  ASSIGNED: 'Assigned',
  IN_PROGRESS: 'In progress',
  PENDING_REVIEW: 'Pending review',
  CLOSED: 'Closed',
  REOPENED: 'Reopened',
}

export interface DashboardQueuesPanelProps {
  asOf: string
  queues: QueueEntry[]
  onSelectStatus: (status: CaseStatus) => void
}

function formatAsOf(value: string): string {
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(value))
  } catch {
    return value
  }
}

/**
 * CAP-007 / API-040 aggregate dashboard (read-only).
 * Drill-down navigates to the existing Case list filter (API-005) — DEC-CAP007-BQ-001 §3.
 */
export function DashboardQueuesPanel({
  asOf,
  queues,
  onSelectStatus,
}: DashboardQueuesPanelProps) {
  if (queues.length === 0) {
    return (
      <section className={styles.panel} aria-label="Operational queue dashboard">
        <header className={styles.header}>
          <h2 className={styles.title}>Operational queues</h2>
          <p className={styles.asOf}>As of {formatAsOf(asOf)}</p>
        </header>
        <p className={styles.empty}>
          No unit-scoped cases in queue yet. Assign a case to your unit to see
          aggregates.
        </p>
      </section>
    )
  }

  return (
    <section className={styles.panel} aria-label="Operational queue dashboard">
      <header className={styles.header}>
        <h2 className={styles.title}>Operational queues</h2>
        <p className={styles.asOf}>As of {formatAsOf(asOf)}</p>
      </header>
      <ul className={styles.grid}>
        {queues.map((entry) => (
          <li key={`${entry.unitId}-${entry.status}`}>
            <button
              type="button"
              className={styles.card}
              onClick={() => onSelectStatus(entry.status)}
            >
              <span className={styles.status}>
                {STATUS_LABEL[entry.status] ?? entry.status}
              </span>
              <span className={styles.count}>{entry.count}</span>
              <span className={styles.meta}>Unit {entry.unitId}</span>
            </button>
          </li>
        ))}
      </ul>
    </section>
  )
}
