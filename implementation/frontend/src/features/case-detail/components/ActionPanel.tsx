import type { Case } from '../../../api/types'
import { useAuth } from '../../../auth/AuthContext'
import { getActionVisibility } from '../permissions'
import { AssignActionForm } from './AssignActionForm'
import styles from './ActionPanel.module.css'

interface ActionPanelProps {
  caseData: Case
  isRefreshing?: boolean
}

/**
 * Permission-aware action gate — renders 0 or 1 action surface (Screen Spec §6).
 */
export function ActionPanel({ caseData, isRefreshing = false }: ActionPanelProps) {
  const auth = useAuth()
  const visibility = getActionVisibility(caseData, {
    userId: auth.userId,
    permissions: auth.permissions,
    supervisedUnitIds: auth.supervisedUnitIds,
  })

  if (visibility.kind === 'none') {
    return null
  }

  return (
    <section
      className={styles.panel}
      aria-labelledby="action-panel-heading"
      data-action-kind={visibility.kind}
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
        <ul className={styles.stubList} data-testid="status-gate">
          {visibility.canStartHandling ? (
            <li>Start Handling</li>
          ) : null}
          {visibility.canSubmitForReview ? (
            <li>Submit for Review</li>
          ) : null}
          {visibility.canApproveClose ? (
            <li>Approve &amp; Close</li>
          ) : null}
          {visibility.canReject ? <li>Reject</li> : null}
        </ul>
      )}
    </section>
  )
}
