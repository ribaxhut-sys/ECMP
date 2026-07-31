import { ReportsView } from "@/features/reports";
import {
  PageContainer,
  PageHeader,
} from "@/shared/ui";

export default function ReportsPage() {
  return (
    <PageContainer>
      <PageHeader
        title="Reports"
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Reports" },
        ]}
        description="Complaint summary, status breakdown, and branch distribution."
      />
      <ReportsView />
    </PageContainer>
  );
}
