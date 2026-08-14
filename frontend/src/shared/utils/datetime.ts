/**
 * Operator-facing datetime — Bahasa Indonesia, 24-hour, Asia/Jakarta.
 * Do not use the host locale (`undefined`): lab/server Node is often en-US
 * and renders "Aug 14, 2026, 10:51" instead of "14 Agu 2026, 10.51".
 */

export const OPERATOR_TIME_ZONE = "Asia/Jakarta";
export const OPERATOR_DATE_LOCALE = "id-ID";

const OPERATOR_DATE_TIME_OPTIONS: Intl.DateTimeFormatOptions = {
  day: "2-digit",
  month: "short",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
  timeZone: OPERATOR_TIME_ZONE,
};

export function formatDateTime24(
  value: string | null | undefined,
  empty = "",
): string {
  if (!value) return empty;
  try {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return empty || value;
    return new Intl.DateTimeFormat(
      OPERATOR_DATE_LOCALE,
      OPERATOR_DATE_TIME_OPTIONS,
    ).format(date);
  } catch {
    return value;
  }
}
