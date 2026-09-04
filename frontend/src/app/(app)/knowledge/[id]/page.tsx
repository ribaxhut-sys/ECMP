"use client";

import { Suspense, use } from "react";
import { KnowledgeDetailView } from "@/features/knowledge";
import { PageContainer, Skeleton } from "@/shared/ui";

export default function KnowledgeDetailPage({
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
      <KnowledgeDetailView id={id} />
    </Suspense>
  );
}
