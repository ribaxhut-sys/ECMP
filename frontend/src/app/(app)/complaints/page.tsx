"use client";

import { useRouter } from "next/navigation";
import {
  Button,
  Empty,
  PageContainer,
  PageHeader,
} from "@/shared/ui";

export default function ComplaintsPage() {
  const router = useRouter();

  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title="Complaints"
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Complaints" },
        ]}
        description="Browse and register customer complaints."
        actions={
          <Button type="button" onClick={() => router.push("/complaints/new")}>
            Create Complaint
          </Button>
        }
      />
      <Empty
        title="Complaint queue"
        description="Use Create Complaint to register a new case. Queue listing ships in a later task."
        action={
          <Button
            type="button"
            variant="outline"
            onClick={() => router.push("/complaints/new")}
          >
            Create Complaint
          </Button>
        }
      />
    </PageContainer>
  );
}
