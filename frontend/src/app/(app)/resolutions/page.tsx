"use client";

import { Suspense } from "react";
import { ResolutionListView } from "@/features/resolutions";
import { PageFallback } from "@/shared/ui";

export default function ResolutionsPage() {
  return (
    <Suspense fallback={<PageFallback titleKey="resolutions" />}>
      <ResolutionListView />
    </Suspense>
  );
}
