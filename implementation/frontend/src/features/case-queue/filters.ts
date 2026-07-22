import type { CaseStatus, CaseType, Priority } from '../../api/types'

export interface CaseQueueFilters {
  page: number
  pageSize: number
  status?: CaseStatus
  priority?: Priority
  caseType?: CaseType
  assigneeId?: string
}

const CASE_STATUSES: readonly CaseStatus[] = [
  'REGISTERED',
  'ASSIGNED',
  'IN_PROGRESS',
  'PENDING_REVIEW',
  'CLOSED',
  'REOPENED',
] as const

const PRIORITIES: readonly Priority[] = [
  'LOW',
  'MEDIUM',
  'HIGH',
  'CRITICAL',
] as const

const CASE_TYPES: readonly CaseType[] = ['COMPLAINT', 'INQUIRY'] as const

export const QUEUE_STATUS_OPTIONS = CASE_STATUSES
export const QUEUE_PRIORITY_OPTIONS = PRIORITIES
export const QUEUE_CASE_TYPE_OPTIONS = CASE_TYPES

const DEFAULT_PAGE = 1
const DEFAULT_PAGE_SIZE = 20
const MAX_PAGE_SIZE = 100

function parsePositiveInt(raw: string | null, fallback: number): number {
  if (!raw) return fallback
  const n = Number.parseInt(raw, 10)
  if (!Number.isFinite(n) || n < 1) return fallback
  return n
}

function isCaseStatus(value: string): value is CaseStatus {
  return (CASE_STATUSES as readonly string[]).includes(value)
}

function isPriority(value: string): value is Priority {
  return (PRIORITIES as readonly string[]).includes(value)
}

function isCaseType(value: string): value is CaseType {
  return (CASE_TYPES as readonly string[]).includes(value)
}

/** Parse queue filters from URL search params; clamp pageSize ≤ 100. */
export function parseQueueFilters(params: URLSearchParams): CaseQueueFilters {
  const page = parsePositiveInt(params.get('page'), DEFAULT_PAGE)
  const pageSize = Math.min(
    MAX_PAGE_SIZE,
    parsePositiveInt(params.get('pageSize'), DEFAULT_PAGE_SIZE),
  )

  const statusRaw = params.get('status')
  const priorityRaw = params.get('priority')
  const caseTypeRaw = params.get('caseType')
  const assigneeRaw = params.get('assigneeId')?.trim()

  return {
    page,
    pageSize,
    status: statusRaw && isCaseStatus(statusRaw) ? statusRaw : undefined,
    priority: priorityRaw && isPriority(priorityRaw) ? priorityRaw : undefined,
    caseType: caseTypeRaw && isCaseType(caseTypeRaw) ? caseTypeRaw : undefined,
    assigneeId: assigneeRaw || undefined,
  }
}

export function hasActiveFilters(filters: CaseQueueFilters): boolean {
  return Boolean(
    filters.status || filters.priority || filters.caseType || filters.assigneeId,
  )
}

/** Build URLSearchParams from filters; omits defaults and empty filters. */
export function filtersToSearchParams(filters: CaseQueueFilters): URLSearchParams {
  const next = new URLSearchParams()
  if (filters.page !== DEFAULT_PAGE) next.set('page', String(filters.page))
  if (filters.pageSize !== DEFAULT_PAGE_SIZE) {
    next.set('pageSize', String(filters.pageSize))
  }
  if (filters.status) next.set('status', filters.status)
  if (filters.priority) next.set('priority', filters.priority)
  if (filters.caseType) next.set('caseType', filters.caseType)
  if (filters.assigneeId) next.set('assigneeId', filters.assigneeId)
  return next
}

export function defaultQueueFilters(): CaseQueueFilters {
  return { page: DEFAULT_PAGE, pageSize: DEFAULT_PAGE_SIZE }
}
