import { useQuery } from '@tanstack/react-query'
import { listCaseNotes } from '../../../api/cases'

export function caseNotesQueryKey(caseId: string) {
  return ['case-notes', caseId] as const
}

export function useCaseNotes(caseId: string) {
  return useQuery({
    queryKey: caseNotesQueryKey(caseId),
    queryFn: () => listCaseNotes(caseId),
    enabled: Boolean(caseId),
    staleTime: 0,
    retry: false,
  })
}
