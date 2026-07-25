"use client";

import { Suspense } from "react";
import { ComplaintListView } from "@/features/complaints";
import { PageContainer, PageHeader, Skeleton } from "@/shared/ui";

function ListFallback() {
  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title="Complaints"
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Complaints" },
        ]}
      />
      <Skeleton rows={6} />
    </PageContainer>
  );
}

export default function ComplaintsPage() {
  return (
    <Suspense fallback={<ListFallback />}>
      <ComplaintListView />
    </Suspense>
  );
}
