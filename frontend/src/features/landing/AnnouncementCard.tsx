"use client";

import { useId, useState } from "react";
import { useTranslations } from "next-intl";
import { downloadAttachment } from "@/lib/api";
import type { Announcement } from "@/lib/api/types";
import { AnnouncementPriorityBadge } from "@/features/announcements";
import { formatDate } from "@/i18n/formatting";
import { IconPaperclip } from "@/shared/icons";
import { useLocaleContext } from "@/shared/i18n";
import { Card, CardBody } from "@/shared/ui";
import { cn } from "@/shared/utils";
import { summarize } from "./announcementSummary";

/** Best-effort save-as — mirrors AttachmentCard's download handler, kept
 * minimal here since the landing card only needs a plain link, not the full
 * preview/viewer UI (that lives on the announcement detail page). */
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

export function AnnouncementCard({
  announcement,
  featured = false,
}: {
  announcement: Announcement;
  /** Pengumuman terbaru — hierarki visual lebih kuat. */
  featured?: boolean;
}) {
  const t = useTranslations("landing");
  const { locale } = useLocaleContext();
  const [expanded, setExpanded] = useState(false);
  const bodyId = useId();

  const published = announcement.publishedAt
    ? formatDate(announcement.publishedAt, locale, {
        day: "numeric",
        month: "long",
        year: "numeric",
      })
    : null;

  return (
    <Card
      className={cn(
        featured &&
          "border-ecmp-primary/30 bg-ecmp-primary-muted/25 shadow-ecmp-raised",
      )}
    >
      <CardBody className="space-y-2">
        <div className="flex flex-wrap items-center gap-2">
          <AnnouncementPriorityBadge priority={announcement.priority} />
          {published ? (
            <time
              dateTime={announcement.publishedAt ?? undefined}
              className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-muted"
            >
              {published}
            </time>
          ) : null}
        </div>

        <h3
          className={cn(
            "font-[number:var(--ecmp-font-card-title-weight)] leading-snug tracking-tight text-ecmp-text-primary",
            featured
              ? "text-[length:var(--ecmp-font-section-title-size)]"
              : "text-[length:var(--ecmp-font-card-title-size)]",
          )}
        >
          {announcement.title}
        </h3>

        <p
          hidden={expanded}
          className={cn(
            "leading-relaxed text-ecmp-text-secondary",
            featured
              ? "text-[length:var(--ecmp-font-body-size)]"
              : "text-[length:var(--ecmp-font-body-small-size)]",
          )}
        >
          {summarize(announcement.body)}
        </p>

        {!expanded && announcement.attachmentCount > 0 ? (
          <p className="flex items-center gap-1.5 text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
            <IconPaperclip className="size-3.5 shrink-0" aria-hidden />
            {t("attachmentCount", { count: announcement.attachmentCount })}
          </p>
        ) : null}

        <div id={bodyId} hidden={!expanded} className="space-y-3">
          <p className="whitespace-pre-line text-[length:var(--ecmp-font-body-small-size)] leading-relaxed text-ecmp-text-primary">
            {announcement.body}
          </p>
          {announcement.attachments.length > 0 ? (
            <ul className="space-y-1.5">
              {announcement.attachments.map((attachment) => (
                <li key={attachment.id}>
                  <button
                    type="button"
                    onClick={() =>
                      void downloadAndSave(attachment.id, attachment.fileName)
                    }
                    className={cn(
                      "ecmp-touch inline-flex items-center gap-1.5 rounded-[var(--ecmp-radius-md)]",
                      "text-[length:var(--ecmp-font-body-small-size)] text-ecmp-primary",
                      "underline-offset-2 hover:underline",
                      "focus-visible:outline-none focus-visible:ring-[length:var(--ecmp-focus-ring-width)] focus-visible:ring-ecmp-focus",
                    )}
                  >
                    <IconPaperclip className="size-3.5 shrink-0" aria-hidden />
                    {attachment.fileName}
                  </button>
                </li>
              ))}
            </ul>
          ) : null}
        </div>

        {/* Buka di tempat — bukan modal/popup, dan tanpa route detail baru. */}
        <button
          type="button"
          aria-expanded={expanded}
          aria-controls={bodyId}
          onClick={() => setExpanded((open) => !open)}
          className={cn(
            "ecmp-touch inline-flex items-center rounded-[var(--ecmp-radius-md)] text-left",
            "text-[length:var(--ecmp-font-body-small-size)] font-medium text-ecmp-primary",
            "underline-offset-2 hover:underline",
            "focus-visible:outline-none focus-visible:ring-[length:var(--ecmp-focus-ring-width)] focus-visible:ring-ecmp-focus",
          )}
        >
          {expanded ? t("readLess") : t("readMore")}
        </button>
      </CardBody>
    </Card>
  );
}
