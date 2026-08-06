"use client";

import { useTranslations } from "next-intl";
import { Badge, Card, CardBody, CardHeader } from "@/shared/ui";
import { submitCompleteness } from "@/features/supervisor-assign/mock/assignmentRepository";
import type { MockEvidenceItem } from "@/features/supervisor-assign/mock/assignmentRepository";

export interface EvidenceChecklistProps {
  resolutionSummary: string;
  evidenceItems: readonly MockEvidenceItem[];
}

/** Side panel — “bukti cukup?” checklist (SCR-WS-05, conditionally visible). */
export function EvidenceChecklist({
  resolutionSummary,
  evidenceItems,
}: EvidenceChecklistProps) {
  const t = useTranslations("submitReview");
  const items = submitCompleteness({ resolutionSummary, evidenceItems });
  const ready = items.every((item) => item.filled);

  return (
    <Card>
      <CardHeader>
        <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
          {t("checklistTitle")}
        </h2>
        <p className="mt-1 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
          {ready ? t("checklistReady") : t("checklistIncomplete")}
        </p>
      </CardHeader>
      <CardBody>
        <ul className="space-y-2">
          {items.map((item) => (
            <li
              key={item.key}
              className="flex items-center justify-between gap-2 rounded-[var(--ecmp-radius-md)] border border-ecmp-border/60 px-3 py-2"
            >
              <span className="text-ecmp-text-primary">
                {t(`checklist.${item.key}`)}
              </span>
              <Badge
                tone={item.filled ? "success" : "neutral"}
                variant="outline"
              >
                {item.filled ? t("checklistFilled") : t("checklistMissing")}
              </Badge>
            </li>
          ))}
        </ul>
      </CardBody>
    </Card>
  );
}
