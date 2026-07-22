import { useQuery } from '@tanstack/react-query'
import { getCase } from '../../../api/cases'

export function caseQueryKey(caseId: string) {
  return ['case', caseId] as const
}

export function useCase(caseId: string) {
  return useQuery({
    queryKey: caseQueryKey(caseId),
    queryFn: () => getCase(caseId),
    enabled: Boolean(caseId),
    staleTime: 0,
    retry: false,
  })
}
