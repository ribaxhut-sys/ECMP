"use client";

import {
  createContext,
  createElement,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { useAuth } from "@/auth/AuthProvider";
import { fetchBranches, type Branch } from "@/lib/api";

type OrgUnitBranchContextValue = {
  provided: boolean;
  branch: Branch | null | undefined;
};

const OrgUnitBranchContext = createContext<OrgUnitBranchContextValue>({
  provided: false,
  branch: undefined,
});

function useFetchOrgUnitBranch(enabled: boolean): Branch | null | undefined {
  const { user, status } = useAuth();
  const [branch, setBranch] = useState<Branch | null | undefined>(undefined);

  useEffect(() => {
    if (!enabled) return;
    if (status !== "authenticated" || !user) {
      setBranch(undefined);
      return;
    }
    const branchId = user.branchId?.trim() || null;
    if (!branchId) {
      setBranch(null);
      return;
    }
    let cancelled = false;
    void fetchBranches(100)
      .then((res) => {
        if (cancelled) return;
        setBranch(res.data.find((b) => b.id === branchId) ?? null);
      })
      .catch(() => {
        if (!cancelled) setBranch(null);
      });
    return () => {
      cancelled = true;
    };
  }, [enabled, status, user]);

  return branch;
}

/**
 * One branch-catalog fetch for the authenticated shell. Sidebar, knowledge,
 * and announcement manage all read this instead of fetching `/branches` again.
 */
export function OrgUnitBranchProvider({ children }: { children: ReactNode }) {
  const branch = useFetchOrgUnitBranch(true);
  return createElement(
    OrgUnitBranchContext.Provider,
    { value: { provided: true, branch } },
    children,
  );
}

/**
 * Resolve the caller's own branch catalog row.
 * - ``undefined`` — still loading (or unauthenticated)
 * - ``null`` — authenticated with no branch (typical Admin Pusat), or not found
 * - ``Branch`` — the matched catalog row (code, name, id)
 *
 * Inside ``OrgUnitBranchProvider`` this is a context read (no extra fetch).
 * Outside the shell (tests, isolated pages) it falls back to one local fetch.
 */
export function useOrgUnitBranch(): Branch | null | undefined {
  const ctx = useContext(OrgUnitBranchContext);
  const fallback = useFetchOrgUnitBranch(!ctx.provided);
  return ctx.provided ? ctx.branch : fallback;
}

/**
 * Resolve the caller's org/unit code for AuthZ mirrors (announcement manage).
 * - ``undefined`` — still loading (or unauthenticated)
 * - ``null`` — authenticated with no branch (typical Admin Pusat)
 * - ``string`` — branch catalog code (e.g. PUSAT, UPPPD-…)
 */
export function useOrgUnitCode(): string | null | undefined {
  const branch = useOrgUnitBranch();
  if (branch === undefined) return undefined;
  return branch?.code ?? null;
}
