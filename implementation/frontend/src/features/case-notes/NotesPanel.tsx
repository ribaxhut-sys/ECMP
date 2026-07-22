import { useState, type FormEvent } from 'react'
import { ApiError, getErrorCopy, isApiError } from '../../api/errors'
import { useAuth } from '../../auth/AuthContext'
import { AsyncPanel } from '../../components/AsyncPanel'
import { InlineFieldError } from '../../components/InlineFieldError'
import { useToast } from '../../components/Toast/ToastContainer'
import { useAddNote } from './hooks/useAddNote'
import { useCaseNotes } from './hooks/useCaseNotes'
import styles from './NotesPanel.module.css'

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

interface NotesPanelProps {
  caseId: string
}

export function NotesPanel({ caseId }: NotesPanelProps) {
  const { hasPermission } = useAuth()
  const canCreate = hasPermission('cases:notes:create')
  const { showToast } = useToast()
  const query = useCaseNotes(caseId)
  const mutation = useAddNote(caseId)
  const [body, setBody] = useState('')
  const [clientError, setClientError] = useState<string | null>(null)

  const error = isApiError(query.error)
    ? query.error
    : query.isError
      ? new ApiError(500, 'INTERNAL_ERROR', 'Unexpected error')
      : null
  const copy = error ? getErrorCopy(error, 'load') : null

  function onSubmit(event: FormEvent) {
    event.preventDefault()
    const trimmed = body.trim()
    if (!trimmed) {
      setClientError('Note text is required')
      return
    }
    setClientError(null)
    mutation.mutate(
      { body: trimmed },
      {
        onSuccess: () => {
          setBody('')
          showToast('success', 'Note added')
        },
      },
    )
  }

  const mutationError =
    mutation.isError && isApiError(mutation.error)
      ? getErrorCopy(mutation.error, 'assign').message
      : mutation.isError
        ? 'Could not add note'
        : null

  return (
    <section className={styles.panel} aria-labelledby="notes-heading">
      <h2 id="notes-heading" className={styles.title}>
        Internal notes
      </h2>

      <AsyncPanel
        isLoading={query.isLoading}
        isError={query.isError}
        errorTitle={
          error?.code === 'FORBIDDEN'
            ? "You don't have access to view notes"
            : copy?.title
        }
        errorMessage={copy?.message}
        onRetry={() => void query.refetch()}
        isEmpty={!query.isLoading && !query.isError && (query.data?.items.length ?? 0) === 0}
        emptyTitle="No notes yet."
        emptyMessage="Internal notes will appear here when added."
      >
        <ul className={styles.list}>
          {(query.data?.items ?? []).map((note) => (
            <li key={note.noteId} className={styles.item}>
              <p className={styles.body}>{note.body}</p>
              <div className={styles.meta}>
                <span>{note.authorUserId}</span>
                <span aria-hidden="true">·</span>
                <time dateTime={note.createdAt}>{formatWhen(note.createdAt)}</time>
              </div>
            </li>
          ))}
        </ul>
      </AsyncPanel>

      {canCreate ? (
        <form className={styles.composer} onSubmit={onSubmit} noValidate>
          <label className={styles.label} htmlFor={`note-body-${caseId}`}>
            Add note
          </label>
          <textarea
            id={`note-body-${caseId}`}
            className={styles.textarea}
            rows={3}
            value={body}
            maxLength={4000}
            onChange={(e) => {
              setBody(e.target.value)
              if (clientError) setClientError(null)
            }}
            disabled={mutation.isPending}
            aria-invalid={Boolean(clientError)}
          />
          {clientError ? <InlineFieldError message={clientError} /> : null}
          {mutationError ? <p className={styles.panelError}>{mutationError}</p> : null}
          <button
            type="submit"
            className={styles.submit}
            disabled={mutation.isPending}
          >
            {mutation.isPending ? 'Saving…' : 'Add note'}
          </button>
        </form>
      ) : (
        <p className={styles.readOnlyHint}>
          You can view notes but do not have permission to add them.
        </p>
      )}
    </section>
  )
}

export default NotesPanel
