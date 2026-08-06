"use client";

import { Suspense } from "react";
import { CmBatch1ComplaintListView } from "@/features/complaints";
import { PageFallback } from "@/shared/ui";

/**
 * Mode A primary Pengaduan list = Aggregate (API-514 / DEC-020 coexistence).
 * Detail remains under `/complaints/cm/[id]` to avoid clashing with foundation `[id]`.
 */
export default function ComplaintsPage() {
  return (
    <Suspense fallback={<PageFallback titleKey="complaints" />}>
      <CmBatch1ComplaintListView />
    </Suspense>
  );
}
