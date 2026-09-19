"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import { isInternalComplaintsUiEnabled } from "@/shared/config/internalComplaintsUi";
import { fetchPendingTransferRequestCount } from "@/lib/api/internalComplaints";

/**
 * Sidebar badge for the Agent transfer-request gate (Pengaduan Internal).
 * Same visibility as the backend endpoint (DEC-024 UNIT/PUSAT/ALL) — a
 * Supervisor/Manager/Admin sees "Perlu Putusan"; an Agent sees their own
 * unit's queue including requests still awaiting a decision. Fail-open: a
 * fetch error never blocks navigation, the badge just hides (mirrors
 * useUnreadAnnouncementCount).
 */
export function usePendingTransferRequestCount(): number {
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
    fetchPendingTransferRequestCount()
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
