/**
 * Hand-written types mirroring case-service.v1.yaml v1.5.0.
 * Source of truth: 07 API Catalog/openapi/case-service.v1.yaml
 * If the contract changes, update this file by hand in the same PR.
 * No codegen tool was decided in ADR-013.
 */

export type CaseType = 'COMPLAINT' | 'INQUIRY'
export type Priority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
export type CaseStatus =
  | 'REGISTERED'
  | 'ASSIGNED'
  | 'IN_PROGRESS'
  | 'PENDING_REVIEW'
  | 'CLOSED'
  | 'REOPENED'

export interface Case {
  caseId: string
  customerId: string
  caseType: CaseType
  priority: Priority
  subject: string
  description: string
  status: CaseStatus
  channel: string | null
  customerVerified: boolean
  assigneeId: string | null
  unitId: string | null
  createdAt: string
  createdBy: string
  updatedAt: string
}

export interface AssignRequest {
  assigneeId: string
  unitId: string
}

export interface StatusChangeRequest {
  toStatus: CaseStatus
  resolutionCode?: string | null
  reason?: string | null
}

export interface ApiErrorBody {
  code: string
  message: string
  details?: Record<string, string>
}
