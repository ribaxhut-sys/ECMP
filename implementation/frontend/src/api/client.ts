import { ApiError, parseApiErrorBody } from './errors'
import type { ApiErrorBody } from './types'

let authTokenGetter: (() => string | null) | null = null

/** Wire the AuthContext token into the fetch wrapper (called from AuthProvider). */
export function setAuthTokenGetter(getter: () => string | null): void {
  authTokenGetter = getter
}

function baseUrl(): string {
  const raw = import.meta.env.VITE_API_BASE_URL ?? ''
  return raw.replace(/\/$/, '')
}

export async function apiRequest<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const url = `${baseUrl()}${path}`
  const headers = new Headers(init.headers)
  if (!headers.has('Content-Type') && init.body) {
    headers.set('Content-Type', 'application/json')
  }
  const token = authTokenGetter?.() ?? null
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  let response: Response
  try {
    response = await fetch(url, { ...init, headers })
  } catch {
    throw new ApiError(0, 'NETWORK_ERROR', 'Network request failed')
  }

  if (response.ok) {
    if (response.status === 204) {
      return undefined as T
    }
    return (await response.json()) as T
  }

  let body: ApiErrorBody | null = null
  try {
    body = parseApiErrorBody(await response.json())
  } catch {
    body = null
  }

  throw new ApiError(
    response.status,
    body?.code ?? (response.status === 500 ? 'INTERNAL_ERROR' : 'UNKNOWN_ERROR'),
    body?.message || response.statusText || 'Request failed',
    body?.details,
  )
}
