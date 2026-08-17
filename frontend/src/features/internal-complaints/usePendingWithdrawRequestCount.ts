"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import { isInternalComplaintsUiEnabled } from "@/shared/config/internalComplaintsUi";
import { fetchPendingWithdrawRequestCount } from "@/lib/api/internalComplaints";

/**
 * Sidebar badge — pending branch withdraw requests (after Pusat received).
 * Fail-open: a fetch error never blocks navigation.
 */
export function usePendingWithdrawRequestCount(): number {
  const pathname = usePathname();
  const { hasPermission } = useAuth();
  const canRead = isInternalComplaintsUiEnabled() && hasPermission("complaints:read");
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (!canRead) {
      setCount(0);
      return;
    }
    let cancelled = false;
    fetchPendingWithdrawRequestCount()
      .then((res) => {
        if (cancelled) return;
        const next = typeof res.data === "number" && res.data > 0 ? res.data : 0;
        setCount(next);
      })
      .catch(() => {
        if (!cancelled) setCount(0);
      });
    return () => {
      cancelled = true;
    };
  }, [canRead, pathname]);

  return count;
}
