"use client";

import { Suspense, use } from "react";
import { useTranslations } from "next-intl";
import { CmBatch1ConfirmationView } from "@/features/complaints";
import { PageContainer, PageHeader, Skeleton } from "@/shared/ui";

function ConfirmationFallback() {
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");

  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title={t("registeredTitle")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title"), href: "/complaints" },
          { label: t("confirmation") },
        ]}
      />
      <Skeleton rows={5} />
    </PageContainer>
  );
}

export default function CmBatch1ConfirmationPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  return (
    <Suspense fallback={<ConfirmationFallback />}>
      <CmBatch1ConfirmationView complaintId={id} />
    </Suspense>
  );
}
