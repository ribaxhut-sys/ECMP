"use client";

import { Suspense } from "react";
import { CmBatch1SupervisorQueueView } from "@/features/complaints";
import { PageFallback } from "@/shared/ui";

export default function CmBatch1SupervisorQueuePage() {
  return (
    <Suspense fallback={<PageFallback titleKey="complaints" />}>
      <CmBatch1SupervisorQueueView />
    </Suspense>
  );
}
