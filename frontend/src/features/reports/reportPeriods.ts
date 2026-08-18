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

/** Resolve a preset into the query window sent to the Aggregate KPI. */
export function reportPeriodRange(
  key: ReportPeriodKey,
  now: Date = new Date(),
): ReportPeriodRange {
  if (key === "all") return {};

  const today = jakartaYmd(now);

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

/** Message key per preset — keeps message ids camelCase like the rest. */
export const REPORT_PERIOD_LABEL_KEY: Record<ReportPeriodKey, string> = {
  all: "periodAll",
  thisMonth: "periodThisMonth",
  lastMonth: "periodLastMonth",
  last90: "periodLast90",
  thisYear: "periodThisYear",
};
