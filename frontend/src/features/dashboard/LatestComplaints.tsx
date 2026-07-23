import type { Complaint } from "@/lib/api/types";
import { EmptyBlock, LoadingBlock, Panel, PriorityBadge, StatusBadge } from "./ui";

function formatWhen(value: string): string {
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

export function LatestComplaints({
  rows,
  loading,
}: {
  rows: Complaint[] | null;
  loading: boolean;
}) {
  if (loading) {
    return (
      <Panel title="Latest Complaints">
        <LoadingBlock rows={5} />
      </Panel>
    );
  }

  if (!rows || rows.length === 0) {
    return (
      <Panel title="Latest Complaints">
        <EmptyBlock message="No complaints found." />
      </Panel>
    );
  }

  return (
    <Panel title="Latest Complaints">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-white/10 text-[var(--muted)]">
            <tr>
              <th className="py-2 pr-3 font-medium">Number</th>
              <th className="py-2 pr-3 font-medium">Subject</th>
              <th className="py-2 pr-3 font-medium">Status</th>
              <th className="py-2 pr-3 font-medium">Priority</th>
              <th className="py-2 font-medium">Created</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id} className="border-b border-white/5 align-top">
                <td className="py-2.5 pr-3 font-mono text-xs text-[var(--accent)]">
                  {row.complaintNumber}
                </td>
                <td className="max-w-[18rem] py-2.5 pr-3">
                  <span className="line-clamp-2">{row.subject}</span>
                </td>
                <td className="py-2.5 pr-3">
                  <StatusBadge status={row.status} />
                </td>
                <td className="py-2.5 pr-3">
                  <PriorityBadge priority={row.priority} />
                </td>
                <td className="py-2.5 whitespace-nowrap text-[var(--muted)]">
                  {formatWhen(row.createdAt)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Panel>
  );
}
