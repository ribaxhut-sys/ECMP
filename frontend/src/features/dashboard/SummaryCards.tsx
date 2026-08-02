"use client";

import { useTranslations } from "next-intl";
import type { DashboardHeader } from "@/lib/api/types";
import {
  Card,
  CardBody,
  CardHeader,
  Empty,
  SectionHeader,
  Skeleton,
  StatCard,
} from "@/shared/ui";

export function SummaryCards({
  header,
  loading,
}: {
  header: DashboardHeader | null;
  loading: boolean;
}) {
  const t = useTranslations("dashboard");

  if (loading) {
    return (
      <Card data-testid="dashboard-header-cards">
        <CardHeader>
          <SectionHeader title={t("summary")} />
        </CardHeader>
        <CardBody>
          <Skeleton rows={2} />
        </CardBody>
      </Card>
    );
  }

  if (!header) {
    return (
      <Card data-testid="dashboard-header-cards">
        <CardHeader>
          <SectionHeader title={t("summary")} />
        </CardHeader>
        <CardBody>
          <Empty
            title={t("noSummaryYet")}
            description={t("noSummaryDescription")}
          />
        </CardBody>
      </Card>
    );
  }

  const cards = [
    { label: t("totalComplaints"), value: header.totalComplaints },
    { label: t("openComplaints"), value: header.openComplaints },
    { label: t("closedComplaints"), value: header.closedComplaints },
  ];

  return (
    <section
      data-testid="dashboard-header-cards"
      className="space-y-[var(--ecmp-panel-gap)]"
      aria-label={t("summary")}
    >
      <SectionHeader title={t("summary")} />
      <div className="grid grid-cols-1 gap-[var(--ecmp-card-gap)] sm:grid-cols-3">
        {cards.map((card) => (
          <StatCard
            key={card.label}
            title={card.label}
            value={
              <span className="tabular-nums">{card.value}</span>
            }
          />
        ))}
      </div>
    </section>
  );
}
