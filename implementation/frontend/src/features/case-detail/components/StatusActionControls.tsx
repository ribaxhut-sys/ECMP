import { useState } from 'react'
import { getErrorCopy, isApiError } from '../../../api/errors'
import { useToast } from '../../../components/Toast/ToastContainer'
import type { ActionVisibility } from '../permissions'
import { useChangeStatus } from '../hooks/useChangeStatus'
import { ApproveCloseForm } from './ApproveCloseForm'
import { RejectButton } from './RejectButton'
import styles from './StatusActionControls.module.css'

interface StatusActionControlsProps {
  caseId: string
  visibility: ActionVisibility
  /** On mobile sticky bar: park Reject behind an overflow menu (Screen Spec §10). */
  mobileCompact?: boolean
}

export function StatusActionControls({
  caseId,
  visibility,
  mobileCompact = false,
}: StatusActionControlsProps) {
  const { showToast } = useToast()
  const mutation = useChangeStatus(caseId)
  const [menuOpen, setMenuOpen] = useState(false)

  const panelError =
    mutation.isError && isApiError(mutation.error)
      ? getErrorCopy(mutation.error, 'status').message
      : null

  function runSimpleTransition(
    toStatus: 'IN_PROGRESS' | 'PENDING_REVIEW',
    successMessage: string,
  ) {
    mutation.mutate(
      { toStatus },
      {
        onSuccess: () => showToast('success', successMessage),
        onError: (error) => {
          if (isApiError(error)) {
            showToast('error', getErrorCopy(error, 'status').message)
          } else {
            showToast('error', 'Status change failed')
          }
        },
      },
    )
  }

  const pending = mutation.isPending
  const showSimpleError =
    Boolean(panelError) &&
    (visibility.canStartHandling || visibility.canSubmitForReview)
  const rejectInOverflow =
    mobileCompact && visibility.canReject && visibility.canApproveClose

  return (
    <div
      className={`${styles.controls} ${mobileCompact ? styles.compact : ''}`}
    >
      {visibility.canStartHandling ? (
        <button
          type="button"
          className={styles.primary}
          disabled={pending}
          aria-busy={pending}
          onClick={() =>
            runSimpleTransition('IN_PROGRESS', 'Case is now in progress')
          }
        >
          {pending ? 'Working…' : 'Start Handling'}
        </button>
      ) : null}

      {visibility.canSubmitForReview ? (
        <button
          type="button"
          className={styles.primary}
          disabled={pending}
          aria-busy={pending}
          onClick={() =>
            runSimpleTransition('PENDING_REVIEW', 'Submitted for review')
          }
        >
          {pending ? 'Working…' : 'Submit for Review'}
        </button>
      ) : null}

      {visibility.canApproveClose ? (
        <ApproveCloseForm caseId={caseId} />
      ) : null}

      {visibility.canReject && !rejectInOverflow ? (
        <RejectButton caseId={caseId} />
      ) : null}

      {rejectInOverflow ? (
        <div className={styles.overflow}>
          <button
            type="button"
            className={styles.kebab}
            aria-label="More actions"
            aria-expanded={menuOpen}
            aria-haspopup="menu"
            onClick={() => setMenuOpen((open) => !open)}
          >
            ⋮
          </button>
          {menuOpen ? (
            <div className={styles.menu} role="menu">
              <RejectButton caseId={caseId} />
            </div>
          ) : null}
        </div>
      ) : null}

      {showSimpleError ? (
        <p className={styles.panelError} role="alert">
          {panelError}
        </p>
      ) : null}
    </div>
  )
}
