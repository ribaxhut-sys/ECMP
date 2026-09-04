"use client";

import { Suspense } from "react";
import { HqScheduleView } from "@/features/hq-schedule";
import { PageFallback } from "@/shared/ui";

/**
 * Jadwal Kedatangan Pusat — readable by any complaints:read holder (Cabang +
 * Pusat). Holiday write and per-complaint pending proposals stay permission /
 * HQ-review gated inside the view.
 */
export default function HqSchedulePage() {
  return (
    <Suspense fallback={<PageFallback titleKey="hqSchedule" />}>
      <HqScheduleView />
    </Suspense>
  );
}
