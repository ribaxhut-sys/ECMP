"use client";

import { useTranslations } from "next-intl";
import type { Announcement } from "@/lib/api/types";
import { AttachmentCard } from "@/features/attachments/AttachmentCard";
import { Empty } from "@/shared/ui";
import { toAttachmentCardModel } from "./attachmentAdapter";

/** Read-only attachment display for the announcement detail page (§13) —
 * reuses the existing preview/download UI (AttachmentCard) unchanged. */
export function AnnouncementAttachmentList({
  announcement,
}: {
  announcement: Announcement;
}) {
  const t = useTranslations("announcements");

  if (announcement.attachments.length === 0) {
    return <Empty title={t("noAttachments")} description={t("noAttachmentsDescription")} />;
  }

  return (
    <div className="grid grid-cols-1 gap-[var(--ecmp-card-gap)] lg:grid-cols-2">
      {announcement.attachments.map((attachment) => (
        <AttachmentCard
          key={attachment.id}
          attachment={toAttachmentCardModel(attachment, announcement)}
        />
      ))}
    </div>
  );
}
