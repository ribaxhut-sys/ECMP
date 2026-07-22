import { useMutation, useQueryClient } from '@tanstack/react-query'
import { changeStatus } from '../../../api/cases'
import { isApiError } from '../../../api/errors'
import type { Case, StatusChangeRequest } from '../../../api/types'
import { caseQueryKey } from './useCase'

export function useChangeStatus(caseId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (body: StatusChangeRequest) => changeStatus(caseId, body),
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
