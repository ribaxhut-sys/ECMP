import { useNavigate } from 'react-router-dom'
import type { Case } from '../../../api/types'
import { PriorityBadge } from '../../../components/PriorityBadge'
import { StatusBadge } from '../../../components/StatusBadge'
import styles from './CaseQueueTable.module.css'

interface CaseQueueTableProps {
  items: Case[]
  dimmed?: boolean
}

function formatDate(iso: string): string {
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(iso))
  } catch {
    return iso
  }
}

export function CaseQueueTable({ items, dimmed = false }: CaseQueueTableProps) {
  const navigate = useNavigate()

  return (
    <div
      className={`${styles.wrap} ${dimmed ? styles.dimmed : ''}`}
      aria-busy={dimmed || undefined}
    >
      <table className={styles.table}>
        <thead>
          <tr>
            <th scope="col">Case ID</th>
            <th scope="col">Subject</th>
            <th scope="col">Status</th>
            <th scope="col">Priority</th>
            <th scope="col">Type</th>
            <th scope="col">Assignee</th>
            <th scope="col">Created</th>
          </tr>
        </thead>
        <tbody>
          {items.map((c) => (
            <tr
              key={c.caseId}
              className={styles.row}
              tabIndex={0}
              onClick={() => navigate(`/cases/${encodeURIComponent(c.caseId)}`)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  navigate(`/cases/${encodeURIComponent(c.caseId)}`)
                }
              }}
              aria-label={`Open case ${c.caseId}`}
            >
              <td className={styles.mono}>{c.caseId}</td>
              <td className={styles.subject}>{c.subject}</td>
              <td>
                <StatusBadge status={c.status} />
              </td>
              <td>
                <PriorityBadge priority={c.priority} />
              </td>
              <td>{c.caseType === 'COMPLAINT' ? 'Complaint' : 'Inquiry'}</td>
              <td className={styles.mono}>{c.assigneeId ?? '—'}</td>
              <td>{formatDate(c.createdAt)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
