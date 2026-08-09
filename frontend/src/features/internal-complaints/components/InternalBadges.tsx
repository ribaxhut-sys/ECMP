"use client";

import { useTranslations } from "next-intl";
import { Badge } from "@/shared/ui";
import {
  CATEGORY_LABEL_KEY,
  PRIORITY_TONE,
  STATUS_LABEL_KEY,
  STATUS_TONE,
  type InternalCategory,
  type InternalPriority,
  type InternalStatus,
} from "../types";

export function InternalStatusBadge({ status }: { status: string }) {
  const t = useTranslations("internalComplaints");
  const key = status as InternalStatus;
  const labelKey = STATUS_LABEL_KEY[key];
  const tone = STATUS_TONE[key] ?? "neutral";
  return (
    <Badge tone={tone}>{labelKey ? t(labelKey) : status}</Badge>
  );
}

export function InternalPriorityBadge({ priority }: { priority: string }) {
  const tPriority = useTranslations("priority");
  const tone = PRIORITY_TONE[priority as InternalPriority] ?? "neutral";
  return <Badge tone={tone}>{tPriority(priority as InternalPriority)}</Badge>;
}

export function InternalCategoryBadge({ category }: { category: string }) {
  const t = useTranslations("internalComplaints");
  const key = CATEGORY_LABEL_KEY[category as InternalCategory];
  return <Badge tone="neutral">{key ? t(key) : category}</Badge>;
}
