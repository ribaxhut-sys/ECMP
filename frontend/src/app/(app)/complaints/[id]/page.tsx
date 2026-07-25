"use client";

import { Suspense, use } from "react";
import { ComplaintDetailView } from "@/features/complaints";
import { PageContainer, PageHeader, Skeleton } from "@/shared/ui";

function DetailFallback() {
  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title="Complaint"
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Complaints", href: "/complaints" },
          { label: "Complaint Detail" },
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
