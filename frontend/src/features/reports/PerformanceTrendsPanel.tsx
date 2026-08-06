"use client";

import { useTranslations } from "next-intl";
import {
  Card,
  CardBody,
  CardHeader,
  Empty,
  PanelHeader,
  SectionHeader,
  Skeleton,
} from "@/shared/ui";

export function PerformanceTrendsPanel({
  loading,
  onRefresh,
}: {
  loading: boolean;
  onRefresh?: () => void;
}) {
  const t = useTranslations("reports");

  return (
    <section
      className="space-y-[var(--ecmp-panel-gap)]"
      aria-label={t("performance")}
    >
      <SectionHeader
        title={t("performance")}
        description={t("performanceDescription")}
      />
      {loading ? (
        <Skeleton rows={3} />
      ) : (
        <Card>
          <CardHeader>
            <PanelHeader
              title={t("trend")}
              description={t("performanceDescription")}
              className="mb-0 border-0 pb-0"
            />
          </CardHeader>
          <CardBody>
            <Empty
              title={t("trendUnavailable")}
              description={t("trendUnavailableDescription")}
              primaryAction={
                onRefresh
                  ? { label: t("refreshReport"), onClick: onRefresh }
                  : undefined
              }
            />
          </CardBody>
        </Card>
      )}
    </section>
  );
}
