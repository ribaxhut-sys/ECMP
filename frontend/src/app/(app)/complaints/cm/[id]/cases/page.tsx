"use client";

import { Suspense, use } from "react";
import { CaseListView } from "@/features/cases";
import { PageContainer, PageHeader, Skeleton } from "@/shared/ui";

function CasesFallback() {
  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title="Cases"
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Complaints", href: "/complaints" },
          { label: "Cases" },
        ]}
      />
      <Skeleton rows={4} />
    </PageContainer>
  );
}

export default function CmCaseListPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  return (
    <Suspense fallback={<CasesFallback />}>
      <CaseListView complaintId={id} />
    </Suspense>
  );
}
