import { Suspense } from "react";
import { DashboardView } from "@/features/dashboard/DashboardView";
import { PageContainer, PageHeader, Skeleton } from "@/shared/ui";

function DashboardFallback() {
  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title="Dashboard"
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Dashboard" },
        ]}
      />
      <Skeleton rows={6} />
    </PageContainer>
  );
}

export default function DashboardPage() {
  return (
    <Suspense fallback={<DashboardFallback />}>
      <DashboardView />
    </Suspense>
  );
}
