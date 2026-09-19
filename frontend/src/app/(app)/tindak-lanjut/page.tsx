"use client";

import { Suspense } from "react";
import { FollowUpListView } from "@/features/complaints";
import { PageFallback } from "@/shared/ui";

/**
 * Tindak lanjut — Case-only work list, FE composition over API-514 /
 * API-536. See followUpRows.ts for filter/sort rules.
 */
export default function TindakLanjutPage() {
  return (
    <Suspense fallback={<PageFallback titleKey="followUp" />}>
      <FollowUpListView />
    </Suspense>
  );
}
