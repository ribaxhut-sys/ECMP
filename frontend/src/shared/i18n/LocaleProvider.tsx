"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { NextIntlClientProvider } from "next-intl";
import { useRouter } from "next/navigation";
import {
  DEFAULT_LOCALE,
  LOCALE_COOKIE,
  LOCALE_COOKIE_MAX_AGE,
  LOCALE_STORAGE_KEY,
  isAppLocale,
  resolveLocale,
  type AppLocale,
} from "@/i18n/config";

type Messages = Record<string, unknown>;

interface LocaleContextValue {
  locale: AppLocale;
  setLocale: (locale: AppLocale) => Promise<void>;
  ready: boolean;
}

const LocaleContext = createContext<LocaleContextValue | null>(null);

function readStoredLocale(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return window.localStorage.getItem(LOCALE_STORAGE_KEY);
  } catch {
    return null;
  }
}

function readCookieLocale(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie
    .split("; ")
    .find((row) => row.startsWith(`${LOCALE_COOKIE}=`));
  return match ? decodeURIComponent(match.split("=")[1] ?? "") : null;
}

function persistLocale(locale: AppLocale): void {
  try {
    window.localStorage.setItem(LOCALE_STORAGE_KEY, locale);
  } catch {
    /* ignore quota / private mode */
  }
  const secure =
    typeof window !== "undefined" && window.location.protocol === "https:"
      ? "; Secure"
      : "";
  document.cookie = `${LOCALE_COOKIE}=${encodeURIComponent(locale)}; Path=/; Max-Age=${LOCALE_COOKIE_MAX_AGE}; SameSite=Lax${secure}`;
  if (typeof document !== "undefined") {
    document.documentElement.lang = locale;
  }
}

async function loadMessages(locale: AppLocale): Promise<Messages> {
  const mod = await import(`../../../messages/${locale}.json`);
  return mod.default as Messages;
}

export function LocaleProvider({
  children,
  initialLocale,
  initialMessages,
  userPreferredLanguage,
  onLocalePersisted,
}: {
  children: ReactNode;
  initialLocale: AppLocale;
  initialMessages: Messages;
  /** From AuthMe when authenticated — highest priority when present. */
  userPreferredLanguage?: string | null;
  /** Persist preference to API when authenticated. */
  onLocalePersisted?: (locale: AppLocale) => Promise<void> | void;
}) {
  const router = useRouter();
  const [locale, setLocaleState] = useState<AppLocale>(initialLocale);
  const [messages, setMessages] = useState<Messages>(initialMessages);
  const [ready, setReady] = useState(false);
  /** Last user preference we applied — avoids reverting after a local switch. */
  const appliedUserPref = useRef<string | null>(null);
  const hydrated = useRef(false);

  // Initial client hydration (cookie / storage / browser). Runs once.
  useEffect(() => {
    if (hydrated.current) return;
    hydrated.current = true;

    const resolved = resolveLocale({
      userPreference: isAppLocale(userPreferredLanguage)
        ? userPreferredLanguage
        : null,
      cookieValue: readCookieLocale() ?? readStoredLocale(),
    });

    let cancelled = false;
    void (async () => {
      if (resolved !== locale) {
        const nextMessages = await loadMessages(resolved);
        if (cancelled) return;
        setMessages(nextMessages);
        setLocaleState(resolved);
      }
      persistLocale(resolved);
      if (isAppLocale(userPreferredLanguage)) {
        appliedUserPref.current = userPreferredLanguage;
      }
      if (!cancelled) setReady(true);
    })();

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // When the authenticated user's stored preference first arrives (or changes
  // from the server — e.g. another device), adopt it once per distinct value.
  useEffect(() => {
    if (!isAppLocale(userPreferredLanguage)) return;
    if (appliedUserPref.current === userPreferredLanguage) return;
    appliedUserPref.current = userPreferredLanguage;
    if (userPreferredLanguage === locale) {
      persistLocale(userPreferredLanguage);
      return;
    }
    let cancelled = false;
    void (async () => {
      const nextMessages = await loadMessages(userPreferredLanguage);
      if (cancelled) return;
      setMessages(nextMessages);
      setLocaleState(userPreferredLanguage);
      persistLocale(userPreferredLanguage);
    })();
    return () => {
      cancelled = true;
    };
  }, [userPreferredLanguage, locale]);

  const setLocale = useCallback(
    async (next: AppLocale) => {
      if (next === locale) return;
      const nextMessages = await loadMessages(next);
      setMessages(nextMessages);
      setLocaleState(next);
      persistLocale(next);
      // Treat local switch as the new applied preference so the user-pref
      // effect does not snap back to a stale AuthMe value.
      appliedUserPref.current = next;
      try {
        await onLocalePersisted?.(next);
      } catch {
        /* API persistence is best-effort; UI already switched */
      }
      router.refresh();
    },
    [locale, onLocalePersisted, router],
  );

  const value = useMemo(
    () => ({ locale, setLocale, ready }),
    [locale, setLocale, ready],
  );

  return (
    <LocaleContext.Provider value={value}>
      <NextIntlClientProvider
        locale={locale}
        messages={messages}
        timeZone="Asia/Jakarta"
      >
        {children}
      </NextIntlClientProvider>
    </LocaleContext.Provider>
  );
}

export function useLocaleContext(): LocaleContextValue {
  const ctx = useContext(LocaleContext);
  if (!ctx) {
    throw new Error("useLocaleContext must be used within LocaleProvider");
  }
  return ctx;
}

export { DEFAULT_LOCALE };
