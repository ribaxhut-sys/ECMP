/**
 * Operator-facing datetime display — always 24-hour clock (never AM/PM).
 */

export function formatDateTime24(
  value: string | null | undefined,
  empty = "",
): string {
  if (!value) return empty;
  try {
    return new Intl.DateTimeFormat(undefined, {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    }).format(new Date(value));
  } catch {
    return value;
  }
}
