import { SystemSettingsManagement } from "@/features/settings";
import { SlaPolicyManagement } from "@/features/sla";
import {
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
        description="Administration and configuration for ECMP complaint operations."
      />
      <div style={{ display: "grid", gap: "1.5rem" }}>
        <SystemSettingsManagement />
        <SlaPolicyManagement />
      </div>
    </PageContainer>
  );
}
