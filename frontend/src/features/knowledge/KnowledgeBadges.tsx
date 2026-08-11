"use client";

import { useTranslations } from "next-intl";
import { Badge, type BadgeTone } from "@/shared/ui";
import type { KnowledgeStatus, KnowledgeType } from "@/lib/api/types";

const statusTone: Record<KnowledgeStatus, BadgeTone> = {
  DRAFT: "neutral",
  ACTIVE: "success",
  ARCHIVED: "neutral",
};

function statusKey(status: KnowledgeStatus): string {
  switch (status) {
    case "ACTIVE":
      return "statusActive";
    case "ARCHIVED":
      return "statusArchived";
    default:
      return "statusDraft";
  }
}

export function KnowledgeStatusBadge({ status }: { status: KnowledgeStatus }) {
  const t = useTranslations("knowledge");
  return <Badge tone={statusTone[status]}>{t(statusKey(status))}</Badge>;
}

export function knowledgeTypeKey(
  type: KnowledgeType,
):
  | "typeSop"
  | "typePeraturan"
  | "typeSuratEdaran"
  | "typeKeputusan"
  | "typePanduan" {
  switch (type) {
    case "PERATURAN":
      return "typePeraturan";
    case "SURAT_EDARAN":
      return "typeSuratEdaran";
    case "KEPUTUSAN":
      return "typeKeputusan";
    case "PANDUAN":
      return "typePanduan";
    default:
      return "typeSop";
  }
}

export function KnowledgeTypeBadge({ type }: { type: KnowledgeType }) {
  const t = useTranslations("knowledge");
  return <Badge tone="info">{t(knowledgeTypeKey(type))}</Badge>;
}
