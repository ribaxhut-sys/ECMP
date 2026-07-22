import type { Case } from '../../../api/types'
import { useAuth } from '../../../auth/AuthContext'
import { getActionVisibility, type ActionVisibility } from '../permissions'
import { AssignActionForm } from './AssignActionForm'
import { StatusActionControls } from './StatusActionControls'
import styles from './ActionPanel.module.css'

interface ActionPanelProps {
  caseData: Case
  isRefreshing?: boolean
  /** Mobile sticky bottom bar layout (Screen Spec §10). */
  stickyMobile?: boolean
}

function primaryLabel(visibility: ActionVisibility): string | null {
  if (visibility.kind === 'assign') return 'Assign'
  if (visibility.canStartHandling) return 'Start Handling'
  if (visibility.canSubmitForReview) return 'Submit for Review'
  if (visibility.canApproveClose) return 'Approve & Close'
  if (visibility.canReject) return 'Reject'
  return null
}

/**
 * Permission-aware action gate — renders 0 or 1 action surface (Screen Spec §6).
 */
export function ActionPanel({
  caseData,
  isRefreshing = false,
  stickyMobile = false,
}: ActionPanelProps) {
  const auth = useAuth()
  const visibility = getActionVisibility(caseData, {
    userId: auth.userId,
    permissions: auth.permissions,
    supervisedUnitIds: auth.supervisedUnitIds,
  })

  if (visibility.kind === 'none') {
    return null
  }

  const label = primaryLabel(visibility)

  return (
    <section
      className={`${styles.panel} ${stickyMobile ? styles.stickyMobile : ''}`}
      aria-labelledby="action-panel-heading"
      data-action-kind={visibility.kind}
      data-primary-action={label ?? undefined}
    >
      <div className={styles.headerRow}>
        <h2 id="action-panel-heading" className={styles.title}>
          Actions
        </h2>
        {isRefreshing ? (
          <span className={styles.refreshing} aria-live="polite">
            Refreshing case…
          </span>
        ) : null}
      </div>

      {visibility.kind === 'assign' ? (
        <AssignActionForm caseId={caseData.caseId} />
      ) : (
        <StatusActionControls
          caseId={caseData.caseId}
          visibility={visibility}
          mobileCompact={stickyMobile}
        />
      )}
    </section>
  )
}
