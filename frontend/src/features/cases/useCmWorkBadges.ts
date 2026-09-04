"use client";

import { useCallback, useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import { fetchCmWorkBadges } from "@/lib/api";
import { WORK_BADGES_REFRESH_EVENT } from "./workBadgesSignal";

/**
 * Sidebar work counts for Mode A: Cabang unread Cases + Pusat unopened queue.
 * Same receiver pattern as Internal (two engines, one UX): kirim / kirim ulang
 * raises the badge on the receiving login.
 * Refetch on route change, the same-tab refresh signal, tab focus, and a
 * quiet poll so the other login sees escalate / return / resend without
 * navigating.
 * Fail-open: a fetch error never blocks navigation — counts hide.
 */
export const WORK_BADGES_POLL_MS = 60_000;

export function useCmWorkBadges(): {
  unreadCases: number;
  pusatQueue: number;
  pusatFollowUp: number;
  hqScheduleUnread: number;
} {
  const pathname = usePathname();
  const { hasPermission } = useAuth();
  const canRead = hasPermission("complaints:read");
  const [unreadCases, setUnreadCases] = useState(0);
  const [pusatQueue, setPusatQueue] = useState(0);
  const [pusatFollowUp, setPusatFollowUp] = useState(0);
  const [hqScheduleUnread, setHqScheduleUnread] = useState(0);

  const load = useCallback(
    (isCancelled: () => boolean) => {
      if (!canRead) {
        setUnreadCases(0);
        setPusatQueue(0);
        setPusatFollowUp(0);
        setHqScheduleUnread(0);
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
          const hqSchedule =
            typeof res.data?.hqScheduleUnread === "number" &&
            res.data.hqScheduleUnread > 0
              ? res.data.hqScheduleUnread
              : 0;
          setUnreadCases(unread);
          setPusatQueue(queue);
          setPusatFollowUp(followUp);
          setHqScheduleUnread(hqSchedule);
        })
        .catch(() => {
          if (isCancelled()) return;
          setUnreadCases(0);
          setPusatQueue(0);
          setPusatFollowUp(0);
          setHqScheduleUnread(0);
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
    window.addEventListener(WORK_BADGES_REFRESH_EVENT, onRefresh);
    document.addEventListener("visibilitychange", onVisible);
    const pollId = window.setInterval(() => {
      if (document.visibilityState !== "visible") return;
      load(isCancelled);
    }, WORK_BADGES_POLL_MS);
    return () => {
      cancelled = true;
      window.removeEventListener(WORK_BADGES_REFRESH_EVENT, onRefresh);
      document.removeEventListener("visibilitychange", onVisible);
      window.clearInterval(pollId);
    };
  }, [load, pathname]);

  return { unreadCases, pusatQueue, pusatFollowUp, hqScheduleUnread };
}
