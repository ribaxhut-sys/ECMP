import { useMutation, useQueryClient } from '@tanstack/react-query'
import { assignCase } from '../../../api/cases'
import { isApiError } from '../../../api/errors'
import type { AssignRequest, Case } from '../../../api/types'
import { caseQueryKey } from './useCase'

export function useAssignCase(caseId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (body: AssignRequest) => assignCase(caseId, body),
    retry: false,
    onSuccess: (updatedCase: Case) => {
      queryClient.setQueryData(caseQueryKey(caseId), updatedCase)
    },
    onError: (error: unknown) => {
      if (
        isApiError(error) &&
        (error.code === 'INVALID_STATE' || error.code === 'INVALID_TRANSITION')
      ) {
        void queryClient.invalidateQueries({ queryKey: caseQueryKey(caseId) })
      }
    },
  })
}
