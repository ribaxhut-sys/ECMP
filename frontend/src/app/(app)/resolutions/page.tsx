"use client";

import { Suspense } from "react";
import { ResolutionListView } from "@/features/resolutions";
import { PageContainer, PageHeader, Skeleton } from "@/shared/ui";

function ResolutionsFallback() {
  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title="Resolutions"
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Resolutions" },
        ]}
      />
      <Skeleton rows={6} />
    </PageContainer>
  );
}

export default function ResolutionsPage() {
  return (
    <Suspense fallback={<ResolutionsFallback />}>
      <ResolutionListView />
    </Suspense>
  );
}
