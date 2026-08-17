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
