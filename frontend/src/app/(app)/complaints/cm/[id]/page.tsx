"use client";

import { Suspense, use } from "react";
import { CmBatch1ConfirmationView } from "@/features/complaints";
import { PageContainer, PageHeader, Skeleton } from "@/shared/ui";

function ConfirmationFallback() {
  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title="Complaint registered"
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Complaints", href: "/complaints" },
          { label: "Confirmation" },
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
