"use client";

import { useTranslations } from "next-intl";
import type { CycleTimeSummary } from "@/lib/api/types";
import {
  Card,
  CardBody,
  CardHeader,
  Empty,
  PanelHeader,
  SectionHeader,
  Skeleton,
  StatCard,
} from "@/shared/ui";
import { cycleTimeBucketRows } from "./cycleTimeStats";

export function CycleTimePanel({
  summary,
  loading,
}: {
  summary: CycleTimeSummary | null;
  loading: boolean;
}) {
  const t = useTranslations("reports");
  const rows = cycleTimeBucketRows(summary);
  const days = (value: number | null | undefined) =>
    value == null ? "—" : t("daysValue", { days: value });

  return (
    <section
      className="space-y-[var(--ecmp-panel-gap)]"
      aria-label={t("cycleTime")}
    >
      <SectionHeader
        title={t("cycleTime")}
        description={t("cycleTimeDescription")}
      />

      {loading ? (
        <Skeleton rows={3} />
      ) : !summary || summary.closedCases === 0 ? (
        <Empty
          title={t("noCycleTimeData")}
          description={t("noCycleTimeDataDescription")}
        />
      ) : (
        <>
          <div className="grid grid-cols-1 gap-[var(--ecmp-card-gap)] sm:grid-cols-2 xl:grid-cols-4">
            <StatCard
              hierarchy="secondary"
              accent="normal"
              title={t("cycleTimeMedian")}
              value={<span className="tabular-nums">{days(summary.medianDays)}</span>}
              subtitle={t("cycleTimeMedianStory")}
            />
            <StatCard
              hierarchy="secondary"
              accent="normal"
              title={t("cycleTimeAverage")}
              value={<span className="tabular-nums">{days(summary.averageDays)}</span>}
              subtitle={t("cycleTimeAverageStory")}
            />
            <StatCard
              hierarchy="secondary"
              accent="attention"
              title={t("cycleTimeP90")}
              value={<span className="tabular-nums">{days(summary.p90Days)}</span>}
              subtitle={t("cycleTimeP90Story")}
            />
            <StatCard
              hierarchy="secondary"
              accent="normal"
              title={t("cycleTimeClosedCases")}
              value={
                <span className="tabular-nums">{summary.closedCases}</span>
              }
              subtitle={t("cycleTimeClosedCasesStory")}
            />
          </div>

          <Card>
            <CardHeader>
              <PanelHeader
                title={t("cycleTimeDistribution")}
                description={t("cycleTimeDistributionDescription")}
                className="mb-0 border-0 pb-0"
              />
            </CardHeader>
            <CardBody>
              <ul className="space-y-[var(--ecmp-card-gap)]" role="list">
                {rows.map((row) => (
                  <li key={row.key} className="space-y-2">
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                        {t(row.labelKey)}
                      </p>
                      <span className="shrink-0 tabular-nums text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                        {t("cycleTimeBucketValue", {
                          count: row.count,
                          share: row.share,
                        })}
                      </span>
                    </div>
                    <div
                      className="h-3 overflow-hidden rounded-[var(--ecmp-radius-full)] bg-ecmp-secondary-muted"
                      role="meter"
                      aria-valuenow={row.share}
                      aria-valuemin={0}
                      aria-valuemax={100}
                      aria-label={t(row.labelKey)}
                    >
                      <div
                        className="h-full rounded-[var(--ecmp-radius-full)] bg-ecmp-info transition-[width] duration-[var(--ecmp-duration-normal)] ease-[var(--ecmp-ease-hover)]"
                        style={{ width: `${row.share}%` }}
                      />
                    </div>
                  </li>
                ))}
              </ul>
            </CardBody>
          </Card>
        </>
      )}
    </section>
  );
}
