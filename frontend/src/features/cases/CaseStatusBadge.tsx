"use client";

import { Badge } from "@/shared/ui";
import { useTranslations } from "next-intl";
import type { CmCaseStatus } from "@/lib/api/cmCase";
import { caseStatusTone } from "./caseStatus";

export function CaseStatusBadge({ status }: { status: CmCaseStatus | string }) {
  const t = useTranslations("status");
  const key = status.toUpperCase();
  const label = t.has(key as "IN_PROGRESS") ? t(key as "IN_PROGRESS") : status;
  return <Badge tone={caseStatusTone(status)}>{label}</Badge>;
}
