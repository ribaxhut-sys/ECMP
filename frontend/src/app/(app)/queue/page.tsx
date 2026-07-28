"use client";

import { Suspense } from "react";
import { QueueDashboardView } from "@/features/queue";
import { PageFallback } from "@/shared/ui";

export default function QueuePage() {
  return (
    <Suspense fallback={<PageFallback titleKey="queue" />}>
      <QueueDashboardView />
    </Suspense>
  );
}
