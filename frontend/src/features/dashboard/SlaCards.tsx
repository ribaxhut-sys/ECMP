"use client";

import { useTranslations } from "next-intl";
import type { DashboardSlaSummary } from "@/lib/api/types";
import {
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  Empty,
  Skeleton,
} from "@/shared/ui";

function MetricTile({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-background px-4 py-4">
      <p className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary">
        {label}
      </p>
      <p className="mt-2 text-[length:var(--ecmp-font-heading-size)] font-semibold tabular-nums text-ecmp-text-primary">
        {value}
      </p>
    </div>
  );
}

function StageRow({
  label,
  completed,
  breached,
  completedLabel,
  breachedLabel,
}: {
  label: string;
  completed: number;
  breached: number;
  completedLabel: string;
  breachedLabel: string;
}) {
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
      <div className="flex items-center text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary sm:col-span-1">
        {label}
      </div>
      <MetricTile label={completedLabel} value={completed} />
      <MetricTile label={breachedLabel} value={breached} />
    </div>
  );
}

export function SlaCards({
  sla,
  loading,
}: {
  sla: DashboardSlaSummary | null;
  loading: boolean;
}) {
  const t = useTranslations("dashboard");

  if (loading) {
    return (
      <Card data-testid="dashboard-sla-cards">
        <CardHeader>
          <CardTitle>{t("slaSummaryTitle")}</CardTitle>
        </CardHeader>
        <CardBody>
          <Skeleton rows={4} />
        </CardBody>
      </Card>
    );
  }

  if (!sla) {
    return (
      <Card data-testid="dashboard-sla-cards">
        <CardHeader>
          <CardTitle>{t("slaSummaryTitle")}</CardTitle>
        </CardHeader>
        <CardBody>
          <Empty
            title={t("noSlaData")}
            description={t("noSlaDataDescription")}
          />
        </CardBody>
      </Card>
    );
  }

  const stages = [
    { label: t("stageAssignment"), ...sla.assignment },
    { label: t("stageAppointment"), ...sla.appointment },
    { label: t("stageResolution"), ...sla.resolution },
    { label: t("stageEscalation"), ...sla.escalation },
    { label: t("stageOverall"), ...sla.overall },
  ];

  return (
    <Card data-testid="dashboard-sla-cards">
      <CardHeader>
        <CardTitle>{t("slaSummaryTitle")}</CardTitle>
      </CardHeader>
      <CardBody className="space-y-4">
        {stages.map((stage) => (
          <StageRow
            key={stage.label}
            label={stage.label}
            completed={stage.completed}
            breached={stage.breached}
            completedLabel={t("completed")}
            breachedLabel={t("breached")}
          />
        ))}
      </CardBody>
    </Card>
  );
}
