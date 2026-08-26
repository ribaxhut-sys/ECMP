import { Suspense } from "react";
import { redirect } from "next/navigation";
import { CmBatch1ComplaintListView } from "@/features/complaints";
import { closedArchiveRedirectHrefFromRecord } from "@/features/complaints/cmBatch1ListFilters";
import { PageFallback } from "@/shared/ui";

/**
 * Mode A primary Pengaduan list = Aggregate (API-514 / DEC-026 canonical).
 * Detail stays under `/complaints/cm/[id]`. Foundation `/complaints/[id]` redirects.
 * `/complaints?status=CLOSED` bookmarks go to `/ditutup`.
 */
export default async function ComplaintsPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const href = closedArchiveRedirectHrefFromRecord(await searchParams);
  if (href) redirect(href);
  return (
    <Suspense fallback={<PageFallback titleKey="complaints" />}>
      <CmBatch1ComplaintListView />
    </Suspense>
  );
}
