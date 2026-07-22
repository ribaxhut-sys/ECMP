import { useState, type FormEvent } from 'react'
import { getErrorCopy, isApiError } from '../../../api/errors'
import { ConfirmDialog } from '../../../components/ConfirmDialog'
import { InlineFieldError } from '../../../components/InlineFieldError'
import { useToast } from '../../../components/Toast/ToastContainer'
import { useChangeStatus } from '../hooks/useChangeStatus'
import styles from './ApproveCloseForm.module.css'

interface ApproveCloseFormProps {
  caseId: string
  onCaseGone?: () => void
}

export function ApproveCloseForm({ caseId, onCaseGone }: ApproveCloseFormProps) {
  const { showToast } = useToast()
  const mutation = useChangeStatus(caseId)
  const [resolutionCode, setResolutionCode] = useState('')
  const [clientError, setClientError] = useState('')
  const [confirmOpen, setConfirmOpen] = useState(false)

  const serverError =
    mutation.isError && isApiError(mutation.error)
      ? mutation.error.details?.resolutionCode ||
        (mutation.error.code === 'VALIDATION_ERROR'
          ? undefined
          : getErrorCopy(mutation.error, 'status').message)
      : undefined

  function openConfirm(event: FormEvent) {
    event.preventDefault()
    if (!resolutionCode.trim()) {
      setClientError('Resolution code is required')
      return
    }
    setClientError('')
    setConfirmOpen(true)
  }

  function confirmClose() {
    mutation.mutate(
      {
        toStatus: 'CLOSED',
        resolutionCode: resolutionCode.trim(),
      },
      {
        onSuccess: () => {
          setConfirmOpen(false)
          setResolutionCode('')
          showToast('success', 'Case closed')
        },
        onError: (error) => {
          setConfirmOpen(false)
          if (isApiError(error) && error.code === 'NOT_FOUND') {
            onCaseGone?.()
            return
          }
          if (isApiError(error)) {
            showToast('error', getErrorCopy(error, 'status').message)
          } else {
            showToast('error', 'Close failed')
          }
        },
      },
    )
  }

  const fieldError = clientError || serverError
  const pending = mutation.isPending

  return (
    <div className={styles.wrap}>
      <form className={styles.form} onSubmit={openConfirm} noValidate>
        <label className={styles.field} htmlFor="resolution-code">
          <span>Resolution code</span>
          <input
            id="resolution-code"
            name="resolutionCode"
            value={resolutionCode}
            onChange={(e) => setResolutionCode(e.target.value)}
            disabled={pending}
            aria-invalid={Boolean(fieldError)}
            aria-describedby={fieldError ? 'resolution-code-error' : undefined}
            autoComplete="off"
          />
          {fieldError ? (
            <InlineFieldError id="resolution-code-error" message={fieldError} />
          ) : null}
        </label>
        <button
          type="submit"
          className={styles.submit}
          disabled={pending}
          aria-busy={pending}
        >
          {pending ? 'Working…' : 'Approve & Close'}
        </button>
      </form>

      <ConfirmDialog
        open={confirmOpen}
        title="Approve and close this case?"
        message={`Close with resolution code “${resolutionCode.trim()}”. This cannot be reopened in the current workflow.`}
        confirmLabel="Approve & Close"
        onConfirm={confirmClose}
        onCancel={() => setConfirmOpen(false)}
        isPending={pending}
      />
    </div>
  )
}
