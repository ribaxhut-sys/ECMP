import type { ApiErrorBody } from './types'

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public details?: Record<string, string>,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export type ErrorContext = 'load' | 'assign' | 'status'

/**
 * Screen Spec §7 / IMPLEMENTATION_PLAN §9 — purpose-written copy by code.
 * `error.message` is fallback only for unexpected codes.
 */
export function getErrorCopy(
  error: ApiError,
  context: ErrorContext,
): { title: string; message: string; placement: 'page' | 'inline' } {
  switch (error.code) {
    case 'FORBIDDEN':
      if (context === 'load') {
        return {
          title: "You don't have access to this case",
          message: "You don't have permission to view this case.",
          placement: 'page',
        }
      }
      return {
        title: "You don't have permission to do this",
        message: "You don't have permission to do this",
        placement: 'inline',
      }
    case 'NOT_FOUND':
      return {
        title: 'Case not found',
        message: 'This case does not exist or is no longer available.',
        placement: 'page',
      }
    case 'INVALID_STATE':
      return {
        title: 'This case is no longer assignable',
        message: 'This case is no longer assignable',
        placement: 'inline',
      }
    case 'INVALID_TRANSITION':
      return {
        title: 'This action is no longer available',
        message: 'This action is no longer available',
        placement: 'inline',
      }
    case 'NETWORK_ERROR':
      return {
        title: 'Connection problem',
        message: 'Connection problem. Check your network and try again.',
        placement: context === 'load' ? 'page' : 'inline',
      }
    case 'INTERNAL_ERROR':
      return {
        title: 'Something went wrong',
        message: 'Something went wrong. Please try again.',
        placement: context === 'load' ? 'page' : 'inline',
      }
    case 'VALIDATION_ERROR':
      return {
        title: 'Validation error',
        message: error.message || 'Please correct the highlighted fields.',
        placement: 'inline',
      }
    default:
      return {
        title: 'Error',
        message: error.message || 'An unexpected error occurred.',
        placement: context === 'load' ? 'page' : 'inline',
      }
  }
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError
}

export function parseApiErrorBody(body: unknown): ApiErrorBody | null {
  if (
    body &&
    typeof body === 'object' &&
    'code' in body &&
    'message' in body &&
    typeof (body as ApiErrorBody).code === 'string' &&
    typeof (body as ApiErrorBody).message === 'string'
  ) {
    return body as ApiErrorBody
  }
  return null
}
