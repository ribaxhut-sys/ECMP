import { Suspense } from "react";
import { DashboardView } from "@/features/dashboard/DashboardView";
import { PageFallback } from "@/shared/ui";

export default function DashboardPage() {
  return (
    <Suspense fallback={<PageFallback titleKey="dashboard" />}>
      <DashboardView />
    </Suspense>
  );
}
