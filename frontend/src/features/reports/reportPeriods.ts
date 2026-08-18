/**
 * Period presets for /reports.
 *
 * The dashboard answers "what is happening now"; reports answer "what happened
 * in this period". Ranges are half-open on the display side but sent as an
 * inclusive `dateFrom`/`dateTo` pair, matching the backend's `created_at`
 * window on the Batch-1 Aggregate.
 */
export const REPORT_PERIOD_KEYS = [
  "all",
  "thisMonth",
  "lastMonth",
  "last90",
  "thisYear",
] as const;

export type ReportPeriodKey = (typeof REPORT_PERIOD_KEYS)[number];

export const DEFAULT_REPORT_PERIOD: ReportPeriodKey = "all";

export type ReportPeriodRange = {
  dateFrom?: string;
  dateTo?: string;
};

function startOfDay(date: Date): Date {
  return new Date(
    Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()),
  );
}

function endOfDay(date: Date): Date {
  return new Date(
    Date.UTC(
      date.getUTCFullYear(),
      date.getUTCMonth(),
      date.getUTCDate(),
      23,
      59,
      59,
      999,
    ),
  );
}

/** Resolve a preset into the query window sent to the Aggregate KPI. */
export function reportPeriodRange(
  key: ReportPeriodKey,
  now: Date = new Date(),
): ReportPeriodRange {
  if (key === "all") return {};

  const year = now.getUTCFullYear();
  const month = now.getUTCMonth();

  if (key === "thisMonth") {
    return {
      dateFrom: new Date(Date.UTC(year, month, 1)).toISOString(),
      dateTo: endOfDay(now).toISOString(),
    };
  }

  if (key === "lastMonth") {
    return {
      dateFrom: new Date(Date.UTC(year, month - 1, 1)).toISOString(),
      dateTo: new Date(
        Date.UTC(year, month, 1, 0, 0, 0, -1),
      ).toISOString(),
    };
  }

  if (key === "last90") {
    const from = new Date(now);
    from.setUTCDate(from.getUTCDate() - 89);
    return {
      dateFrom: startOfDay(from).toISOString(),
      dateTo: endOfDay(now).toISOString(),
    };
  }

  return {
    dateFrom: new Date(Date.UTC(year, 0, 1)).toISOString(),
    dateTo: endOfDay(now).toISOString(),
  };
}

/** Message key per preset — keeps message ids camelCase like the rest. */
export const REPORT_PERIOD_LABEL_KEY: Record<ReportPeriodKey, string> = {
  all: "periodAll",
  thisMonth: "periodThisMonth",
  lastMonth: "periodLastMonth",
  last90: "periodLast90",
  thisYear: "periodThisYear",
};
