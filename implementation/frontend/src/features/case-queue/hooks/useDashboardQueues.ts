import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { getDashboardQueues } from '../../../api/dashboard'

export function dashboardQueuesQueryKey() {
  return ['dashboard', 'queues'] as const
}

/** CAP-007 / API-040 — operational queue aggregates for supervisors. */
export function useDashboardQueues(enabled: boolean) {
  return useQuery({
    queryKey: dashboardQueuesQueryKey(),
    queryFn: getDashboardQueues,
    enabled,
    placeholderData: keepPreviousData,
    staleTime: 15_000,
    retry: false,
  })
}
