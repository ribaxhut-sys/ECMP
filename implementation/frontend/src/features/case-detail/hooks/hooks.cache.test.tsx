import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { renderHook, waitFor } from '@testing-library/react'
import type { ReactNode } from 'react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { Case } from '../../../api/types'
import { useAddNote } from '../../case-notes/hooks/useAddNote'
import { useCaseNotes } from '../../case-notes/hooks/useCaseNotes'
import { useAssignCase } from './useAssignCase'
import { caseQueryKey } from './useCase'
import { useCaseTimeline } from './useCaseTimeline'
import { useChangeStatus } from './useChangeStatus'

vi.mock('../../../api/cases', () => ({
  assignCase: vi.fn(),
  changeStatus: vi.fn(),
  getCaseTimeline: vi.fn(),
  listCaseNotes: vi.fn(),
  createCaseNote: vi.fn(),
}))

import {
  assignCase,
  changeStatus,
  createCaseNote,
  getCaseTimeline,
  listCaseNotes,
} from '../../../api/cases'
import { ApiError } from '../../../api/errors'

const caseId = 'CASE-00AB12CD34'

const updatedCase: Case = {
  caseId,
  customerId: 'CUST-1',
  caseType: 'COMPLAINT',
  priority: 'HIGH',
  subject: 'Test',
  description: 'Desc',
  status: 'ASSIGNED',
  channel: null,
  customerVerified: false,
  assigneeId: 'USR-2001',
  unitId: 'UNIT-01',
  createdAt: '2026-07-22T00:00:00Z',
  createdBy: 'cs.agent.1',
  updatedAt: '2026-07-22T01:00:00Z',
}

function createWrapper(client: QueryClient) {
  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    )
  }
}

describe('React Query cache synchronization', () => {
  let client: QueryClient

  beforeEach(() => {
    client = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    })
    vi.clearAllMocks()
  })

  it('useAssignCase setQueryData on success', async () => {
    vi.mocked(assignCase).mockResolvedValue(updatedCase)
    const { result } = renderHook(() => useAssignCase(caseId), {
      wrapper: createWrapper(client),
    })

    result.current.mutate({ assigneeId: 'USR-2001', unitId: 'UNIT-01' })

    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(client.getQueryData(caseQueryKey(caseId))).toEqual(updatedCase)
  })

  it('useAssignCase invalidates on INVALID_STATE', async () => {
    vi.mocked(assignCase).mockRejectedValue(
      new ApiError(409, 'INVALID_STATE', 'not assignable'),
    )
    const invalidate = vi.spyOn(client, 'invalidateQueries')
    const { result } = renderHook(() => useAssignCase(caseId), {
      wrapper: createWrapper(client),
    })

    result.current.mutate({ assigneeId: 'USR-2001', unitId: 'UNIT-01' })
    await waitFor(() => expect(result.current.isError).toBe(true))
    expect(invalidate).toHaveBeenCalledWith({
      queryKey: caseQueryKey(caseId),
    })
  })

  it('useChangeStatus setQueryData on success', async () => {
    const next = { ...updatedCase, status: 'IN_PROGRESS' as const }
    vi.mocked(changeStatus).mockResolvedValue(next)
    const { result } = renderHook(() => useChangeStatus(caseId), {
      wrapper: createWrapper(client),
    })

    result.current.mutate({ toStatus: 'IN_PROGRESS' })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(client.getQueryData(caseQueryKey(caseId))).toEqual(next)
  })

  it('useCaseTimeline loads entries', async () => {
    vi.mocked(getCaseTimeline).mockResolvedValue({
      entries: [
        {
          entryId: '1',
          actionCode: 'case.create',
          actorUserId: 'cs.agent.1',
          occurredAt: '2026-07-22T00:00:00Z',
          summary: 'Case created',
          detail: {},
        },
      ],
    })
    const { result } = renderHook(() => useCaseTimeline(caseId), {
      wrapper: createWrapper(client),
    })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data?.entries).toHaveLength(1)
  })

  it('useAddNote invalidates case-notes list', async () => {
    vi.mocked(createCaseNote).mockResolvedValue({
      noteId: 'n1',
      caseId,
      authorUserId: 'cs.agent.1',
      body: 'hi',
      createdAt: '2026-07-22T00:00:00Z',
    })
    vi.mocked(listCaseNotes).mockResolvedValue({ items: [] })
    const invalidate = vi.spyOn(client, 'invalidateQueries')

    const { result } = renderHook(() => useAddNote(caseId), {
      wrapper: createWrapper(client),
    })
    result.current.mutate({ body: 'hi' })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(invalidate).toHaveBeenCalledWith({
      queryKey: ['case-notes', caseId],
    })
  })

  it('useCaseNotes loads list', async () => {
    vi.mocked(listCaseNotes).mockResolvedValue({
      items: [
        {
          noteId: 'n1',
          caseId,
          authorUserId: 'cs.agent.1',
          body: 'hi',
          createdAt: '2026-07-22T00:00:00Z',
        },
      ],
    })
    const { result } = renderHook(() => useCaseNotes(caseId), {
      wrapper: createWrapper(client),
    })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data?.items[0].body).toBe('hi')
  })
})
