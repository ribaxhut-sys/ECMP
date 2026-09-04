import { Suspense } from "react";
import { ClosedArchiveListView } from "@/features/complaints";
import { PageFallback } from "@/shared/ui";

/** Ditutup — successful-close archive. Not the Pengaduan work list. */
export default function DitutupPage() {
  return (
    <Suspense fallback={<PageFallback titleKey="closed" />}>
      <ClosedArchiveListView />
    </Suspense>
  );
}
