"use client";

import { useTranslations } from "next-intl";
import type { DashboardSlaSummary } from "@/lib/api/types";
import {
  Card,
  CardBody,
  CardHeader,
  Empty,
  SectionHeader,
  Skeleton,
  StatCard,
} from "@/shared/ui";

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
    <div className="grid grid-cols-1 gap-[var(--ecmp-card-gap)] sm:grid-cols-3 sm:items-stretch">
      <div className="flex items-center text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary sm:col-span-1">
        {label}
      </div>
      <StatCard
        title={completedLabel}
        value={<span className="tabular-nums">{completed}</span>}
        statusTone="success"
      />
      <StatCard
        title={breachedLabel}
        value={<span className="tabular-nums">{breached}</span>}
        variant={breached > 0 ? "emphasis" : "default"}
        statusTone={breached > 0 ? "danger" : "neutral"}
      />
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
          <SectionHeader title={t("slaSummaryTitle")} />
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
          <SectionHeader title={t("slaSummaryTitle")} />
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
        <SectionHeader title={t("slaSummaryTitle")} />
      </CardHeader>
      <CardBody className="space-y-[var(--ecmp-panel-gap)]">
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
