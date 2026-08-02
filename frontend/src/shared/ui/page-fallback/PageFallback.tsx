"use client";

import { useTranslations } from "next-intl";
import { PageContainer, PageHeader, Skeleton } from "@/shared/ui";

/** Suspense fallback with localized title / Home breadcrumb. */
export function PageFallback({
  titleKey,
  namespace = "nav",
  rows = 6,
}: {
  /** Key within `namespace` (e.g. "dashboard" under "nav"). */
  titleKey: string;
  namespace?: string;
  rows?: number;
}) {
  const t = useTranslations(namespace);
  const tCommon = useTranslations("common");
  const title = t(titleKey);

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={title}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: title },
        ]}
      />
      <Skeleton rows={rows} />
    </PageContainer>
  );
}
