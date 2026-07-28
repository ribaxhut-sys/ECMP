import { UserManagement } from "@/features/users";
import {
  PageContainer,
  PageHeader,
} from "@/shared/ui";

export default function UsersPage() {
  return (
    <PageContainer>
      <PageHeader
        title="Users"
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Users" },
        ]}
        description="Administer ECMP users, including one-time password reset (API-413)."
      />
      <UserManagement />
    </PageContainer>
  );
}
