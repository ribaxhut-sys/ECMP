import {
  Empty,
  PageContainer,
  PageHeader,
} from "@/shared/ui";

export default function SettingsPage() {
  return (
    <PageContainer>
      <PageHeader
        title="Settings"
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Settings" },
        ]}
        description="Application settings placeholder for future configuration screens."
      />
      <Empty
        title="Settings"
        description="Placeholder route. Theme and preference controls will land in a later sprint."
      />
    </PageContainer>
  );
}
