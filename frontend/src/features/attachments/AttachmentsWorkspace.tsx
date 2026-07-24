"use client";

import type { FormEvent } from "react";
import { useMemo, useState } from "react";
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
        title="Attachments"
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Attachments" },
        ]}
        description="Preview images and PDFs, download files, or open them in a new tab. Bytes are loaded only when you preview or download."
      />

      <Card>
        <CardHeader>
          <CardTitle>Load by attachment ID</CardTitle>
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
              >
                Attachment UUID(s)
              </label>
              <Input
                id="attachment-ids"
                name="ids"
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                placeholder="uuid-1, uuid-2"
                autoComplete="off"
              />
            </div>
            <Button type="submit" variant="primary">
              Load
            </Button>
          </form>
          <p className="mt-3 text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
            Uses existing APIs only:{" "}
            <code className="rounded bg-ecmp-secondary-muted px-1">
              GET /api/v1/attachments/&#123;id&#125;
            </code>{" "}
            and{" "}
            <code className="rounded bg-ecmp-secondary-muted px-1">
              GET /api/v1/attachments/&#123;id&#125;/download
            </code>
            . There is no list-by-object endpoint in this task.
          </p>
        </CardBody>
      </Card>

      <AttachmentList
        attachmentIds={idsFromQuery}
        emptyTitle="No attachment IDs"
        emptyDescription="Enter one or more attachment UUIDs above to load cards for preview and download."
      />
    </PageContainer>
  );
}
