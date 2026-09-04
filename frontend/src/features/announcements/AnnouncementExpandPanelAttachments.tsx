"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { downloadAttachment } from "@/lib/api";
import type { AnnouncementAttachment } from "@/lib/api/types";
import { fileTypeLabel, formatFileSize } from "@/features/attachments/fileTypes";
import { IconFile, IconPaperclip } from "@/shared/icons";
import { useToast } from "@/shared/providers";
import { cn } from "@/shared/utils";

async function downloadAndSave(id: string, filename: string) {
  const result = await downloadAttachment(id);
  const url = URL.createObjectURL(result.blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = result.filename || filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

/** Compact attachment rows for the management list expand panel. */
export function AnnouncementExpandPanelAttachments({
  attachments,
  attachmentCount,
}: {
  attachments: AnnouncementAttachment[];
  attachmentCount: number;
}) {
  const t = useTranslations("announcements");
  const { pushError } = useToast();
  const [busyId, setBusyId] = useState<string | null>(null);
  const items = attachments ?? [];
  const count = Math.max(attachmentCount, items.length);

  async function onDownload(att: AnnouncementAttachment) {
    setBusyId(att.id);
    try {
      await downloadAndSave(att.id, att.fileName);
    } catch (err) {
      pushError(err, t("actionFailed"));
    } finally {
      setBusyId(null);
    }
  }

  return (
    <section className="space-y-2" aria-label={t("attachmentsSectionTitle")}>
      <h4 className="flex items-center gap-1.5 text-[length:var(--ecmp-font-helper-size)] font-medium text-ecmp-text-primary">
        <IconPaperclip className="size-3.5 shrink-0 text-ecmp-text-secondary" aria-hidden />
        {t("attachmentsSectionTitle")}
        {count > 0 ? (
          <span className="font-normal text-ecmp-text-secondary">({count})</span>
        ) : null}
      </h4>
      {items.length === 0 ? (
        <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
          {t("listAttachmentCount", { count: 0 })}
        </p>
      ) : (
        <ul className="space-y-1.5">
          {items.map((att) => {
            const typeLabel = fileTypeLabel(att.mimeType, null, att.fileName);
            const busy = busyId === att.id;
            return (
              <li key={att.id}>
                <button
                  type="button"
                  disabled={busy}
                  onClick={() => void onDownload(att)}
                  className={cn(
                    "ecmp-touch flex w-full items-center gap-2 rounded-[var(--ecmp-radius-md)]",
                    "border border-ecmp-border bg-ecmp-surface px-2.5 py-2 text-left",
                    "hover:bg-ecmp-hover",
                    "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-primary",
                    "disabled:opacity-60",
                  )}
                >
                  <span
                    className="inline-flex min-w-[2.75rem] shrink-0 items-center justify-center rounded-[var(--ecmp-radius-badge)] bg-ecmp-surface-sunken px-1.5 py-0.5 text-[length:var(--ecmp-font-caption-size)] font-medium tabular-nums text-ecmp-text-secondary"
                    aria-hidden
                  >
                    {typeLabel}
                  </span>
                  <IconFile
                    className="size-4 shrink-0 text-ecmp-text-secondary"
                    aria-hidden
                  />
                  <span className="min-w-0 flex-1 truncate text-[length:var(--ecmp-font-body-small-size)] font-medium text-ecmp-primary underline-offset-2 hover:underline">
                    {att.fileName}
                  </span>
                  <span className="shrink-0 text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
                    {formatFileSize(att.sizeBytes)}
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
