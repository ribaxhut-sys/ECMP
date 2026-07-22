import { ApiError, getErrorCopy, isApiError } from '../../../api/errors'
import type { TimelineEntry } from '../../../api/types'
import { AsyncPanel } from '../../../components/AsyncPanel'
import { useCaseTimeline } from '../hooks/useCaseTimeline'
import styles from './AuditHistoryPanel.module.css'

function formatWhen(iso: string): string {
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(iso))
  } catch {
    return iso
  }
}

function AuditEntryRow({ entry }: { entry: TimelineEntry }) {
  return (
    <li className={styles.item}>
      <div className={styles.header}>
        <code className={styles.action}>{entry.actionCode}</code>
        <span className={styles.meta}>
          {entry.actorUserId} ·{' '}
          <time dateTime={entry.occurredAt}>{formatWhen(entry.occurredAt)}</time>
        </span>
      </div>
      <pre className={styles.detail}>{JSON.stringify(entry.detail, null, 2)}</pre>
    </li>
  )
}

interface AuditHistoryPanelProps {
  caseId: string
}

/** Denser view of the same API-006 timeline payload. */
export function AuditHistoryPanel({ caseId }: AuditHistoryPanelProps) {
  const query = useCaseTimeline(caseId)
  const error = isApiError(query.error)
    ? query.error
    : query.isError
      ? new ApiError(500, 'INTERNAL_ERROR', 'Unexpected error')
      : null
  const copy = error ? getErrorCopy(error, 'load') : null

  return (
    <section className={styles.panel} aria-labelledby="audit-history-heading">
      <h2 id="audit-history-heading" className={styles.title}>
        Audit history
      </h2>
      <AsyncPanel
        isLoading={query.isLoading}
        isError={query.isError}
        errorTitle={
          error?.code === 'FORBIDDEN'
            ? "You don't have access to view audit history"
            : copy?.title
        }
        errorMessage={copy?.message}
        onRetry={() => void query.refetch()}
        isEmpty={!query.isLoading && !query.isError && (query.data?.entries.length ?? 0) === 0}
        emptyTitle="No audit entries yet."
        emptyMessage="Audit entries are written when the case changes."
      >
        <ol className={styles.list}>
          {(query.data?.entries ?? []).map((entry) => (
            <AuditEntryRow key={entry.entryId} entry={entry} />
          ))}
        </ol>
      </AsyncPanel>
    </section>
  )
}

export default AuditHistoryPanel
