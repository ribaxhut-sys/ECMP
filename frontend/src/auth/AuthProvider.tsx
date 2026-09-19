"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import {
  fetchCurrentUser,
  login as apiLogin,
  logout as apiLogout,
  refreshAccessToken,
} from "@/lib/api/auth";
import { setAuthToken } from "@/lib/api/client";
import type { AuthMe } from "@/lib/api/types";
import { isMockAuthEnabled, isShellUiBatch } from "@/shared/config/uiBatch";
import {
  clearMockSession,
  mockLogin,
  readMockSession,
  updateOfficerWorkMode,
  writeMockSession,
  type MockPersonaId,
  type MockSession,
  type OfficerWorkMode,
} from "@/auth/mockAuth";
import { principalHasPermission } from "@/auth/permissionCheck";

type AuthStatus = "loading" | "authenticated" | "unauthenticated";

interface AuthContextValue {
  status: AuthStatus;
  user: AuthMe | null;
  userId: string | null;
  permissions: readonly string[];
  roles: readonly string[];
  forcePasswordChange: boolean;
  /** True when session comes from mockAuth (Batch B0). */
  isMockSession: boolean;
  mockPersona: MockPersonaId | null;
  officerWorkMode: OfficerWorkMode | null;
  hasPermission: (permission: string) => boolean;
  login: (username: string, password: string) => Promise<AuthMe>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<boolean>;
  refreshUser: () => Promise<boolean>;
  /** Merge fields into the in-memory AuthMe (e.g. preferredLanguage). */
  patchUser: (partial: Partial<AuthMe>) => void;
  /** Officer intake ↔ handling (mock / B0 only). */
  setOfficerWorkMode: (mode: OfficerWorkMode) => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>("loading");
  const [user, setUser] = useState<AuthMe | null>(null);
  const [mockSession, setMockSession] = useState<MockSession | null>(null);

  const applyUser = useCallback((next: AuthMe | null) => {
    setUser(next);
    setStatus(next ? "authenticated" : "unauthenticated");
  }, []);

  const applyMockSession = useCallback(
    (session: MockSession | null) => {
      setMockSession(session);
      if (session) {
        setAuthToken("mock-access-token");
        applyUser(session.user);
      } else {
        setAuthToken(null);
        applyUser(null);
      }
    },
    [applyUser],
  );

  const loadMe = useCallback(async (): Promise<AuthMe | null> => {
    try {
      const me = await fetchCurrentUser();
      setMockSession(null);
      applyUser(me);
      return me;
    } catch {
      setAuthToken(null);
      applyUser(null);
      return null;
    }
  }, [applyUser]);

  const refreshSession = useCallback(async (): Promise<boolean> => {
    if (isMockAuthEnabled() && readMockSession()) {
      const session = readMockSession();
      applyMockSession(session);
      return session != null;
    }
    const tokens = await refreshAccessToken();
    if (!tokens) {
      applyUser(null);
      return false;
    }
    const me = await loadMe();
    return me != null;
  }, [applyMockSession, applyUser, loadMe]);

  const refreshUser = useCallback(async (): Promise<boolean> => {
    if (mockSession) {
      const session = readMockSession();
      applyMockSession(session);
      return session != null;
    }
    const me = await loadMe();
    return me != null;
  }, [applyMockSession, loadMe, mockSession]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      if (isMockAuthEnabled()) {
        const existing = readMockSession();
        if (cancelled) return;
        if (existing) {
          applyMockSession(existing);
          return;
        }
        if (isShellUiBatch()) {
          applyMockSession(null);
          return;
        }
      }
      const tokens = await refreshAccessToken();
      if (cancelled) return;
      if (!tokens) {
        applyUser(null);
        return;
      }
      await loadMe();
    })();
    return () => {
      cancelled = true;
    };
  }, [applyMockSession, applyUser, loadMe]);

  const login = useCallback(
    async (username: string, password: string) => {
      if (isMockAuthEnabled()) {
        try {
          const session = mockLogin(username, password);
          applyMockSession(session);
          return session.user;
        } catch (err) {
          if (isShellUiBatch()) {
            throw err;
          }
          // Non-shell mock mode: fall through to real API
        }
      }
      await apiLogin(username, password);
      const me = await loadMe();
      if (!me) {
        throw new Error("PROFILE_LOAD_FAILED");
      }
      return me;
    },
    [applyMockSession, loadMe],
  );

  const logout = useCallback(async () => {
    if (mockSession || readMockSession()) {
      clearMockSession();
      applyMockSession(null);
      return;
    }
    await apiLogout();
    applyUser(null);
  }, [applyMockSession, applyUser, mockSession]);

  const patchUser = useCallback((partial: Partial<AuthMe>) => {
    setUser((prev) => (prev ? { ...prev, ...partial } : prev));
    setMockSession((prev) => {
      if (!prev) return prev;
      const next = {
        ...prev,
        user: { ...prev.user, ...partial },
      };
      writeMockSession(next);
      return next;
    });
  }, []);

  const setOfficerWorkMode = useCallback(
    (mode: OfficerWorkMode) => {
      const next = updateOfficerWorkMode(mode);
      if (next) applyMockSession(next);
    },
    [applyMockSession],
  );

  const permissions = useMemo(
    () => user?.permissions ?? [],
    [user?.permissions],
  );
  const roles = useMemo(() => user?.roles ?? [], [user?.roles]);
  const forcePasswordChange = Boolean(user?.forcePasswordChange);

  const hasPermission = useCallback(
    (permission: string) => principalHasPermission(permissions, permission),
    [permissions],
  );

  const value = useMemo<AuthContextValue>(
    () => ({
      status,
      user,
      userId: user?.id ?? null,
      permissions,
      roles,
      forcePasswordChange,
      isMockSession: mockSession != null,
      mockPersona: mockSession?.persona ?? null,
      officerWorkMode: mockSession?.officerWorkMode ?? null,
      hasPermission,
      login,
      logout,
      refreshSession,
      refreshUser,
      patchUser,
      setOfficerWorkMode,
    }),
    [
      status,
      user,
      permissions,
      roles,
      forcePasswordChange,
      mockSession,
      hasPermission,
      login,
      logout,
      refreshSession,
      refreshUser,
      patchUser,
      setOfficerWorkMode,
    ],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
