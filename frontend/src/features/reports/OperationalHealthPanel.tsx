"use client";

import { useMemo } from "react";
import { useTranslations } from "next-intl";
import type { ReportSummary } from "@/lib/api/types";
import { cn } from "@/shared/utils";
import {
  Card,
  CardBody,
  CardHeader,
  Empty,
  PanelHeader,
  ProgressMeter,
  SectionHeader,
  Skeleton,
} from "@/shared/ui";
import {
  operationalHealthFromRate,
  reportHeadlineCounts,
  resolutionRatePercent,
} from "./reportSummaryStats";

export function OperationalHealthPanel({
  summary,
  loading,
}: {
  summary: ReportSummary | null;
  loading: boolean;
}) {
  const t = useTranslations("reports");
  const health = useMemo(() => {
    const headlines = reportHeadlineCounts(summary);
    return operationalHealthFromRate(resolutionRatePercent(headlines));
  }, [summary]);

  return (
    <section
      className="space-y-[var(--ecmp-panel-gap)]"
      aria-label={t("operationalHealth")}
    >
      <SectionHeader
        title={t("operationalHealth")}
        description={t("operationalHealthDescription")}
      />
      <Card>
        <CardHeader>
          <PanelHeader
            title={t("healthMeter")}
            description={t("healthMeterDescription")}
            className="mb-0 border-0 pb-0"
          />
        </CardHeader>
        <CardBody className="space-y-[var(--ecmp-panel-gap)]">
          {loading ? (
            <Skeleton rows={3} />
          ) : !health ? (
            <Empty
              title={t("noHealthData")}
              description={t("noHealthDataDescription")}
            />
          ) : (
            <>
              <div className="flex flex-wrap items-end justify-between gap-3">
                <div>
                  <p className="text-[length:var(--ecmp-font-caption-size)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                    {t("currentStatus")}
                  </p>
                  <p className="mt-1 text-[length:var(--ecmp-font-page-title-size)] font-[number:var(--ecmp-font-page-title-weight)] text-ecmp-text-primary">
                    {t(health.labelKey)}
                  </p>
                  <p className="mt-1 text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                    {t("healthStory")}
                  </p>
                </div>
                <p
                  className={cn(
                    "tabular-nums text-[length:var(--ecmp-font-display-size)] font-[number:var(--ecmp-font-page-title-weight)] leading-none",
                    health.tone === "healthy" && "text-ecmp-success-text",
                    health.tone === "attention" && "text-ecmp-warning-text",
                    health.tone === "critical" && "text-ecmp-danger-text",
                  )}
                >
                  {health.score}%
                </p>
              </div>
              <ProgressMeter
                label={t("resolutionRate")}
                value={health.score}
                tone={health.tone}
              />
              <ul
                className="grid grid-cols-1 gap-[var(--ecmp-card-gap)] sm:grid-cols-3"
                aria-label={t("healthLegend")}
              >
                <li className="rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-success-subtle/40 px-3 py-2">
                  <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-success-text">
                    {t("healthy")}
                  </p>
                  <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                    {t("healthyThreshold")}
                  </p>
                </li>
                <li className="rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-warning-subtle/40 px-3 py-2">
                  <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-warning-text">
                    {t("attention")}
                  </p>
                  <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                    {t("attentionThreshold")}
                  </p>
                </li>
                <li className="rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-danger-subtle/40 px-3 py-2">
                  <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-danger-text">
                    {t("critical")}
                  </p>
                  <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                    {t("criticalThreshold")}
                  </p>
                </li>
              </ul>
            </>
          )}
        </CardBody>
      </Card>
    </section>
  );
}
