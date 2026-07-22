import { useState } from 'react'
import { getErrorCopy, isApiError } from '../../../api/errors'
import { ConfirmDialog } from '../../../components/ConfirmDialog'
import { useToast } from '../../../components/Toast/ToastContainer'
import { useChangeStatus } from '../hooks/useChangeStatus'
import styles from './RejectButton.module.css'

interface RejectButtonProps {
  caseId: string
}

export function RejectButton({ caseId }: RejectButtonProps) {
  const { showToast } = useToast()
  const mutation = useChangeStatus(caseId)
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [reason, setReason] = useState('')

  function confirmReject() {
    mutation.mutate(
      {
        toStatus: 'IN_PROGRESS',
        reason: reason.trim() || null,
      },
      {
        onSuccess: () => {
          setConfirmOpen(false)
          setReason('')
          showToast('success', 'Case returned to in progress')
        },
        onError: (error) => {
          if (isApiError(error)) {
            showToast('error', getErrorCopy(error, 'status').message)
          } else {
            showToast('error', 'Reject failed')
          }
        },
      },
    )
  }

  const pending = mutation.isPending
  const panelError =
    mutation.isError && isApiError(mutation.error) && !confirmOpen
      ? getErrorCopy(mutation.error, 'status').message
      : null

  return (
    <div className={styles.wrap}>
      <button
        type="button"
        className={styles.reject}
        disabled={pending}
        onClick={() => {
          mutation.reset()
          setConfirmOpen(true)
        }}
      >
        Reject
      </button>

      {panelError ? (
        <p className={styles.panelError} role="alert">
          {panelError}
        </p>
      ) : null}

      <ConfirmDialog
        open={confirmOpen}
        title="Reject this review?"
        message="The case will return to In progress for the handler."
        confirmLabel="Reject"
        onConfirm={confirmReject}
        onCancel={() => {
          if (!pending) {
            setConfirmOpen(false)
            setReason('')
          }
        }}
        isPending={pending}
      >
        <label className={styles.reason} htmlFor="reject-reason">
          <span>Reason (optional)</span>
          <textarea
            id="reject-reason"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            disabled={pending}
            rows={2}
          />
        </label>
      </ConfirmDialog>
    </div>
  )
}
