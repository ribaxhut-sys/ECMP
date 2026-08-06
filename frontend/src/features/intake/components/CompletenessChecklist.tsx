"use client";

import { useTranslations } from "next-intl";
import { Badge, Card, CardBody, CardHeader } from "@/shared/ui";
import { intakeCompleteness } from "@/features/supervisor-assign/mock/assignmentRepository";

export interface CompletenessChecklistProps {
  customerRef: string;
  subject: string;
  description: string;
  category: string;
  channel: string;
  priority: string;
}

/** Data Completeness checklist — required vs filled (SCR-WS-01). */
export function CompletenessChecklist({
  customerRef,
  subject,
  description,
  category,
  channel,
  priority,
}: CompletenessChecklistProps) {
  const t = useTranslations("intake");
  const items = intakeCompleteness({
    customerRef,
    subject,
    description,
    category,
    channel,
    priority,
  });
  const filledCount = items.filter((item) => item.filled).length;

  return (
    <Card>
      <CardHeader>
        <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
          {t("checklistTitle")}
        </h2>
        <p className="mt-1 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
          {t("checklistProgress", {
            filled: filledCount,
            total: items.length,
          })}
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
