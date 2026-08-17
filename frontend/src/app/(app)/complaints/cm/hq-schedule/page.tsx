"use client";

import { Suspense, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import { canCmBatch1HqReview } from "@/features/complaints/cmBatch1HqActions";
import { useOrgUnitCode } from "@/features/announcements/useOrgUnitCode";
import { HqScheduleView } from "@/features/hq-schedule";
import { PageContainer, PageFallback } from "@/shared/ui";

/**
 * Jadwal Kedatangan Pusat — Pusat-only (mirrors backend require_hq_intake_action,
 * Mode A lab gate). Cabang holders are redirected to the complaint list.
 */
export default function HqSchedulePage() {
  const router = useRouter();
  const { roles, hasPermission, status } = useAuth();
  const orgUnitCode = useOrgUnitCode();

  const ready = status === "authenticated" && orgUnitCode !== undefined;
  const canReview =
    ready &&
    canCmBatch1HqReview({ roles, hasPermission, unitCode: orgUnitCode ?? null });

  useEffect(() => {
    if (!ready) return;
    if (!canReview) {
      router.replace("/complaints/cm");
    }
  }, [ready, canReview, router]);

  if (!ready || !canReview) {
    return (
      <PageContainer>
        <div
          className="h-40 animate-pulse rounded-[var(--ecmp-radius-md)] bg-ecmp-surface-sunken"
          aria-hidden
        />
      </PageContainer>
    );
  }

  return (
    <Suspense fallback={<PageFallback titleKey="hqSchedule" />}>
      <HqScheduleView />
    </Suspense>
  );
}
