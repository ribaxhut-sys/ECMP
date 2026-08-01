"use client";

import { Suspense, use } from "react";
import { CaseDetailView } from "@/features/cases";
import { PageContainer, PageHeader, Skeleton } from "@/shared/ui";

function CaseDetailFallback() {
  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title="Case"
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Complaints", href: "/complaints" },
          { label: "Case" },
        ]}
      />
      <Skeleton rows={6} />
    </PageContainer>
  );
}

export default function CmCaseDetailPage({
  params,
}: {
  params: Promise<{ caseId: string }>;
}) {
  const { caseId } = use(params);
  return (
    <Suspense fallback={<CaseDetailFallback />}>
      <CaseDetailView caseId={caseId} />
    </Suspense>
  );
}
