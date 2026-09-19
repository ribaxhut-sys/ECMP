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
import { useAuth } from "@/auth/AuthProvider";
import {
  DEFAULT_NAV_PREFERENCE_STATE,
  navPreferenceStorageKey,
  parseNavPreference,
  serializeNavPreference,
  type NavPreferenceMode,
  type NavPreferenceState,
} from "./navPreference";

interface NavPreferenceContextValue extends NavPreferenceState {
  setMode: (mode: NavPreferenceMode) => void;
  /** Persisted only in "remember" mode; "auto" toggles stay in-visit. */
  setSubgroupExpanded: (subgroupId: string, expanded: boolean) => void;
  /** False until localStorage has been read (SSR-safe first paint). */
  ready: boolean;
}

const NavPreferenceContext = createContext<NavPreferenceContextValue | null>(null);

function readStored(key: string): string | null {
  if (typeof window === "undefined") return null;
  try {
    return window.localStorage.getItem(key);
  } catch {
    return null;
  }
}

function writeStored(key: string, value: string): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(key, value);
  } catch {
    /* ignore quota / private mode — preference is best-effort */
  }
}

/**
 * Personal navigation preference. Mounted inside AuthProvider so the storage
 * key can be scoped to the signed-in user; falls back to an anonymous key
 * before the session resolves.
 */
export function NavPreferenceProvider({ children }: { children: ReactNode }) {
  const { userId } = useAuth();
  const storageKey = navPreferenceStorageKey(userId);
  const [state, setState] = useState<NavPreferenceState>(
    DEFAULT_NAV_PREFERENCE_STATE,
  );
  const [ready, setReady] = useState(false);

  // Re-read whenever the identity (and therefore the key) changes.
  useEffect(() => {
    setState(parseNavPreference(readStored(storageKey)));
    setReady(true);
  }, [storageKey]);

  const persist = useCallback(
    (updater: (prev: NavPreferenceState) => NavPreferenceState) => {
      setState((prev) => {
        const next = updater(prev);
        writeStored(storageKey, serializeNavPreference(next));
        return next;
      });
    },
    [storageKey],
  );

  const setMode = useCallback(
    (mode: NavPreferenceMode) => {
      persist((prev) => (prev.mode === mode ? prev : { ...prev, mode }));
    },
    [persist],
  );

  const setSubgroupExpanded = useCallback(
    (subgroupId: string, expanded: boolean) => {
      persist((prev) => ({
        ...prev,
        expanded: { ...prev.expanded, [subgroupId]: expanded },
      }));
    },
    [persist],
  );

  const value = useMemo(
    () => ({
      mode: state.mode,
      expanded: state.expanded,
      setMode,
      setSubgroupExpanded,
      ready,
    }),
    [state.mode, state.expanded, setMode, setSubgroupExpanded, ready],
  );

  return (
    <NavPreferenceContext.Provider value={value}>
      {children}
    </NavPreferenceContext.Provider>
  );
}

/**
 * Preference accessor. Returns the safe defaults outside a provider so a
 * missing/failed provider can never crash the sidebar (§10 fallback).
 */
export function useNavPreference(): NavPreferenceContextValue {
  const ctx = useContext(NavPreferenceContext);
  if (ctx) return ctx;
  return {
    ...DEFAULT_NAV_PREFERENCE_STATE,
    setMode: () => {},
    setSubgroupExpanded: () => {},
    ready: false,
  };
}
