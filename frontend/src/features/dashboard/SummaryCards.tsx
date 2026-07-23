import type { ReportSummary } from "@/lib/api/types";
import { EmptyBlock, LoadingBlock, Panel } from "./ui";

function openCount(summary: ReportSummary): number {
  const open = new Set(["NEW", "ASSIGNED", "IN_PROGRESS", "ESCALATED"]);
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
      <Panel title="Summary">
        <LoadingBlock rows={2} />
      </Panel>
    );
  }

  if (!summary || summary.total === 0) {
    return (
      <Panel title="Summary">
        <EmptyBlock message="No complaints yet. Summary will appear once cases are registered." />
      </Panel>
    );
  }

  const cards = [
    { label: "Total", value: summary.total },
    { label: "Open", value: openCount(summary) },
    { label: "Resolved", value: statusCount(summary, "RESOLVED") },
    { label: "Closed", value: statusCount(summary, "CLOSED") },
  ];

  return (
    <Panel title="Summary">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {cards.map((card) => (
          <div
            key={card.label}
            className="rounded-lg border border-white/10 bg-black/20 px-4 py-4"
          >
            <p className="text-xs uppercase tracking-[0.16em] text-[var(--muted)]">
              {card.label}
            </p>
            <p className="mt-2 text-3xl font-semibold tabular-nums text-[var(--ink)]">
              {card.value}
            </p>
          </div>
        ))}
      </div>
    </Panel>
  );
}
