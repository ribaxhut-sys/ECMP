import { describe, expect, it } from 'vitest'
import { ApiError, getErrorCopy, isApiError } from './errors'

describe('api/errors', () => {
  it('isApiError narrows ApiError instances', () => {
    expect(isApiError(new ApiError(403, 'FORBIDDEN', 'nope'))).toBe(true)
    expect(isApiError(new Error('x'))).toBe(false)
  })

  it('returns page copy for load FORBIDDEN / NOT_FOUND', () => {
    const forbidden = getErrorCopy(
      new ApiError(403, 'FORBIDDEN', 'x'),
      'load',
    )
    expect(forbidden.placement).toBe('page')
    expect(forbidden.title).toMatch(/access/i)

    const missing = getErrorCopy(
      new ApiError(404, 'NOT_FOUND', 'x'),
      'load',
    )
    expect(missing.title).toBe('Case not found')
  })

  it('returns inline copy for assign FORBIDDEN', () => {
    const copy = getErrorCopy(new ApiError(403, 'FORBIDDEN', 'x'), 'assign')
    expect(copy.placement).toBe('inline')
  })

  it('maps network and internal errors', () => {
    const network = getErrorCopy(
      new ApiError(0, 'NETWORK_ERROR', 'down'),
      'load',
    )
    expect(network.title).toBe('Connection problem')

    const internal = getErrorCopy(
      new ApiError(500, 'INTERNAL_ERROR', 'boom'),
      'status',
    )
    expect(internal.placement).toBe('inline')
  })
})
