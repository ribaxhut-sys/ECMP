import { apiRequest } from './client'
import type { AssignRequest, Case, StatusChangeRequest } from './types'

/** GET /v1/cases/{caseId} — API-002 */
export function getCase(caseId: string): Promise<Case> {
  return apiRequest<Case>(`/v1/cases/${encodeURIComponent(caseId)}`)
}

/** POST /v1/cases/{caseId}/assign — API-003 */
export function assignCase(caseId: string, body: AssignRequest): Promise<Case> {
  return apiRequest<Case>(`/v1/cases/${encodeURIComponent(caseId)}/assign`, {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

/** POST /v1/cases/{caseId}/status — API-004 */
export function changeStatus(
  caseId: string,
  body: StatusChangeRequest,
): Promise<Case> {
  return apiRequest<Case>(`/v1/cases/${encodeURIComponent(caseId)}/status`, {
    method: 'POST',
    body: JSON.stringify(body),
  })
}
