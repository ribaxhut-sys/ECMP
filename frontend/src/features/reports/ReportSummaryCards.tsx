"use client";

import { useTranslations } from "next-intl";
import type { ReportSummary } from "@/lib/api/types";
import {
  Empty,
  SectionHeader,
  Skeleton,
  StatCard,
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
      <section
        data-testid="reports-summary-cards"
        className="space-y-[var(--ecmp-panel-gap)]"
        aria-label={t("summaryTitle")}
      >
        <SectionHeader title={t("summaryTitle")} />
        <Skeleton rows={2} />
      </section>
    );
  }

  const headlines = reportHeadlineCounts(summary);
  if (!headlines) {
    return (
      <section
        data-testid="reports-summary-cards"
        className="space-y-[var(--ecmp-panel-gap)]"
        aria-label={t("summaryTitle")}
      >
        <SectionHeader title={t("summaryTitle")} />
        <Empty
          title={t("noSummary")}
          description={t("noSummaryDescription")}
        />
      </section>
    );
  }

  const cards = [
    { label: t("totalComplaints"), value: headlines.total },
    { label: t("openComplaints"), value: headlines.open },
    { label: t("closedComplaints"), value: headlines.closed },
  ];

  return (
    <section
      data-testid="reports-summary-cards"
      className="space-y-[var(--ecmp-panel-gap)]"
      aria-label={t("summaryTitle")}
    >
      <SectionHeader title={t("summaryTitle")} />
      <div className="grid grid-cols-1 gap-[var(--ecmp-card-gap)] sm:grid-cols-3">
        {cards.map((card) => (
          <StatCard
            key={card.label}
            title={card.label}
            value={<span className="tabular-nums">{card.value}</span>}
          />
        ))}
      </div>
    </section>
  );
}
