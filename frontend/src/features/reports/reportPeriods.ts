/**
 * Period presets for /reports.
 *
 * The dashboard answers "what is happening now"; reports answer "what happened
 * in this period". Bounds are calendar days in Asia/Jakarta (never UTC month
 * arithmetic — see `toLocalDateKey`), sent as an inclusive `dateFrom`/`dateTo`
 * pair matching the backend window.
 */
import { hqArrivalInstant, toLocalDateKey } from "@/shared/utils/datetime";

export const REPORT_PERIOD_KEYS = [
  "all",
  "thisWeek",
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

type Ymd = { year: number; month: number; day: number };

function pad2(value: number): string {
  return String(value).padStart(2, "0");
}

function jakartaYmd(date: Date): Ymd {
  const [year, month, day] = toLocalDateKey(date).split("-").map(Number);
  return { year, month, day };
}

function addCalendarDays(parts: Ymd, delta: number): Ymd {
  const utc = new Date(Date.UTC(parts.year, parts.month - 1, parts.day + delta));
  return {
    year: utc.getUTCFullYear(),
    month: utc.getUTCMonth() + 1,
    day: utc.getUTCDate(),
  };
}

/** 00:00 Asia/Jakarta on that calendar day. */
function jakartaDayStart(parts: Ymd): Date {
  const instant = hqArrivalInstant(
    `${parts.year}-${pad2(parts.month)}-${pad2(parts.day)}`,
    "00:00",
  );
  if (!instant) {
    throw new RangeError(
      `invalid Jakarta calendar day ${parts.year}-${parts.month}-${parts.day}`,
    );
  }
  return instant;
}

function inclusiveEndIso(parts: Ymd): string {
  const next = addCalendarDays(parts, 1);
  return new Date(jakartaDayStart(next).getTime() - 1).toISOString();
}

function startIso(parts: Ymd): string {
  return jakartaDayStart(parts).toISOString();
}

function lastDayOfMonth(year: number, month: number): number {
  return new Date(Date.UTC(year, month, 0)).getUTCDate();
}

function shiftMonth(parts: Ymd, delta: number): Ymd {
  const utc = new Date(Date.UTC(parts.year, parts.month - 1 + delta, 1));
  return {
    year: utc.getUTCFullYear(),
    month: utc.getUTCMonth() + 1,
    day: 1,
  };
}

/** Resolve a preset into the query window sent to the Aggregate KPI. */
export function reportPeriodRange(
  key: ReportPeriodKey,
  now: Date = new Date(),
): ReportPeriodRange {
  if (key === "all") return {};

  const today = jakartaYmd(now);

  if (key === "thisWeek") {
    // ISO week — Monday start. getUTCDay(): 0=Sun..6=Sat.
    const dow = new Date(
      Date.UTC(today.year, today.month - 1, today.day),
    ).getUTCDay();
    const daysSinceMonday = (dow + 6) % 7;
    const monday = addCalendarDays(today, -daysSinceMonday);
    return {
      dateFrom: startIso(monday),
      dateTo: inclusiveEndIso(today),
    };
  }

  if (key === "thisMonth") {
    return {
      dateFrom: startIso({ year: today.year, month: today.month, day: 1 }),
      dateTo: inclusiveEndIso(today),
    };
  }

  if (key === "lastMonth") {
    const firstThisMonth = { year: today.year, month: today.month, day: 1 };
    const lastDayPrev = addCalendarDays(firstThisMonth, -1);
    return {
      dateFrom: startIso({
        year: lastDayPrev.year,
        month: lastDayPrev.month,
        day: 1,
      }),
      dateTo: inclusiveEndIso(lastDayPrev),
    };
  }

  if (key === "last90") {
    const from = addCalendarDays(today, -89);
    return {
      dateFrom: startIso(from),
      dateTo: inclusiveEndIso(today),
    };
  }

  return {
    dateFrom: startIso({ year: today.year, month: 1, day: 1 }),
    dateTo: inclusiveEndIso(today),
  };
}

/**
 * Like-for-like window immediately before the selected preset.
 *
 * `all` has no predecessor. Partial windows (this week / month / year) compare
 * the same days in the previous period, not a full previous month or week.
 */
export function previousReportPeriodRange(
  key: ReportPeriodKey,
  now: Date = new Date(),
): ReportPeriodRange | null {
  if (key === "all") return null;

  const today = jakartaYmd(now);

  if (key === "thisWeek") {
    const current = reportPeriodRange("thisWeek", now);
    const from = jakartaYmd(new Date(current.dateFrom as string));
    const to = jakartaYmd(new Date(current.dateTo as string));
    return {
      dateFrom: startIso(addCalendarDays(from, -7)),
      dateTo: inclusiveEndIso(addCalendarDays(to, -7)),
    };
  }

  if (key === "thisMonth") {
    const prev = shiftMonth({ ...today, day: 1 }, -1);
    const day = Math.min(today.day, lastDayOfMonth(prev.year, prev.month));
    return {
      dateFrom: startIso({ ...prev, day: 1 }),
      dateTo: inclusiveEndIso({ ...prev, day }),
    };
  }

  if (key === "lastMonth") {
    const current = reportPeriodRange("lastMonth", now);
    const first = jakartaYmd(new Date(current.dateFrom as string));
    const prev = shiftMonth(first, -1);
    const last = addCalendarDays(shiftMonth(prev, 1), -1);
    return {
      dateFrom: startIso(prev),
      dateTo: inclusiveEndIso(last),
    };
  }

  if (key === "last90") {
    const current = reportPeriodRange("last90", now);
    const from = jakartaYmd(new Date(current.dateFrom as string));
    const prevTo = addCalendarDays(from, -1);
    return {
      dateFrom: startIso(addCalendarDays(prevTo, -89)),
      dateTo: inclusiveEndIso(prevTo),
    };
  }

  const prevYear = today.year - 1;
  const day = Math.min(today.day, lastDayOfMonth(prevYear, today.month));
  return {
    dateFrom: startIso({ year: prevYear, month: 1, day: 1 }),
    dateTo: inclusiveEndIso({
      year: prevYear,
      month: today.month,
      day,
    }),
  };
}

/** Message key per preset — keeps message ids camelCase like the rest. */
export const REPORT_PERIOD_LABEL_KEY: Record<ReportPeriodKey, string> = {
  all: "periodAll",
  thisWeek: "periodThisWeek",
  thisMonth: "periodThisMonth",
  lastMonth: "periodLastMonth",
  last90: "periodLast90",
  thisYear: "periodThisYear",
};
