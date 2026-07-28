"use client";

import { Suspense } from "react";
import { AssignmentListView } from "@/features/assignments";
import { PageFallback } from "@/shared/ui";

export default function AssignmentsPage() {
  return (
    <Suspense fallback={<PageFallback titleKey="assignments" />}>
      <AssignmentListView />
    </Suspense>
  );
}
