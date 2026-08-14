import {
  LOCALE_META,
  type AppLocale,
  DEFAULT_LOCALE,
  isAppLocale,
} from "./config";

function meta(locale: string | AppLocale) {
  const code = isAppLocale(locale) ? locale : DEFAULT_LOCALE;
  return LOCALE_META[code];
}

/** Format a Date (or ISO string) using locale date pattern. */
export function formatDate(
  value: Date | string | number | null | undefined,
  locale: AppLocale | string,
  options?: Intl.DateTimeFormatOptions,
): string {
  if (value == null || value === "") return "";
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  const { bcp47, dateFormat } = meta(locale);
  const defaults: Intl.DateTimeFormatOptions =
    dateFormat === "dd/MM/yyyy"
      ? { day: "2-digit", month: "2-digit", year: "numeric" }
      : { month: "2-digit", day: "2-digit", year: "numeric" };
  return new Intl.DateTimeFormat(bcp47, {
    timeZone: "Asia/Jakarta",
    ...defaults,
    ...options,
  }).format(date);
}

export function formatDateTime(
  value: Date | string | number | null | undefined,
  locale: AppLocale | string,
  options?: Intl.DateTimeFormatOptions,
): string {
  if (value == null || value === "") return "";
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  const { bcp47, dateFormat } = meta(locale);
  const defaults: Intl.DateTimeFormatOptions =
    dateFormat === "dd/MM/yyyy"
      ? {
          day: "2-digit",
          month: "2-digit",
          year: "numeric",
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        }
      : {
          month: "2-digit",
          day: "2-digit",
          year: "numeric",
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        };
  return new Intl.DateTimeFormat(bcp47, {
    timeZone: "Asia/Jakarta",
    ...defaults,
    ...options,
    // Operator-facing clocks are always 24h (never AM/PM), even for en-US.
    hour12: options?.hour12 ?? false,
  }).format(date);
}

/** id → 1.000,50 ; en → 1,000.50 */
export function formatNumber(
  value: number | null | undefined,
  locale: AppLocale | string,
  options?: Intl.NumberFormatOptions,
): string {
  if (value == null || Number.isNaN(value)) return "";
  return new Intl.NumberFormat(meta(locale).bcp47, options).format(value);
}

/**
 * Currency: Indonesian uses Rp (narrowSymbol), English uses IDR (code).
 * Configurable via LOCALE_META.currencyDisplay.
 */
export function formatCurrency(
  value: number | null | undefined,
  locale: AppLocale | string,
  options?: Intl.NumberFormatOptions,
): string {
  if (value == null || Number.isNaN(value)) return "";
  const { bcp47, currency, currencyDisplay } = meta(locale);
  return new Intl.NumberFormat(bcp47, {
    style: "currency",
    currency,
    currencyDisplay,
    ...options,
  }).format(value);
}
