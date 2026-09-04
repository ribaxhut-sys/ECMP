"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import { fetchUnreadAnnouncementCount } from "@/lib/api";

/**
 * Live unread-active count for the sidebar bell. Refetches on route change
 * so opening a detail (mark-read) updates the badge when the user returns.
 * Fail-open: a fetch error never blocks navigation — the badge just hides.
 */
export function useUnreadAnnouncementCount(): number {
  const pathname = usePathname();
  const { hasPermission } = useAuth();
  const canRead = hasPermission("announcement:read");
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (!canRead) {
      setCount(0);
      return;
    }
    let cancelled = false;
    fetchUnreadAnnouncementCount()
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
