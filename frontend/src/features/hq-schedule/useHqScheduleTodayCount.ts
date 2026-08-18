"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import { useOrgUnitCode } from "@/features/announcements/useOrgUnitCode";
import { canCmBatch1HqReview } from "@/features/complaints/cmBatch1HqActions";
import { fetchHqScheduleAvailabilityDetail } from "@/lib/api/hqSchedule";
import { toLocalDateKey } from "@/shared/utils/datetime";

/**
 * Total HQ arrivals scheduled today, for the Pusat sidebar reminder badge.
 * Branch (Cabang) callers never see this — reuses the same HQ-review gate
 * as the detail schedule endpoint. Fail-open: a fetch error just hides the
 * badge instead of blocking navigation.
 */
export function useHqScheduleTodayCount(): number {
  const pathname = usePathname();
  const { hasPermission, roles } = useAuth();
  const unitCode = useOrgUnitCode();
  const canSeeDetail = canCmBatch1HqReview({ roles, hasPermission, unitCode });
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (!canSeeDetail) {
      setCount(0);
      return;
    }
    let cancelled = false;
    const today = toLocalDateKey(new Date());
    fetchHqScheduleAvailabilityDetail(today, today)
      .then((res) => {
        if (cancelled) return;
        const day = res.data.days[0];
        const total = (day?.slots ?? []).reduce(
          (sum, slot) => sum + slot.scheduledCount,
          0,
        );
        setCount(total);
      })
      .catch(() => {
        if (!cancelled) setCount(0);
      });
    return () => {
      cancelled = true;
    };
  }, [canSeeDetail, pathname]);

  return count;
}
