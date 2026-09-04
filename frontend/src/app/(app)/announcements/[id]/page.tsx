"use client";

import { Suspense, use } from "react";
import { AnnouncementDetailView } from "@/features/announcements";
import { PageContainer, Skeleton } from "@/shared/ui";

export default function AnnouncementDetailPage({
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
      <AnnouncementDetailView id={id} />
    </Suspense>
  );
}
