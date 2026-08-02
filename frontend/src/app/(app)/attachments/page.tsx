import { Suspense } from "react";
import { AttachmentsWorkspace } from "@/features/attachments/AttachmentsWorkspace";
import { PageContainer, Skeleton } from "@/shared/ui";

export default function AttachmentsPage() {
  return (
    <Suspense
      fallback={
        <PageContainer className="space-y-[var(--ecmp-panel-gap)]">
          <Skeleton className="h-10 w-64" />
          <Skeleton className="h-40 w-full" />
        </PageContainer>
      }
    >
      <AttachmentsWorkspace />
    </Suspense>
  );
}
