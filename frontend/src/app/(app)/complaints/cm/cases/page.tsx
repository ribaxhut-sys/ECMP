"use client";

import { Suspense } from "react";
import { CaseInboxListView } from "@/features/cases";
import { PageFallback } from "@/shared/ui";

export default function CmCaseInboxPage() {
  return (
    <Suspense fallback={<PageFallback titleKey="cases" />}>
      <CaseInboxListView />
    </Suspense>
  );
}
