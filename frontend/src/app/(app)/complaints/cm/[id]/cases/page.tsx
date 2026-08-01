"use client";

import { Suspense, use } from "react";
import { useTranslations } from "next-intl";
import { CaseListView } from "@/features/cases";
import { PageContainer, PageHeader, Skeleton } from "@/shared/ui";

function CasesFallback() {
  const tCases = useTranslations("cases");
  const tCommon = useTranslations("common");
  const tNav = useTranslations("nav");
  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title={tCases("list")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: tNav("complaints"), href: "/complaints" },
          { label: tCases("list") },
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
