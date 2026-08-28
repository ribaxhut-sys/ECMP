"use client";

import { useTranslations } from "next-intl";
import { Card, CardBody } from "@/shared/ui";
import {
  countDelta,
  reportBriefingFacts,
  signedCount,
} from "./reportBriefing";
import type { ReportsData } from "./loadReportsData";

export function ReportBriefing({
  data,
  loading,
}: {
  data: ReportsData | null;
  loading: boolean;
}) {
  const t = useTranslations("reports");
  const facts = reportBriefingFacts(data?.summary, data?.byStatus);
  const previous = reportBriefingFacts(
    data?.previous?.summary,
    data?.previous?.byStatus,
  );
  const closedDelta = countDelta(facts?.closed ?? 0, previous?.closed);

  if (loading) {
    return (
      <Card className="border-ecmp-primary/20 bg-ecmp-primary-muted/30">
        <CardBody>
          <p className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-primary">
            {t("briefingOverline")}
          </p>
          <div
            className="mt-3 h-8 max-w-xl animate-pulse rounded-[var(--ecmp-radius-md)] bg-ecmp-secondary-muted motion-reduce:animate-none"
            aria-hidden
          />
        </CardBody>
      </Card>
    );
  }

  if (!facts || facts.total <= 0) {
    return (
      <Card className="border-ecmp-primary/20 bg-ecmp-primary-muted/30">
        <CardBody>
          <p className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-primary">
            {t("briefingOverline")}
          </p>
          <p className="mt-2 text-[length:var(--ecmp-font-section-title-size)] font-[number:var(--ecmp-font-section-title-weight)] text-ecmp-text-primary">
            {t("briefingEmpty")}
          </p>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card
      className="border-ecmp-primary/20 bg-ecmp-primary-muted/30"
      data-testid="reports-briefing"
    >
      <CardBody>
        <p className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-primary">
          {t("briefingOverline")}
        </p>
        <p className="mt-2 text-[length:var(--ecmp-font-section-title-size)] font-[number:var(--ecmp-font-section-title-weight)] leading-snug text-ecmp-text-primary">
          {t("briefing", {
            closed: facts.closed,
            total: facts.total,
            open: facts.open,
          })}
          {facts.escalated > 0
            ? t("briefingEscalated", { escalated: facts.escalated })
            : null}
          {facts.waiting > 0
            ? t("briefingWaiting", { waiting: facts.waiting })
            : null}
        </p>
        {closedDelta != null ? (
          <p className="mt-2 text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
            {t("vsPreviousDelta", { delta: signedCount(closedDelta) })}{" "}
            {t("vsPreviousClosed")}
          </p>
        ) : null}
      </CardBody>
    </Card>
  );
}
