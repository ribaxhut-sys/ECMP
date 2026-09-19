"use client";

import { useTranslations } from "next-intl";
import { Badge, type BadgeTone } from "@/shared/ui";
import type {
  AnnouncementEffectiveStatus,
  AnnouncementPriority,
} from "@/lib/api/types";

const statusTone: Record<AnnouncementEffectiveStatus, BadgeTone> = {
  DRAFT: "neutral",
  PUBLISHED: "success",
  ARCHIVED: "neutral",
  EXPIRED: "warning",
  SCHEDULED: "info",
};

function statusKey(status: AnnouncementEffectiveStatus): string {
  switch (status) {
    case "PUBLISHED":
      return "statusPublished";
    case "ARCHIVED":
      return "statusArchived";
    case "EXPIRED":
      return "statusExpired";
    case "SCHEDULED":
      return "statusScheduled";
    default:
      return "statusDraft";
  }
}

export function AnnouncementStatusBadge({
  status,
}: {
  status: AnnouncementEffectiveStatus;
}) {
  const t = useTranslations("announcements");
  return <Badge tone={statusTone[status]}>{t(statusKey(status))}</Badge>;
}

function priorityKey(priority: AnnouncementPriority): string {
  return priority === "IMPORTANT" ? "priorityImportant" : "priorityNormal";
}

export function AnnouncementPriorityBadge({
  priority,
}: {
  priority: AnnouncementPriority;
}) {
  const t = useTranslations("announcements");
  if (priority !== "IMPORTANT") return null;
  return <Badge tone="danger">{t(priorityKey(priority))}</Badge>;
}
