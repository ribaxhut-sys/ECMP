"use client";

import { useTranslations } from "next-intl";
import type { KpiSummary } from "@/lib/api/types";
import {
  Card,
  CardBody,
  CardHeader,
  Empty,
  PanelHeader,
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
    <div className="rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface-sunken px-[var(--ecmp-panel-gap)] py-[var(--ecmp-panel-gap)]">
      <p className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
        {label}
      </p>
      <p className="mt-2 text-[length:var(--ecmp-font-page-title-size)] font-[number:var(--ecmp-font-page-title-weight)] tabular-nums text-ecmp-text-primary">
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
    <div className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] sm:grid-cols-3">
      <div className="flex items-center text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary sm:col-span-1">
        {label}
      </div>
      <MetricTile label={completedLabel} value={completed} />
      <MetricTile label={breachedLabel} value={breached} />
    </div>
  );
}

export function KpiSummaryCard({
  summary,
  loading,
}: {
  summary: KpiSummary | null;
  loading: boolean;
}) {
  const t = useTranslations("kpi");
  const td = useTranslations("dashboard");

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <PanelHeader title={t("title")} className="mb-0 border-0 pb-0" />
        </CardHeader>
        <CardBody>
          <Skeleton rows={4} />
        </CardBody>
      </Card>
    );
  }

  if (!summary) {
    return (
      <Card>
        <CardHeader>
          <PanelHeader title={t("title")} className="mb-0 border-0 pb-0" />
        </CardHeader>
        <CardBody>
          <Empty
            title={t("noData")}
            description={t("noDataDescription")}
          />
        </CardBody>
      </Card>
    );
  }

  const stages = [
    { label: td("stageAssignment"), ...summary.assignment },
    { label: td("stageAppointment"), ...summary.appointment },
    { label: td("stageResolution"), ...summary.resolution },
    { label: td("stageEscalation"), ...summary.escalation },
    { label: td("stageOverall"), ...summary.overall },
  ];

  return (
    <Card data-testid="kpi-summary-card">
      <CardHeader>
        <PanelHeader title={t("title")} className="mb-0 border-0 pb-0" />
      </CardHeader>
      <CardBody className="space-y-[var(--ecmp-panel-gap)]">
        <div>
          <p className="mb-[var(--ecmp-form-gap)] text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
            {t("complaintsSectionLabel")}
          </p>
          <div className="grid grid-cols-1 gap-[var(--ecmp-card-gap)] sm:grid-cols-3">
            <MetricTile label={td("totalComplaints")} value={summary.complaints.total} />
            <MetricTile label={t("open")} value={summary.complaints.open} />
            <MetricTile label={t("closed")} value={summary.complaints.closed} />
          </div>
        </div>

        <div className="space-y-[var(--ecmp-panel-gap)]">
          <p className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
            {t("slaSectionLabel")}
          </p>
          {stages.map((stage) => (
            <StageRow
              key={stage.label}
              label={stage.label}
              completed={stage.completed}
              breached={stage.breached}
              completedLabel={td("completed")}
              breachedLabel={td("breached")}
            />
          ))}
        </div>
      </CardBody>
    </Card>
  );
}
