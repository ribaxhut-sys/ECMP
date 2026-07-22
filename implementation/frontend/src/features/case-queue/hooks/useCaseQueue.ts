import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { listCases } from '../../../api/cases'
import type { CaseQueueFilters } from '../filters'

export function caseQueueQueryKey(filters: CaseQueueFilters) {
  return [
    'cases',
    {
      page: filters.page,
      pageSize: filters.pageSize,
      status: filters.status,
      priority: filters.priority,
      caseType: filters.caseType,
      assigneeId: filters.assigneeId,
    },
  ] as const
}

export function useCaseQueue(filters: CaseQueueFilters) {
  return useQuery({
    queryKey: caseQueueQueryKey(filters),
    queryFn: () => listCases(filters),
    placeholderData: keepPreviousData,
    staleTime: 0,
    retry: false,
  })
}
