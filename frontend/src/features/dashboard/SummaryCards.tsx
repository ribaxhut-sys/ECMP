import type { ReportSummary } from "@/lib/api/types";
import {
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  Empty,
  Skeleton,
} from "@/shared/ui";

function openCount(summary: ReportSummary): number {
  const open = new Set([
    "NEW",
    "ASSIGNED",
    "IN_PROGRESS",
    "PENDING",
    "ESCALATED",
  ]);
  return summary.byStatus
    .filter((row) => open.has(row.status))
    .reduce((sum, row) => sum + row.count, 0);
}

function statusCount(summary: ReportSummary, status: string): number {
  return summary.byStatus.find((row) => row.status === status)?.count ?? 0;
}

export function SummaryCards({
  summary,
  loading,
}: {
  summary: ReportSummary | null;
  loading: boolean;
}) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Summary</CardTitle>
        </CardHeader>
        <CardBody>
          <Skeleton rows={2} />
        </CardBody>
      </Card>
    );
  }

  if (!summary || summary.total === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Summary</CardTitle>
        </CardHeader>
        <CardBody>
          <Empty
            title="No summary yet"
            description="No complaints yet. Summary will appear once cases are registered."
          />
        </CardBody>
      </Card>
    );
  }

  const cards = [
    { label: "Total", value: summary.total },
    { label: "Open", value: openCount(summary) },
    { label: "Resolved", value: statusCount(summary, "RESOLVED") },
    { label: "Closed", value: statusCount(summary, "CLOSED") },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Summary</CardTitle>
      </CardHeader>
      <CardBody>
        {/* Mobile: 1 col · Tablet: 2 · Desktop: 4 */}
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
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
