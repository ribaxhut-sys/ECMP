"use client";

import type { FormEvent } from "react";
import { useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import { useRouter, useSearchParams } from "next/navigation";
import { AttachmentList } from "@/features/attachments";
import {
  Button,
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  Input,
  PageContainer,
  PageHeader,
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
    <PageContainer className="space-y-6">
      <PageHeader
        title={t("title")}
        breadcrumbs={[
          { label: t("home"), href: "/dashboard" },
          { label: t("title") },
        ]}
        description={t("workspaceDescription")}
      />

      <Card>
        <CardHeader>
          <CardTitle>{t("loadByIdTitle")}</CardTitle>
        </CardHeader>
        <CardBody>
          <form
            className="flex flex-col gap-3 sm:flex-row sm:items-end"
            onSubmit={onSubmit}
          >
            <div className="min-w-0 flex-1 space-y-1">
              <label
                htmlFor="attachment-ids"
                className="text-[length:var(--ecmp-font-caption-size)] font-medium text-ecmp-text-secondary"
              >{t("attachmentUuidsLabel")}              </label>
              <Input
                id="attachment-ids"
                name="ids"
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                placeholder={t("idsPlaceholder")}
                autoComplete="off"
              />
            </div>
            <Button type="submit" variant="primary">{t("load")}            </Button>
          </form>
          <p className="mt-3 text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
            {t("apiHintPrefix")}{" "}
            <code className="rounded bg-ecmp-secondary-muted px-1">
              GET /api/v1/attachments/&#123;id&#125;
            </code>{" "}
            {t("apiHintJoin")}{" "}
            <code className="rounded bg-ecmp-secondary-muted px-1">
              GET /api/v1/attachments/&#123;id&#125;/download
            </code>
            . {t("noListEndpointNote")}
          </p>
        </CardBody>
      </Card>

      <AttachmentList
        attachmentIds={idsFromQuery}
        emptyTitle={t("noAttachmentIds")}
        emptyDescription={t("noAttachmentIdsDescription")}
      />
    </PageContainer>
  );
}
