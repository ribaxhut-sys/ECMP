"use client";

import { useCallback, useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import { fetchCmWorkBadges } from "@/lib/api";
import { WORK_BADGES_REFRESH_EVENT } from "./workBadgesSignal";

/**
 * Sidebar work counts for Mode A: Cabang unread Cases + Pusat unopened queue.
 * Refetches on route change and on the refresh signal a detail view fires once
 * it has loaded (the read receipt is written by that same request).
 * Fail-open: a fetch error never blocks navigation — counts hide.
 */
export function useCmWorkBadges(): {
  unreadCases: number;
  pusatQueue: number;
  pusatFollowUp: number;
} {
  const pathname = usePathname();
  const { hasPermission } = useAuth();
  const canRead = hasPermission("complaints:read");
  const [unreadCases, setUnreadCases] = useState(0);
  const [pusatQueue, setPusatQueue] = useState(0);
  const [pusatFollowUp, setPusatFollowUp] = useState(0);

  const load = useCallback(
    (isCancelled: () => boolean) => {
      if (!canRead) {
        setUnreadCases(0);
        setPusatQueue(0);
        setPusatFollowUp(0);
        return;
      }
      fetchCmWorkBadges()
        .then((res) => {
          if (isCancelled()) return;
          const unread =
            typeof res.data?.unreadCases === "number" && res.data.unreadCases > 0
              ? res.data.unreadCases
              : 0;
          const queue =
            typeof res.data?.pusatQueue === "number" && res.data.pusatQueue > 0
              ? res.data.pusatQueue
              : 0;
          const followUp =
            typeof res.data?.pusatFollowUp === "number" &&
            res.data.pusatFollowUp > 0
              ? res.data.pusatFollowUp
              : 0;
          setUnreadCases(unread);
          setPusatQueue(queue);
          setPusatFollowUp(followUp);
        })
        .catch(() => {
          if (isCancelled()) return;
          setUnreadCases(0);
          setPusatQueue(0);
          setPusatFollowUp(0);
        });
    },
    [canRead],
  );

  useEffect(() => {
    let cancelled = false;
    const isCancelled = () => cancelled;
    load(isCancelled);
    const onRefresh = () => load(isCancelled);
    window.addEventListener(WORK_BADGES_REFRESH_EVENT, onRefresh);
    return () => {
      cancelled = true;
      window.removeEventListener(WORK_BADGES_REFRESH_EVENT, onRefresh);
    };
  }, [load, pathname]);

  return { unreadCases, pusatQueue, pusatFollowUp };
}
