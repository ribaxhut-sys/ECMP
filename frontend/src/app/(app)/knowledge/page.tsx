"use client";

import { useTranslations } from "next-intl";
import { IconFile } from "@/shared/icons";
import { Empty, PageContainer, PageHeader } from "@/shared/ui";

/**
 * Pengetahuan — placeholder only for this milestone (§16, LOCKED). No
 * editor, article management, search, or AI retrieval — that is a separate
 * milestone.
 */
export default function KnowledgePage() {
  const t = useTranslations("knowledgePage");
  const tCommon = useTranslations("common");

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={t("title")}
        description={t("description")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title") },
        ]}
      />
      <Empty
        icon={<IconFile className="size-8" aria-hidden />}
        title={t("emptyTitle")}
        description={t("emptyDescription")}
      />
    </PageContainer>
  );
}
