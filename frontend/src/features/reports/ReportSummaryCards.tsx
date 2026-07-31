"use client";

import { useTranslations } from "next-intl";
import type { ReportSummary } from "@/lib/api/types";
import {
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  Empty,
  Skeleton,
} from "@/shared/ui";
import { reportHeadlineCounts } from "./reportSummaryStats";

export function ReportSummaryCards({
  summary,
  loading,
}: {
  summary: ReportSummary | null;
  loading: boolean;
}) {
  const t = useTranslations("reports");

  if (loading) {
    return (
      <Card data-testid="reports-summary-cards">
        <CardHeader>
          <CardTitle>{t("summaryTitle")}</CardTitle>
        </CardHeader>
        <CardBody>
          <Skeleton rows={2} />
        </CardBody>
      </Card>
    );
  }

  const headlines = reportHeadlineCounts(summary);
  if (!headlines) {
    return (
      <Card data-testid="reports-summary-cards">
        <CardHeader>
          <CardTitle>{t("summaryTitle")}</CardTitle>
        </CardHeader>
        <CardBody>
          <Empty
            title={t("noSummary")}
            description={t("noSummaryDescription")}
          />
        </CardBody>
      </Card>
    );
  }

  const cards = [
    { label: t("totalComplaints"), value: headlines.total },
    { label: t("openComplaints"), value: headlines.open },
    { label: t("closedComplaints"), value: headlines.closed },
  ];

  return (
    <Card data-testid="reports-summary-cards">
      <CardHeader>
        <CardTitle>{t("summaryTitle")}</CardTitle>
      </CardHeader>
      <CardBody>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          {cards.map((card) => (
            <div
              key={card.label}
              className="rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-background px-4 py-4"
            >
              <p className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary">
                {card.label}
              </p>
              <p className="mt-2 text-[length:var(--ecmp-font-heading-size)] font-semibold tabular-nums text-ecmp-text-primary">
                {card.value}
              </p>
            </div>
          ))}
        </div>
      </CardBody>
    </Card>
  );
}
