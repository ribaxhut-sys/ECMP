import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createCaseNote } from '../../../api/cases'
import type { NoteCreateRequest } from '../../../api/types'
import { caseNotesQueryKey } from './useCaseNotes'

export function useAddNote(caseId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (body: NoteCreateRequest) => createCaseNote(caseId, body),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: caseNotesQueryKey(caseId),
      })
    },
    retry: false,
  })
}
