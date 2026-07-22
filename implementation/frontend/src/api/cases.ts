import { apiRequest } from './client'
import type {
  AssignRequest,
  Case,
  CaseNote,
  CaseNoteList,
  CasePage,
  CaseStatus,
  CaseTimeline,
  CaseType,
  NoteCreateRequest,
  Priority,
  StatusChangeRequest,
} from './types'

export interface ListCasesParams {
  page: number
  pageSize: number
  status?: CaseStatus
  priority?: Priority
  caseType?: CaseType
  assigneeId?: string
}

/** GET /v1/cases — API-005 */
export function listCases(params: ListCasesParams): Promise<CasePage> {
  const qs = new URLSearchParams()
  qs.set('page', String(params.page))
  qs.set('pageSize', String(params.pageSize))
  if (params.status) qs.set('status', params.status)
  if (params.priority) qs.set('priority', params.priority)
  if (params.caseType) qs.set('caseType', params.caseType)
  if (params.assigneeId) qs.set('assigneeId', params.assigneeId)
  return apiRequest<CasePage>(`/v1/cases?${qs.toString()}`)
}

/** GET /v1/cases/{caseId} — API-002 */
export function getCase(caseId: string): Promise<Case> {
  return apiRequest<Case>(`/v1/cases/${encodeURIComponent(caseId)}`)
}

/** GET /v1/cases/{caseId}/timeline — API-006 */
export function getCaseTimeline(caseId: string): Promise<CaseTimeline> {
  return apiRequest<CaseTimeline>(
    `/v1/cases/${encodeURIComponent(caseId)}/timeline`,
  )
}

/** GET /v1/cases/{caseId}/notes — API-007 */
export function listCaseNotes(caseId: string): Promise<CaseNoteList> {
  return apiRequest<CaseNoteList>(
    `/v1/cases/${encodeURIComponent(caseId)}/notes`,
  )
}

/** POST /v1/cases/{caseId}/notes — API-008 */
export function createCaseNote(
  caseId: string,
  body: NoteCreateRequest,
): Promise<CaseNote> {
  return apiRequest<CaseNote>(
    `/v1/cases/${encodeURIComponent(caseId)}/notes`,
    {
      method: 'POST',
      body: JSON.stringify(body),
    },
  )
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
