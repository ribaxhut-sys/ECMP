"use client";

import { Suspense } from "react";
import { AssignmentListView } from "@/features/assignments";
import { PageContainer, PageHeader, Skeleton } from "@/shared/ui";

function AssignmentsFallback() {
  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title="Assignments"
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Assignments" },
        ]}
      />
      <Skeleton rows={6} />
    </PageContainer>
  );
}

export default function AssignmentsPage() {
  return (
    <Suspense fallback={<AssignmentsFallback />}>
      <AssignmentListView />
    </Suspense>
  );
}
