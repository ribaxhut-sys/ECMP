"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import {
  AddCaseToComplaintView,
  CreateComplaintView,
} from "@/features/complaints";
import { isAddCaseMode } from "@/features/complaints/addCaseToComplaint";
import { PageContainer, PageHeader, Skeleton } from "@/shared/ui";

function NewComplaintFallback() {
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={t("create")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title"), href: "/complaints" },
          { label: tCommon("create") },
        ]}
      />
      <Skeleton rows={5} />
    </PageContainer>
  );
}

function NewComplaintRouter() {
  const searchParams = useSearchParams();
  const mode = searchParams.get("mode");
  const complaintId = searchParams.get("complaintId")?.trim() ?? "";
  if (isAddCaseMode(mode)) {
    return <AddCaseToComplaintView complaintId={complaintId} />;
  }
  return <CreateComplaintView />;
}

export default function CreateComplaintPage() {
  return (
    <Suspense fallback={<NewComplaintFallback />}>
      <NewComplaintRouter />
    </Suspense>
  );
}
