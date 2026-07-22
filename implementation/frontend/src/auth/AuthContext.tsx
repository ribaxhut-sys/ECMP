import {
  createContext,
  useCallback,
  useContext,
  useLayoutEffect,
  useMemo,
  type ReactNode,
} from 'react'
import { setAuthToken } from '../api/client'

/**
 * Dev-mode AuthContext (ADR-013 item 7 — token acquisition unresolved).
 * Mirrors backend static fixtures in app/auth.py. Not a login flow.
 */

export interface AuthClaims {
  token: string
  userId: string
  permissions: string[]
  supervisedUnitIds: string[]
}

interface AuthContextValue extends AuthClaims {
  hasPermission: (permission: string) => boolean
  /** Hook for future app-shell 401 handling — this screen does not redirect. */
  onUnauthenticated?: () => void
}

const DEV_FIXTURES: Record<string, Omit<AuthClaims, 'token'>> = {
  'dev-token': {
    userId: 'cs.agent.1',
    permissions: ['cases:create', 'cases:read', 'cases:notes:create'],
    supervisedUnitIds: [],
  },
  'dev-readonly-token': {
    userId: 'viewer.1',
    permissions: ['cases:read'],
    supervisedUnitIds: [],
  },
  'dev-supervisor-token': {
    userId: 'supervisor.1',
    permissions: [
      'cases:assign',
      'cases:read',
      'cases:create',
      'cases:notes:create',
    ],
    supervisedUnitIds: ['UNIT-01'],
  },
  'dev-handler-token': {
    userId: 'USR-2001',
    permissions: ['cases:status', 'cases:read', 'cases:notes:create'],
    supervisedUnitIds: [],
  },
  'dev-noperm-token': {
    userId: 'noperm.1',
    permissions: [],
    supervisedUnitIds: [],
  },
  'dev-foreign-supervisor-token': {
    userId: 'supervisor.other',
    permissions: ['cases:assign', 'cases:read', 'cases:notes:create'],
    supervisedUnitIds: ['UNIT-99'],
  },
}

const AuthContext = createContext<AuthContextValue | null>(null)

function resolveClaims(token: string): AuthClaims {
  const fixture = DEV_FIXTURES[token]
  if (!fixture) {
    return {
      token,
      userId: 'unknown',
      permissions: [],
      supervisedUnitIds: [],
    }
  }
  return { token, ...fixture }
}

interface AuthProviderProps {
  children: ReactNode
  onUnauthenticated?: () => void
}

export function AuthProvider({ children, onUnauthenticated }: AuthProviderProps) {
  const token = import.meta.env.VITE_DEV_TOKEN || 'dev-token'
  const claims = useMemo(() => resolveClaims(token), [token])

  // Synchronous write — must happen before children schedule fetches.
  // Do not clear on effect cleanup (StrictMode would race the first query).
  setAuthToken(claims.token)
  useLayoutEffect(() => {
    setAuthToken(claims.token)
  }, [claims.token])

  const hasPermission = useCallback(
    (permission: string) => claims.permissions.includes(permission),
    [claims.permissions],
  )

  const value = useMemo<AuthContextValue>(
    () => ({ ...claims, hasPermission, onUnauthenticated }),
    [claims, hasPermission, onUnauthenticated],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return ctx
}
