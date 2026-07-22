import type { Case, CaseStatus } from '../../api/types'

/** Assignable statuses per Screen Spec §6 (REOPENED configured but unreachable — Gap #4). */
const ASSIGNABLE_STATUSES: ReadonlySet<CaseStatus> = new Set([
  'REGISTERED',
  'REOPENED',
])

export interface UserClaims {
  userId: string
  permissions: string[]
  supervisedUnitIds: string[]
}

export type ActionKind = 'none' | 'assign' | 'status'

export interface ActionVisibility {
  kind: ActionKind
  canStartHandling: boolean
  canSubmitForReview: boolean
  canApproveClose: boolean
  canReject: boolean
}

function hasPermission(user: UserClaims, permission: string): boolean {
  return user.permissions.includes(permission)
}

export function canShowAssignPanel(caseData: Case, user: UserClaims): boolean {
  return (
    hasPermission(user, 'cases:assign') &&
    ASSIGNABLE_STATUSES.has(caseData.status)
  )
}

/**
 * Mirrors the explicit backend guard on ASSIGNED→IN_PROGRESS:
 * caller is assignee OR unit supervisor of case.unitId.
 */
export function canStartHandling(caseData: Case, user: UserClaims): boolean {
  if (!hasPermission(user, 'cases:status')) return false
  if (caseData.status !== 'ASSIGNED') return false
  if (user.userId === caseData.assigneeId) return true
  if (
    caseData.unitId &&
    user.supervisedUnitIds.includes(caseData.unitId)
  ) {
    return true
  }
  return false
}

export function canSubmitForReview(caseData: Case, user: UserClaims): boolean {
  return (
    hasPermission(user, 'cases:status') && caseData.status === 'IN_PROGRESS'
  )
}

/** No extra unit/reviewer guard today — mirrors backend (Screen Spec Gap #5). */
export function canApproveClose(caseData: Case, user: UserClaims): boolean {
  return (
    hasPermission(user, 'cases:status') && caseData.status === 'PENDING_REVIEW'
  )
}

export function canReject(caseData: Case, user: UserClaims): boolean {
  return (
    hasPermission(user, 'cases:status') && caseData.status === 'PENDING_REVIEW'
  )
}

/**
 * Exactly one of assign / status / none — Screen Spec §2 / §6.
 * Assign takes precedence when both could somehow apply (they shouldn't overlap
 * for a given status in the current workflow).
 */
export function getActionVisibility(
  caseData: Case,
  user: UserClaims,
): ActionVisibility {
  if (canShowAssignPanel(caseData, user)) {
    return {
      kind: 'assign',
      canStartHandling: false,
      canSubmitForReview: false,
      canApproveClose: false,
      canReject: false,
    }
  }

  const start = canStartHandling(caseData, user)
  const submit = canSubmitForReview(caseData, user)
  const approve = canApproveClose(caseData, user)
  const reject = canReject(caseData, user)

  if (start || submit || approve || reject) {
    return {
      kind: 'status',
      canStartHandling: start,
      canSubmitForReview: submit,
      canApproveClose: approve,
      canReject: reject,
    }
  }

  return {
    kind: 'none',
    canStartHandling: false,
    canSubmitForReview: false,
    canApproveClose: false,
    canReject: false,
  }
}
