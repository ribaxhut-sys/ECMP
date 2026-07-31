import type { ReportSummary, StatusCount } from "@/lib/api/types";

export type ReportHeadlineCounts = {
  total: number;
  open: number;
  closed: number;
};

/** Derive headline counts from API-210 summary (or by-status rows). */
export function reportHeadlineCounts(
  summary: Pick<ReportSummary, "total" | "byStatus"> | null | undefined,
): ReportHeadlineCounts | null {
  if (!summary) return null;
  return {
    total: summary.total,
    open: countOpen(summary.byStatus),
    closed: countClosed(summary.byStatus),
  };
}

function countOpen(rows: StatusCount[]): number {
  return rows
    .filter((row) => row.status !== "CLOSED" && row.status !== "RESOLVED")
    .reduce((acc, row) => acc + row.count, 0);
}

function countClosed(rows: StatusCount[]): number {
  return rows
    .filter((row) => row.status === "CLOSED" || row.status === "RESOLVED")
    .reduce((acc, row) => acc + row.count, 0);
}
