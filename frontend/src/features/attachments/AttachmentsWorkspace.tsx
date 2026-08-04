"use client";

import { useMemo } from "react";
import { useTranslations } from "next-intl";
import { useRouter, useSearchParams } from "next/navigation";
import { AttachmentList } from "@/features/attachments";
import {
  PageContainer,
  PageHeader,
  WorkspaceToolbar,
} from "@/shared/ui";

function parseIds(raw: string | null): string[] {
  if (!raw) return [];
  return raw
    .split(/[\s,]+/)
    .map((part) => part.trim())
    .filter(Boolean);
}

export function AttachmentsWorkspace() {
  const t = useTranslations("attachments");
  const tCommon = useTranslations("common");
  const tTable = useTranslations("table");
  const router = useRouter();
  const searchParams = useSearchParams();
  const idsFromQuery = useMemo(
    () => parseIds(searchParams.get("ids")),
    [searchParams],
  );

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={t("title")}
        breadcrumbs={[
          { label: t("home"), href: "/dashboard" },
          { label: t("title") },
        ]}
        description={t("workspaceDescription")}
      />

      {idsFromQuery.length > 0 ? (
        <WorkspaceToolbar
          summary={tTable("itemsInView", { count: idsFromQuery.length })}
        />
      ) : null}

      <AttachmentList
        attachmentIds={idsFromQuery}
        emptyTitle={t("noItems")}
        emptyDescription={t("noItemsDescription")}
        emptyPrimaryAction={{
          label: tCommon("goToComplaints"),
          onClick: () => router.push("/complaints"),
        }}
      />
    </PageContainer>
  );
}
