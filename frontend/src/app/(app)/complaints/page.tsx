"use client";

import { Suspense } from "react";
import { ComplaintListView } from "@/features/complaints";
import { PageFallback } from "@/shared/ui";

export default function ComplaintsPage() {
  return (
    <Suspense fallback={<PageFallback titleKey="complaints" />}>
      <ComplaintListView />
    </Suspense>
  );
}
