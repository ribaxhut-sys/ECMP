import type { StatusCount } from "@/lib/api/types";
import { EmptyBlock, LoadingBlock, Panel } from "./ui";

export function ComplaintByStatus({
  rows,
  loading,
}: {
  rows: StatusCount[] | null;
  loading: boolean;
}) {
  if (loading) {
    return (
      <Panel title="Complaint by Status">
        <LoadingBlock rows={4} />
      </Panel>
    );
  }

  const visible = (rows ?? []).filter((row) => row.count > 0);
  if (visible.length === 0) {
    return (
      <Panel title="Complaint by Status">
        <EmptyBlock message="No status breakdown available." />
      </Panel>
    );
  }

  const max = Math.max(...visible.map((row) => row.count), 1);

  return (
    <Panel title="Complaint by Status">
      <ul className="space-y-3">
        {visible.map((row) => (
          <li key={row.status}>
            <div className="mb-1 flex items-center justify-between text-sm">
              <span>{row.status.replaceAll("_", " ")}</span>
              <span className="tabular-nums text-[var(--muted)]">{row.count}</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-white/10">
              <div
                className="h-full rounded-full bg-[var(--accent)]"
                style={{ width: `${(row.count / max) * 100}%` }}
              />
            </div>
          </li>
        ))}
      </ul>
    </Panel>
  );
}
