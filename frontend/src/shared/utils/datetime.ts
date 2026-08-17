/**
 * Operator-facing datetime — locale-aware, 24-hour, Asia/Jakarta.
 * Date and time are formatted separately so `month: "long"` does not insert
 * ICU's "pukul" (e.g. "14 Agustus 2026, 10.51" not "… pukul 10.51").
 *
 * The locale argument is required: operator screens must follow the language
 * the user picked in the switcher, not the browser's. Pass `useLocale()` from
 * next-intl in components, or thread the active locale through helpers.
 */

import { LOCALE_META, DEFAULT_LOCALE, isAppLocale } from "@/i18n/config";

export const OPERATOR_TIME_ZONE = "Asia/Jakarta";

const OPERATOR_DATE_OPTIONS: Intl.DateTimeFormatOptions = {
  day: "2-digit",
  month: "long",
  year: "numeric",
  timeZone: OPERATOR_TIME_ZONE,
};

const OPERATOR_TIME_OPTIONS: Intl.DateTimeFormatOptions = {
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
  timeZone: OPERATOR_TIME_ZONE,
};

function bcp47(locale: string | undefined): string {
  return LOCALE_META[isAppLocale(locale) ? locale : DEFAULT_LOCALE].bcp47;
}

export function formatDateTime24(
  value: string | null | undefined,
  locale: string,
  empty = "",
): string {
  if (!value) return empty;
  try {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return empty || value;
    const tag = bcp47(locale);
    const datePart = new Intl.DateTimeFormat(
      tag,
      OPERATOR_DATE_OPTIONS,
    ).format(date);
    const timePart = new Intl.DateTimeFormat(
      tag,
      OPERATOR_TIME_OPTIONS,
    ).format(date);
    return `${datePart}, ${timePart}`;
  } catch {
    return value;
  }
}

const OPERATOR_SHORT_DATETIME_OPTIONS: Intl.DateTimeFormatOptions = {
  day: "2-digit",
  month: "short",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
  timeZone: OPERATOR_TIME_ZONE,
};

/** Compact single-part variant (short month, one Intl call) used in history/timeline panels. */
export function formatShortDateTime24(iso: string, locale: string): string {
  try {
    return new Intl.DateTimeFormat(
      bcp47(locale),
      OPERATOR_SHORT_DATETIME_OPTIONS,
    ).format(new Date(iso));
  } catch {
    return iso;
  }
}

/**
 * `YYYY-MM-DD` for the operator calendar in Asia/Jakarta — never
 * `toISOString().slice(0, 10)` (UTC) and never `Date#getFullYear/Month/Date`
 * (browser TZ). Lab operators are WIB regardless of the machine clock.
 */
export function toLocalDateKey(date: Date): string {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: OPERATOR_TIME_ZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(date);
  const year = parts.find((part) => part.type === "year")?.value ?? "";
  const month = parts.find((part) => part.type === "month")?.value ?? "";
  const day = parts.find((part) => part.type === "day")?.value ?? "";
  return `${year}-${month}-${day}`;
}

const HQ_ARRIVAL_DATE_RE = /^\d{4}-\d{2}-\d{2}$/;
const HQ_ARRIVAL_TIME_RE = /^\d{2}:\d{2}$/;
/** Calendar line written into older HQ-arrival notes: `YYYY-MM-DD HH:MM` plus optional WP note. */
const HQ_ARRIVAL_BLOB_RE =
  /^(\d{4}-\d{2}-\d{2})(?:[ T]| pukul | at )(\d{2})[:.](\d{2})(?:\s*\n([\s\S]*))?$/i;

const HQ_ARRIVAL_WEEKDAY_OPTIONS: Intl.DateTimeFormatOptions = {
  weekday: "long",
  timeZone: OPERATOR_TIME_ZONE,
};

const HQ_ARRIVAL_DATE_OPTIONS: Intl.DateTimeFormatOptions = {
  day: "numeric",
  month: "long",
  year: "numeric",
  timeZone: OPERATOR_TIME_ZONE,
};

/**
 * Parse a calendar date+time as a fixed-offset Asia/Jakarta instant.
 * Indonesia has no DST; do not use the browser timezone.
 */
export function hqArrivalInstant(
  date: string,
  time: string,
): Date | null {
  const ymd = date.trim();
  const hm = time.trim();
  if (!HQ_ARRIVAL_DATE_RE.test(ymd) || !HQ_ARRIVAL_TIME_RE.test(hm)) return null;
  const instant = new Date(`${ymd}T${hm}:00+07:00`);
  return Number.isNaN(instant.getTime()) ? null : instant;
}

export function formatHqArrivalSlot(
  date: string,
  time: string,
  locale: string,
): { weekday: string; date: string; time: string } | null {
  const instant = hqArrivalInstant(date, time);
  if (!instant) return null;
  const tag = bcp47(locale);
  return {
    weekday: new Intl.DateTimeFormat(tag, HQ_ARRIVAL_WEEKDAY_OPTIONS).format(
      instant,
    ),
    date: new Intl.DateTimeFormat(tag, HQ_ARRIVAL_DATE_OPTIONS).format(instant),
    time: new Intl.DateTimeFormat(tag, OPERATOR_TIME_OPTIONS).format(instant),
  };
}

export function parseHqArrivalScheduleBlob(
  note: string | null | undefined,
): { date: string; time: string; wpNote: string } | null {
  const text = (note ?? "").trim();
  if (!text) return null;
  const match = text.match(HQ_ARRIVAL_BLOB_RE);
  if (!match) return null;
  return {
    date: match[1],
    time: `${match[2]}:${match[3]}`,
    wpNote: (match[4] ?? "").trim(),
  };
}

/** Prefer structured slot fields; fall back to the legacy note blob. Never invent a slot. */
export function resolveHqArrivalDisplay(input: {
  arrivalDate?: string | null;
  arrivalTime?: string | null;
  note?: string | null;
}): { date: string; time: string; wpNote: string } | null {
  const date = (input.arrivalDate ?? "").trim();
  const time = (input.arrivalTime ?? "").trim();
  const parsedNote = parseHqArrivalScheduleBlob(input.note);
  if (date && time) {
    return {
      date,
      time,
      wpNote: parsedNote ? parsedNote.wpNote : (input.note ?? "").trim(),
    };
  }
  return parsedNote;
}
