import { useState, type FormEvent } from 'react'
import { getErrorCopy, isApiError } from '../../../api/errors'
import { InlineFieldError } from '../../../components/InlineFieldError'
import { useToast } from '../../../components/Toast/ToastContainer'
import { useAssignCase } from '../hooks/useAssignCase'
import styles from './AssignActionForm.module.css'

interface AssignActionFormProps {
  caseId: string
}

export function AssignActionForm({ caseId }: AssignActionFormProps) {
  const { showToast } = useToast()
  const mutation = useAssignCase(caseId)
  const [assigneeId, setAssigneeId] = useState('')
  const [unitId, setUnitId] = useState('')
  const [clientErrors, setClientErrors] = useState<Record<string, string>>({})

  const serverDetails =
    mutation.isError && isApiError(mutation.error)
      ? mutation.error.details ?? {}
      : {}

  const panelError =
    mutation.isError && isApiError(mutation.error) && !mutation.error.details
      ? getErrorCopy(mutation.error, 'assign').message
      : mutation.isError && isApiError(mutation.error) && mutation.error.code !== 'VALIDATION_ERROR'
        ? getErrorCopy(mutation.error, 'assign').message
        : null

  function validate(): boolean {
    const next: Record<string, string> = {}
    if (!assigneeId.trim()) next.assigneeId = 'Assignee is required'
    if (!unitId.trim()) next.unitId = 'Unit is required'
    setClientErrors(next)
    return Object.keys(next).length === 0
  }

  function onSubmit(event: FormEvent) {
    event.preventDefault()
    if (!validate()) return
    mutation.mutate(
      { assigneeId: assigneeId.trim(), unitId: unitId.trim() },
      {
        onSuccess: () => {
          showToast('success', 'Case assigned')
          setAssigneeId('')
          setUnitId('')
          setClientErrors({})
        },
        onError: (error) => {
          if (isApiError(error) && error.code === 'VALIDATION_ERROR') {
            showToast('error', 'Please correct the highlighted fields')
          } else if (isApiError(error)) {
            showToast('error', getErrorCopy(error, 'assign').message)
          } else {
            showToast('error', 'Assignment failed')
          }
        },
      },
    )
  }

  const pending = mutation.isPending
  const assigneeError = clientErrors.assigneeId || serverDetails.assigneeId
  const unitError = clientErrors.unitId || serverDetails.unitId

  return (
    <form className={styles.form} onSubmit={onSubmit} noValidate>
      <p className={styles.hint}>
        Enter assignee and unit ids (no directory lookup in this version).
      </p>

      <label className={styles.field} htmlFor="assign-assignee">
        <span>Assignee ID</span>
        <input
          id="assign-assignee"
          name="assigneeId"
          value={assigneeId}
          onChange={(e) => setAssigneeId(e.target.value)}
          disabled={pending}
          aria-invalid={Boolean(assigneeError)}
          aria-describedby={assigneeError ? 'assign-assignee-error' : undefined}
          autoComplete="off"
        />
        {assigneeError ? (
          <InlineFieldError id="assign-assignee-error" message={assigneeError} />
        ) : null}
      </label>

      <label className={styles.field} htmlFor="assign-unit">
        <span>Unit ID</span>
        <input
          id="assign-unit"
          name="unitId"
          value={unitId}
          onChange={(e) => setUnitId(e.target.value)}
          disabled={pending}
          aria-invalid={Boolean(unitError)}
          aria-describedby={unitError ? 'assign-unit-error' : undefined}
          autoComplete="off"
        />
        {unitError ? (
          <InlineFieldError id="assign-unit-error" message={unitError} />
        ) : null}
      </label>

      {panelError ? (
        <p className={styles.panelError} role="alert">
          {panelError}
          {(isApiError(mutation.error) &&
            (mutation.error.code === 'INTERNAL_ERROR' ||
              mutation.error.status === 0)) ? (
            <>
              {' '}
              <button
                type="button"
                className={styles.retry}
                onClick={() =>
                  mutation.mutate({
                    assigneeId: assigneeId.trim(),
                    unitId: unitId.trim(),
                  })
                }
                disabled={pending}
              >
                Retry
              </button>
            </>
          ) : null}
        </p>
      ) : null}

      <button
        type="submit"
        className={styles.submit}
        disabled={pending}
        aria-busy={pending}
      >
        {pending ? 'Assigning…' : 'Assign'}
      </button>
    </form>
  )
}
