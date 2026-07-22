import { ApiError, getErrorCopy, isApiError } from '../../../api/errors'
import type { TimelineEntry } from '../../../api/types'
import { AsyncPanel } from '../../../components/AsyncPanel'
import { useCaseTimeline } from '../hooks/useCaseTimeline'
import styles from './CaseActivityTimeline.module.css'

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

function TimelineEntryRow({ entry }: { entry: TimelineEntry }) {
  return (
    <li className={styles.item}>
      <div className={styles.summary}>{entry.summary}</div>
      <div className={styles.meta}>
        <span>{entry.actorUserId}</span>
        <span aria-hidden="true">·</span>
        <time dateTime={entry.occurredAt}>{formatWhen(entry.occurredAt)}</time>
      </div>
    </li>
  )
}

interface CaseActivityTimelineProps {
  caseId: string
}

export function CaseActivityTimeline({ caseId }: CaseActivityTimelineProps) {
  const query = useCaseTimeline(caseId)
  const error = isApiError(query.error)
    ? query.error
    : query.isError
      ? new ApiError(500, 'INTERNAL_ERROR', 'Unexpected error')
      : null
  const copy = error ? getErrorCopy(error, 'load') : null

  return (
    <section className={styles.panel} aria-labelledby="activity-timeline-heading">
      <h2 id="activity-timeline-heading" className={styles.title}>
        Activity
      </h2>
      <AsyncPanel
        isLoading={query.isLoading}
        isError={query.isError}
        errorTitle={
          error?.code === 'FORBIDDEN'
            ? "You don't have access to view activity"
            : copy?.title
        }
        errorMessage={copy?.message}
        onRetry={() => void query.refetch()}
        isEmpty={!query.isLoading && !query.isError && (query.data?.entries.length ?? 0) === 0}
        emptyTitle="No activity yet."
        emptyMessage="Activity will appear here as the case is updated."
      >
        <ol className={styles.list}>
          {(query.data?.entries ?? []).map((entry) => (
            <TimelineEntryRow key={entry.entryId} entry={entry} />
          ))}
        </ol>
      </AsyncPanel>
    </section>
  )
}

export default CaseActivityTimeline
