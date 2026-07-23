import {
  Empty,
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
        description="Reporting views will use the shared design system and App Layout."
      />
      <Empty
        title="Reports module"
        description="Placeholder route for future report screens. No business features in this sprint."
      />
    </PageContainer>
  );
}
