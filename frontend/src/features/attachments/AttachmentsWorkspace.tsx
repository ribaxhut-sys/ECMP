"use client";

import type { FormEvent } from "react";
import { useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import { useRouter, useSearchParams } from "next/navigation";
import { AttachmentList } from "@/features/attachments";
import {
  Button,
  FilterBar,
  Input,
  PageContainer,
  PageHeader,
  SectionHeader,
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
  const router = useRouter();
  const searchParams = useSearchParams();
  const idsFromQuery = useMemo(
    () => parseIds(searchParams.get("ids")),
    [searchParams],
  );
  const [draft, setDraft] = useState(idsFromQuery.join(", "));

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    const ids = parseIds(draft);
    const next = new URLSearchParams();
    if (ids.length > 0) {
      next.set("ids", ids.join(","));
    }
    const qs = next.toString();
    router.push(qs ? `/attachments?${qs}` : "/attachments");
  };

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

      <section className="space-y-[var(--ecmp-panel-gap)]" aria-label={t("loadByIdTitle")}>
        <SectionHeader
          title={t("loadByIdTitle")}
          description={
            <>
              {t("apiHintPrefix")}{" "}
              <code className="rounded bg-ecmp-secondary-muted px-1">
                GET /api/v1/attachments/&#123;id&#125;
              </code>{" "}
              {t("apiHintJoin")}{" "}
              <code className="rounded bg-ecmp-secondary-muted px-1">
                GET /api/v1/attachments/&#123;id&#125;/download
              </code>
              . {t("noListEndpointNote")}
            </>
          }
        />
        <form onSubmit={onSubmit}>
          <FilterBar
            search={
              <Input
                id="attachment-ids"
                name="ids"
                label={t("attachmentUuidsLabel")}
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                placeholder={t("idsPlaceholder")}
                autoComplete="off"
              />
            }
            actions={
              <Button type="submit" variant="primary">
                {t("load")}
              </Button>
            }
          />
        </form>
      </section>

      <AttachmentList
        attachmentIds={idsFromQuery}
        emptyTitle={t("noAttachmentIds")}
        emptyDescription={t("noAttachmentIdsDescription")}
      />
    </PageContainer>
  );
}
