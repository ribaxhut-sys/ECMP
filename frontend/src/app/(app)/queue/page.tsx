"use client";

import { Suspense } from "react";
import { QueueDashboardView } from "@/features/queue";
import { PageContainer, PageHeader, Skeleton } from "@/shared/ui";

function QueueFallback() {
  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title="Queue"
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Queue" },
        ]}
      />
      <Skeleton rows={6} />
    </PageContainer>
  );
}

export default function QueuePage() {
  return (
    <Suspense fallback={<QueueFallback />}>
      <QueueDashboardView />
    </Suspense>
  );
}
