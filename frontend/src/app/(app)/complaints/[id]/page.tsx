"use client";

import { Suspense, use } from "react";
import { useTranslations } from "next-intl";
import { ComplaintDetailView } from "@/features/complaints";
import { PageContainer, PageHeader, Skeleton } from "@/shared/ui";

function DetailFallback() {
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");

  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title={t("title")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title"), href: "/complaints" },
          { label: t("detailTitle") },
        ]}
      />
      <Skeleton rows={6} />
    </PageContainer>
  );
}

export default function ComplaintDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  return (
    <Suspense fallback={<DetailFallback />}>
      <ComplaintDetailView complaintId={id} />
    </Suspense>
  );
}
