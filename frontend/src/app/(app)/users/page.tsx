import { UsersManagement } from "@/features/users";
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
        description="List accounts and create users with role and optional branch."
      />
      <UsersManagement />
    </PageContainer>
  );
}
