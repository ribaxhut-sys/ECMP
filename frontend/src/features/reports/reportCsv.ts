/**
 * CSV export for /reports — a report you cannot take into a meeting is only
 * half a report. Built in the browser from the data already on screen, so no
 * second read of the Aggregate can disagree with what the user is looking at.
 */
import { toLocalDateKey } from "@/shared/utils/datetime";

export type ReportCsvRow = (string | number)[];

const SEPARATOR = ",";
const LINE_BREAK = "\r\n";
/** Excel opens UTF-8 CSV as latin-1 without this. */
const BOM = "﻿";

function escapeCsvCell(value: string | number): string {
  const text = String(value ?? "");
  return `"${text.replace(/"/g, '""')}"`;
}

/** Serialize rows to RFC-4180 CSV; every cell is quoted. */
export function buildReportCsv(rows: ReportCsvRow[]): string {
  return (
    BOM +
    rows.map((row) => row.map(escapeCsvCell).join(SEPARATOR)).join(LINE_BREAK) +
    LINE_BREAK
  );
}

/** `laporan-pengaduan-thisMonth-2026-08-18.csv` */
export function reportCsvFilename(
  periodKey: string,
  now: Date = new Date(),
): string {
  const stamp = toLocalDateKey(now);
  return `laporan-pengaduan-${periodKey}-${stamp}.csv`;
}

/** Hand the CSV to the browser as a download. No-op outside the browser. */
export function downloadCsv(filename: string, csv: string): void {
  if (typeof document === "undefined") return;
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
