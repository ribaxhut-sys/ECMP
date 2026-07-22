import { useEffect, useState } from 'react'
import type { CaseStatus, CaseType, Priority } from '../../../api/types'
import type { CaseQueueFilters } from '../filters'
import {
  QUEUE_CASE_TYPE_OPTIONS,
  QUEUE_PRIORITY_OPTIONS,
  QUEUE_STATUS_OPTIONS,
} from '../filters'
import styles from './QueueFilterBar.module.css'

interface QueueFilterBarProps {
  filters: CaseQueueFilters
  isFetching: boolean
  onChange: (patch: Partial<CaseQueueFilters>) => void
  onClear: () => void
}

const STATUS_LABEL: Record<CaseStatus, string> = {
  REGISTERED: 'Registered',
  ASSIGNED: 'Assigned',
  IN_PROGRESS: 'In progress',
  PENDING_REVIEW: 'Pending review',
  CLOSED: 'Closed',
  REOPENED: 'Reopened',
}

const PRIORITY_LABEL: Record<Priority, string> = {
  LOW: 'Low',
  MEDIUM: 'Medium',
  HIGH: 'High',
  CRITICAL: 'Critical',
}

const TYPE_LABEL: Record<CaseType, string> = {
  COMPLAINT: 'Complaint',
  INQUIRY: 'Inquiry',
}

export function QueueFilterBar({
  filters,
  isFetching,
  onChange,
  onClear,
}: QueueFilterBarProps) {
  const [assigneeDraft, setAssigneeDraft] = useState(filters.assigneeId ?? '')

  useEffect(() => {
    setAssigneeDraft(filters.assigneeId ?? '')
  }, [filters.assigneeId])

  useEffect(() => {
    const trimmed = assigneeDraft.trim()
    const current = filters.assigneeId ?? ''
    if (trimmed === current) return
    const handle = window.setTimeout(() => {
      onChange({ assigneeId: trimmed || undefined })
    }, 300)
    return () => window.clearTimeout(handle)
  }, [assigneeDraft, filters.assigneeId, onChange])

  const hasFilters = Boolean(
    filters.status || filters.priority || filters.caseType || filters.assigneeId,
  )

  return (
    <div className={styles.bar} role="search" aria-label="Case queue filters">
      <label className={styles.field}>
        <span className={styles.label}>Status</span>
        <select
          value={filters.status ?? ''}
          onChange={(e) =>
            onChange({
              status: (e.target.value || undefined) as CaseStatus | undefined,
            })
          }
          aria-label="Filter by status"
        >
          <option value="">All</option>
          {QUEUE_STATUS_OPTIONS.map((s) => (
            <option key={s} value={s}>
              {STATUS_LABEL[s]}
            </option>
          ))}
        </select>
      </label>

      <label className={styles.field}>
        <span className={styles.label}>Priority</span>
        <select
          value={filters.priority ?? ''}
          onChange={(e) =>
            onChange({
              priority: (e.target.value || undefined) as Priority | undefined,
            })
          }
          aria-label="Filter by priority"
        >
          <option value="">All</option>
          {QUEUE_PRIORITY_OPTIONS.map((p) => (
            <option key={p} value={p}>
              {PRIORITY_LABEL[p]}
            </option>
          ))}
        </select>
      </label>

      <label className={styles.field}>
        <span className={styles.label}>Case type</span>
        <select
          value={filters.caseType ?? ''}
          onChange={(e) =>
            onChange({
              caseType: (e.target.value || undefined) as CaseType | undefined,
            })
          }
          aria-label="Filter by case type"
        >
          <option value="">All</option>
          {QUEUE_CASE_TYPE_OPTIONS.map((t) => (
            <option key={t} value={t}>
              {TYPE_LABEL[t]}
            </option>
          ))}
        </select>
      </label>

      <label className={styles.field}>
        <span className={styles.label}>Assignee ID</span>
        <input
          type="text"
          value={assigneeDraft}
          placeholder="e.g. USR-2001"
          onChange={(e) => setAssigneeDraft(e.target.value)}
          aria-label="Filter by assignee ID"
        />
      </label>

      <div className={styles.actions}>
        <button
          type="button"
          className={styles.clear}
          onClick={onClear}
          disabled={!hasFilters}
        >
          Clear filters
        </button>
        {isFetching ? (
          <span className={styles.spinner} aria-live="polite" aria-label="Updating">
            Updating…
          </span>
        ) : null}
      </div>
    </div>
  )
}
