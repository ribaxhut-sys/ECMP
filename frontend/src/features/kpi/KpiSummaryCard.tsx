"use client";

import type { KpiSummary } from "@/lib/api/types";
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
}: {
  label: string;
  completed: number;
  breached: number;
}) {
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
      <div className="flex items-center text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary sm:col-span-1">
        {label}
      </div>
      <MetricTile label="Completed" value={completed} />
      <MetricTile label="Breached" value={breached} />
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
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>KPI Summary</CardTitle>
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
          <CardTitle>KPI Summary</CardTitle>
        </CardHeader>
        <CardBody>
          <Empty
            title="No KPI data"
            description="KPI summary will appear once complaints are registered."
          />
        </CardBody>
      </Card>
    );
  }

  const stages = [
    { label: "Assignment", ...summary.assignment },
    { label: "Appointment", ...summary.appointment },
    { label: "Resolution", ...summary.resolution },
    { label: "Escalation", ...summary.escalation },
    { label: "Overall", ...summary.overall },
  ];

  return (
    <Card data-testid="kpi-summary-card">
      <CardHeader>
        <CardTitle>KPI Summary</CardTitle>
      </CardHeader>
      <CardBody className="space-y-6">
        <div>
          <p className="mb-3 text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary">
            Complaints
          </p>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            <MetricTile label="Total Complaints" value={summary.complaints.total} />
            <MetricTile label="Open" value={summary.complaints.open} />
            <MetricTile label="Closed" value={summary.complaints.closed} />
          </div>
        </div>

        <div className="space-y-4">
          <p className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary">
            SLA
          </p>
          {stages.map((stage) => (
            <StageRow
              key={stage.label}
              label={stage.label}
              completed={stage.completed}
              breached={stage.breached}
            />
          ))}
        </div>
      </CardBody>
    </Card>
  );
}
