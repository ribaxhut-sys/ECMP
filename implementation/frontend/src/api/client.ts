import { ApiError, parseApiErrorBody } from './errors'
import type { ApiErrorBody } from './types'

/**
 * Module-level bearer token for the fetch wrapper.
 * Set synchronously by AuthProvider during render (not only in effects).
 * Never cleared on effect cleanup — React StrictMode cleanup would otherwise
 * race TanStack Query's first fetch and drop Authorization.
 */
let authToken: string | null = null

/** Wire the AuthContext token into the fetch wrapper (called from AuthProvider). */
export function setAuthToken(token: string | null): void {
  authToken = token
}

function resolveAuthToken(): string {
  const fromStore = authToken?.trim()
  if (fromStore) return fromStore
  const fromEnv = String(import.meta.env.VITE_DEV_TOKEN ?? '').trim()
  if (fromEnv) return fromEnv
  // Last-resort default matching backend .env.example / AuthContext
  return 'dev-token'
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

  const token = resolveAuthToken()
  headers.set('Authorization', `Bearer ${token}`)

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
