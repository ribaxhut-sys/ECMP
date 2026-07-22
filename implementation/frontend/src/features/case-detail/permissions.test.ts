import { describe, expect, it } from 'vitest'
import type { Case } from '../../api/types'
import {
  canApproveClose,
  canReject,
  canShowAssignPanel,
  canStartHandling,
  canSubmitForReview,
  getActionVisibility,
  type UserClaims,
} from './permissions'

const baseCase: Case = {
  caseId: 'CASE-00AB12CD34',
  customerId: 'CUST-1',
  caseType: 'COMPLAINT',
  priority: 'HIGH',
  subject: 'Test',
  description: 'Desc',
  status: 'REGISTERED',
  channel: 'CALL',
  customerVerified: false,
  assigneeId: null,
  unitId: null,
  createdAt: '2026-07-22T00:00:00Z',
  createdBy: 'cs.agent.1',
  updatedAt: '2026-07-22T00:00:00Z',
}

const supervisor: UserClaims = {
  userId: 'supervisor.1',
  permissions: ['cases:assign', 'cases:read'],
  supervisedUnitIds: ['UNIT-01'],
}

const handler: UserClaims = {
  userId: 'USR-2001',
  permissions: ['cases:status', 'cases:read'],
  supervisedUnitIds: [],
}

describe('permissions', () => {
  it('shows assign panel for REGISTERED + cases:assign', () => {
    expect(canShowAssignPanel(baseCase, supervisor)).toBe(true)
    expect(getActionVisibility(baseCase, supervisor).kind).toBe('assign')
  })

  it('hides assign without permission', () => {
    expect(canShowAssignPanel(baseCase, handler)).toBe(false)
  })

  it('allows start handling for assignee on ASSIGNED', () => {
    const assigned = {
      ...baseCase,
      status: 'ASSIGNED' as const,
      assigneeId: 'USR-2001',
      unitId: 'UNIT-01',
    }
    expect(canStartHandling(assigned, handler)).toBe(true)
    expect(getActionVisibility(assigned, handler).canStartHandling).toBe(true)
  })

  it('allows start handling for unit supervisor', () => {
    const assigned = {
      ...baseCase,
      status: 'ASSIGNED' as const,
      assigneeId: 'USR-9999',
      unitId: 'UNIT-01',
    }
    const unitSupervisor: UserClaims = {
      userId: 'supervisor.1',
      permissions: ['cases:status'],
      supervisedUnitIds: ['UNIT-01'],
    }
    expect(canStartHandling(assigned, unitSupervisor)).toBe(true)
  })

  it('gates submit / approve / reject by status', () => {
    const inProgress = { ...baseCase, status: 'IN_PROGRESS' as const }
    expect(canSubmitForReview(inProgress, handler)).toBe(true)
    expect(canApproveClose(inProgress, handler)).toBe(false)

    const pending = { ...baseCase, status: 'PENDING_REVIEW' as const }
    expect(canApproveClose(pending, handler)).toBe(true)
    expect(canReject(pending, handler)).toBe(true)
  })

  it('returns none when no actions apply', () => {
    const viewer: UserClaims = {
      userId: 'viewer.1',
      permissions: ['cases:read'],
      supervisedUnitIds: [],
    }
    expect(getActionVisibility(baseCase, viewer).kind).toBe('none')
  })
})
