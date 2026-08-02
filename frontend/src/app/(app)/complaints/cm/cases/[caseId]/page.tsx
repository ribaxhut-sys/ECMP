"use client";

import { Suspense, use } from "react";
import { useTranslations } from "next-intl";
import { CaseDetailView } from "@/features/cases";
import { PageContainer, PageHeader, Skeleton } from "@/shared/ui";

function CaseDetailFallback() {
  const tCases = useTranslations("cases");
  const tCommon = useTranslations("common");
  const tNav = useTranslations("nav");
  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={tCases("title")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: tNav("complaints"), href: "/complaints" },
          { label: tCases("title") },
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
