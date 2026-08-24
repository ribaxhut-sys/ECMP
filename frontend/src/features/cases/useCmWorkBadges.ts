"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import { fetchCmWorkBadges } from "@/lib/api";

/**
 * Sidebar work counts for Mode A: Cabang unread Cases + Pusat unclaimed queue.
 * Refetches on route change so opening a Case (mark-read) updates the badge.
 * Fail-open: a fetch error never blocks navigation — counts hide.
 */
export function useCmWorkBadges(): { unreadCases: number; pusatQueue: number } {
  const pathname = usePathname();
  const { hasPermission } = useAuth();
  const canRead = hasPermission("complaints:read");
  const [unreadCases, setUnreadCases] = useState(0);
  const [pusatQueue, setPusatQueue] = useState(0);

  useEffect(() => {
    if (!canRead) {
      setUnreadCases(0);
      setPusatQueue(0);
      return;
    }
    let cancelled = false;
    fetchCmWorkBadges()
      .then((res) => {
        if (cancelled) return;
        const unread =
          typeof res.data?.unreadCases === "number" && res.data.unreadCases > 0
            ? res.data.unreadCases
            : 0;
        const queue =
          typeof res.data?.pusatQueue === "number" && res.data.pusatQueue > 0
            ? res.data.pusatQueue
            : 0;
        setUnreadCases(unread);
        setPusatQueue(queue);
      })
      .catch(() => {
        if (!cancelled) {
          setUnreadCases(0);
          setPusatQueue(0);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [canRead, pathname]);

  return { unreadCases, pusatQueue };
}
