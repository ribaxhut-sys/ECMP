/**
 * ECMP i18n configuration — unlimited future locales.
 * Add a locale here, create messages/<code>.json, and register display metadata.
 */

export const LOCALES = ["id", "en"] as const;

export type AppLocale = (typeof LOCALES)[number];

export const DEFAULT_LOCALE: AppLocale = "id";

/** Cookie + localStorage key for persisted UI language preference. */
export const LOCALE_COOKIE = "NEXT_LOCALE";
export const LOCALE_STORAGE_KEY = "ecmp.locale";

export const LOCALE_COOKIE_MAX_AGE = 60 * 60 * 24 * 365; // 1 year

export interface LocaleMeta {
  code: AppLocale;
  /** Native display name */
  label: string;
  /** Short language code (e.g. ID, EN) — fallback / aria */
  flag: string;
  /** Public path to flag SVG/PNG used in the language switcher */
  flagSrc: string;
  /** BCP 47 tag for Intl formatters */
  bcp47: string;
  dateFormat: "dd/MM/yyyy" | "MM/dd/yyyy";
  /** ISO 4217; display style differs by locale (Rp vs IDR) */
  currency: "IDR";
  currencyDisplay: "narrowSymbol" | "code";
}

export const LOCALE_META: Record<AppLocale, LocaleMeta> = {
  id: {
    code: "id",
    label: "Bahasa Indonesia",
    flag: "ID",
    flagSrc: "/flags/id.svg",
    bcp47: "id-ID",
    dateFormat: "dd/MM/yyyy",
    currency: "IDR",
    currencyDisplay: "narrowSymbol",
  },
  en: {
    code: "en",
    label: "English",
    flag: "EN",
    flagSrc: "/flags/en.svg",
    bcp47: "en-US",
    dateFormat: "MM/dd/yyyy",
    currency: "IDR",
    currencyDisplay: "code",
  },
};

export function isAppLocale(value: unknown): value is AppLocale {
  return typeof value === "string" && (LOCALES as readonly string[]).includes(value);
}

/** Map browser language tags (e.g. id-ID, en-GB) to supported AppLocale. */
export function resolveBrowserLocale(
  languages: readonly string[] | undefined,
): AppLocale | null {
  if (!languages?.length) return null;
  for (const raw of languages) {
    const tag = raw.trim().toLowerCase();
    if (!tag) continue;
    const primary = tag.split("-")[0] ?? tag;
    if (isAppLocale(primary)) return primary;
  }
  return null;
}

/**
 * Resolve locale by priority:
 * 1. Explicit user preference (API / cookie / localStorage)
 * 2. Default = Indonesian (`id`)
 *
 * Browser `Accept-Language` is intentionally NOT used for first paint —
 * ECMP ships Indonesian-first; English is opt-in via the language switcher.
 * (Browser hint remains available via `resolveBrowserLocale` for future use.)
 */
export function resolveLocale(options: {
  userPreference?: string | null;
  cookieValue?: string | null;
  browserLanguages?: readonly string[];
}): AppLocale {
  if (isAppLocale(options.userPreference)) return options.userPreference;
  if (isAppLocale(options.cookieValue)) return options.cookieValue;
  void options.browserLanguages;
  return DEFAULT_LOCALE;
}
