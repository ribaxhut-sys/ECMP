import {
  Empty,
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
        description="User administration UI will be built on this foundation."
      />
      <Empty
        title="Users module"
        description="Placeholder route for future user management screens."
      />
    </PageContainer>
  );
}
