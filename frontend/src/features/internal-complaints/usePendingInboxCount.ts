"use client";

import { useCallback, useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import { fetchPendingInboxCount } from "@/lib/api/internalComplaints";
import { isInternalComplaintsUiEnabled } from "@/shared/config/internalComplaintsUi";
import { INTERNAL_INBOX_BADGES_REFRESH_EVENT } from "./inboxBadgesSignal";

/** Background poll so the receiving unit sees create / return / resend. */
export const INTERNAL_INBOX_BADGE_POLL_MS = 60_000;

/**
 * Sidebar badge — work waiting on this unit (API-551).
 * Cabang: incoming, owner usulan hidup, close-gate.
 * Pusat: incoming, rebound after tolak/kembalikan, withdraw, close-gate.
 * Fail-open: a fetch error never blocks navigation.
 *
 * Refetch on route change, the same-tab refresh signal, tab focus, and a
 * quiet poll so the other login sees kirim / kembalikan / kirim ulang /
 * usulan without navigating.
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
    const onVisible = () => {
      if (document.visibilityState === "visible") load(isCancelled);
    };
    window.addEventListener(INTERNAL_INBOX_BADGES_REFRESH_EVENT, onRefresh);
    document.addEventListener("visibilitychange", onVisible);
    const pollId = window.setInterval(() => {
      if (document.visibilityState !== "visible") return;
      load(isCancelled);
    }, INTERNAL_INBOX_BADGE_POLL_MS);
    return () => {
      cancelled = true;
      window.removeEventListener(INTERNAL_INBOX_BADGES_REFRESH_EVENT, onRefresh);
      document.removeEventListener("visibilitychange", onVisible);
      window.clearInterval(pollId);
    };
  }, [load, pathname]);

  return count;
}
