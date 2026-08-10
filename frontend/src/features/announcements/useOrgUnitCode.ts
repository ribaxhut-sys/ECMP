"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/auth/AuthProvider";
import { fetchBranches } from "@/lib/api";

/**
 * Resolve the caller's org/unit code for AuthZ mirrors (announcement manage).
 * - ``undefined`` — still loading (or unauthenticated)
 * - ``null`` — authenticated with no branch (typical Admin Pusat)
 * - ``string`` — branch catalog code (e.g. PUSAT, UPPPD-…)
 */
export function useOrgUnitCode(): string | null | undefined {
  const { user, status } = useAuth();
  const [orgUnitCode, setOrgUnitCode] = useState<string | null | undefined>(
    undefined,
  );

  useEffect(() => {
    if (status !== "authenticated" || !user) {
      setOrgUnitCode(undefined);
      return;
    }
    const branchId = user.branchId?.trim() || null;
    if (!branchId) {
      setOrgUnitCode(null);
      return;
    }
    let cancelled = false;
    void fetchBranches(100)
      .then((res) => {
        if (cancelled) return;
        const match = res.data.find((branch) => branch.id === branchId);
        setOrgUnitCode(match?.code ?? null);
      })
      .catch(() => {
        if (!cancelled) setOrgUnitCode(null);
      });
    return () => {
      cancelled = true;
    };
  }, [status, user]);

  return orgUnitCode;
}
