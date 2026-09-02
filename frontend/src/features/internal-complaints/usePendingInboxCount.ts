"use client";

import { useCallback, useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import { fetchPendingInboxCount } from "@/lib/api/internalComplaints";
import { isInternalComplaintsUiEnabled } from "@/shared/config/internalComplaintsUi";
import { INTERNAL_INBOX_BADGES_REFRESH_EVENT } from "./inboxBadgesSignal";

/**
 * Sidebar badge — incoming Pengaduan Internal awaiting receive at this unit.
 * Cabang and Pusat both use the same endpoint (API-551); the server scopes
 * handling-unit. Fail-open: a fetch error never blocks navigation.
 */
export function usePendingInboxCount(): number {
  const pathname = usePathname();
  const { hasPermission } = useAuth();
  const canRead =
    isInternalComplaintsUiEnabled() && hasPermission("complaints:read");
  const [count, setCount] = useState(0);

  const load = useCallback(
    (isCancelled: () => boolean) => {
      if (!canRead) {
        setCount(0);
        return;
      }
      fetchPendingInboxCount()
        .then((res) => {
          if (isCancelled()) return;
          const next = typeof res.data === "number" && res.data > 0 ? res.data : 0;
          setCount(next);
        })
        .catch(() => {
          if (!isCancelled()) setCount(0);
        });
    },
    [canRead],
  );

  useEffect(() => {
    let cancelled = false;
    const isCancelled = () => cancelled;
    load(isCancelled);
    const onRefresh = () => load(isCancelled);
    window.addEventListener(INTERNAL_INBOX_BADGES_REFRESH_EVENT, onRefresh);
    return () => {
      cancelled = true;
      window.removeEventListener(INTERNAL_INBOX_BADGES_REFRESH_EVENT, onRefresh);
    };
  }, [load, pathname]);

  return count;
}
