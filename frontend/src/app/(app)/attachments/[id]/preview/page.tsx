"use client";

import { Suspense, use } from "react";
import { AttachmentPreviewView } from "@/features/attachments/AttachmentPreviewView";
import { PageContainer, Skeleton } from "@/shared/ui";

export default function AttachmentPreviewPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  return (
    <Suspense
      fallback={
        <PageContainer>
          <Skeleton rows={8} />
        </PageContainer>
      }
    >
      <AttachmentPreviewView id={id} />
    </Suspense>
  );
}
