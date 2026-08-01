"use client";

import { Badge } from "@/shared/ui";
import type { CmCaseStatus } from "@/lib/api/cmCase";
import { caseStatusTone } from "./caseStatus";

export function CaseStatusBadge({ status }: { status: CmCaseStatus | string }) {
  return <Badge tone={caseStatusTone(status)}>{status}</Badge>;
}
