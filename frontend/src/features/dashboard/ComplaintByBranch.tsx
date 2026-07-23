import type { BranchCount } from "@/lib/api/types";
import { EmptyBlock, LoadingBlock, Panel } from "./ui";

export function ComplaintByBranch({
  rows,
  loading,
}: {
  rows: BranchCount[] | null;
  loading: boolean;
}) {
  if (loading) {
    return (
      <Panel title="Complaint by Branch">
        <LoadingBlock rows={4} />
      </Panel>
    );
  }

  if (!rows || rows.length === 0) {
    return (
      <Panel title="Complaint by Branch">
        <EmptyBlock message="No branch activity yet." />
      </Panel>
    );
  }

  return (
    <Panel title="Complaint by Branch">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-white/10 text-[var(--muted)]">
            <tr>
              <th className="py-2 pr-4 font-medium">Branch</th>
              <th className="py-2 pr-4 font-medium">Code</th>
              <th className="py-2 text-right font-medium">Total</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, index) => (
              <tr
                key={row.branchId ?? `unassigned-${index}`}
                className="border-b border-white/5"
              >
                <td className="py-2.5 pr-4">
                  {row.branchName ?? "Unassigned"}
                </td>
                <td className="py-2.5 pr-4 text-[var(--muted)]">
                  {row.branchCode ?? "—"}
                </td>
                <td className="py-2.5 text-right tabular-nums font-medium">
                  {row.total}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Panel>
  );
}
