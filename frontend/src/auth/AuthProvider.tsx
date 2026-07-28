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

type AuthStatus = "loading" | "authenticated" | "unauthenticated";

interface AuthContextValue {
  status: AuthStatus;
  user: AuthMe | null;
  userId: string | null;
  permissions: readonly string[];
  roles: readonly string[];
  forcePasswordChange: boolean;
  hasPermission: (permission: string) => boolean;
  login: (username: string, password: string) => Promise<AuthMe>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<boolean>;
  refreshUser: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>("loading");
  const [user, setUser] = useState<AuthMe | null>(null);

  const applyUser = useCallback((next: AuthMe | null) => {
    setUser(next);
    setStatus(next ? "authenticated" : "unauthenticated");
  }, []);

  const loadMe = useCallback(async (): Promise<AuthMe | null> => {
    try {
      const me = await fetchCurrentUser();
      applyUser(me);
      return me;
    } catch {
      setAuthToken(null);
      applyUser(null);
      return null;
    }
  }, [applyUser]);

  const refreshSession = useCallback(async (): Promise<boolean> => {
    const tokens = await refreshAccessToken();
    if (!tokens) {
      applyUser(null);
      return false;
    }
    const me = await loadMe();
    return me != null;
  }, [applyUser, loadMe]);

  const refreshUser = useCallback(async (): Promise<boolean> => {
    const me = await loadMe();
    return me != null;
  }, [loadMe]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
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
  }, [applyUser, loadMe]);

  const login = useCallback(
    async (username: string, password: string) => {
      await apiLogin(username, password);
      const me = await loadMe();
      if (!me) {
        throw new Error("Failed to load user profile");
      }
      return me;
    },
    [loadMe],
  );

  const logout = useCallback(async () => {
    await apiLogout();
    applyUser(null);
  }, [applyUser]);

  const permissions = user?.permissions ?? [];
  const roles = user?.roles ?? [];
  const forcePasswordChange = Boolean(user?.forcePasswordChange);

  const hasPermission = useCallback(
    (permission: string) =>
      permissions.includes("*") || permissions.includes(permission),
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
      hasPermission,
      login,
      logout,
      refreshSession,
      refreshUser,
    }),
    [
      status,
      user,
      permissions,
      roles,
      forcePasswordChange,
      hasPermission,
      login,
      logout,
      refreshSession,
      refreshUser,
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
