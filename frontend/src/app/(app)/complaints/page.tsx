"use client";

import { Suspense } from "react";
import { CmBatch1ComplaintListView } from "@/features/complaints";
import { PageFallback } from "@/shared/ui";

/**
 * Mode A primary Pengaduan list = Aggregate (API-514 / DEC-026 canonical).
 * Detail stays under `/complaints/cm/[id]`. Foundation `/complaints/[id]` redirects.
 */
export default function ComplaintsPage() {
  return (
    <Suspense fallback={<PageFallback titleKey="complaints" />}>
      <CmBatch1ComplaintListView />
    </Suspense>
  );
}
