import { useQuery } from '@tanstack/react-query'
import { getCaseTimeline } from '../../../api/cases'

export function caseTimelineQueryKey(caseId: string) {
  return ['case-timeline', caseId] as const
}

export function useCaseTimeline(caseId: string) {
  return useQuery({
    queryKey: caseTimelineQueryKey(caseId),
    queryFn: () => getCaseTimeline(caseId),
    enabled: Boolean(caseId),
    staleTime: 0,
    retry: false,
  })
}
