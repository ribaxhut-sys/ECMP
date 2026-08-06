"use client";

import { useEffect, useId, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import { LOCALE_META, LOCALES, type AppLocale } from "@/i18n/config";
import { useLocaleContext } from "./LocaleProvider";

interface LanguageSwitcherProps {
  /** Compact select for header; full for settings/profile */
  variant?: "compact" | "full";
  className?: string;
  id?: string;
}

function FlagIcon({
  locale,
  className = "h-3.5 w-5",
}: {
  locale: AppLocale;
  className?: string;
}) {
  const meta = LOCALE_META[locale];
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={meta.flagSrc}
      alt=""
      width={20}
      height={14}
      className={`inline-block shrink-0 rounded-[var(--ecmp-radius-sm)] object-cover ring-1 ring-ecmp-border ${className}`}
      aria-hidden="true"
    />
  );
}

export function LanguageSwitcher({
  variant = "compact",
  className = "",
  id,
}: LanguageSwitcherProps) {
  const { locale, setLocale } = useLocaleContext();
  const tCommon = useTranslations("common");
  const listId = useId();
  const rootId = id ?? `language-switcher-${listId}`;
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const current = LOCALE_META[locale];

  useEffect(() => {
    if (!open) return;
    function onPointerDown(event: MouseEvent) {
      if (!rootRef.current?.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  async function choose(next: AppLocale) {
    setOpen(false);
    await setLocale(next);
  }

  return (
    <div
      ref={rootRef}
      className={
        variant === "full"
          ? `relative flex flex-col gap-1 ${className}`
          : `relative inline-flex ${className}`
      }
    >
      {variant === "full" ? (
        <span className="text-[length:var(--ecmp-font-caption-size)] font-medium text-ecmp-text-secondary">
          {tCommon("language")}
        </span>
      ) : (
        <span className="sr-only">{tCommon("language")}</span>
      )}

      <button
        type="button"
        id={rootId}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={`${rootId}-list`}
        aria-label={`${tCommon("language")}: ${current.label}`}
        onClick={() => setOpen((prev) => !prev)}
        className={
          variant === "full"
            ? "ecmp-touch inline-flex w-full max-w-[8rem] items-center gap-1.5 rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface px-2.5 py-2 text-left text-[length:var(--ecmp-font-body-size)] font-semibold tracking-wide text-ecmp-text-primary focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-focus"
            : "ecmp-touch inline-flex items-center gap-1.5 rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface px-2 py-1.5 text-[length:var(--ecmp-font-caption-size)] font-semibold tracking-wide text-ecmp-text-primary focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-focus"
        }
      >
        <FlagIcon locale={locale} />
        <span>{current.flag}</span>
        <span className="text-ecmp-text-secondary" aria-hidden="true">
          ▾
        </span>
      </button>

      {open ? (
        <ul
          id={`${rootId}-list`}
          role="listbox"
          aria-labelledby={rootId}
          className="absolute top-full right-0 z-50 mt-1 min-w-full overflow-hidden rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface py-1 shadow-ecmp-md"
        >
          {LOCALES.map((code) => {
            const meta = LOCALE_META[code];
            const selected = code === locale;
            return (
              <li key={code} role="option" aria-selected={selected}>
                <button
                  type="button"
                  aria-label={meta.label}
                  className={
                    selected
                      ? "ecmp-touch flex w-full items-center gap-1.5 bg-ecmp-primary-muted px-2.5 py-2 text-left text-[length:var(--ecmp-font-body-size)] font-semibold tracking-wide text-ecmp-primary"
                      : "ecmp-touch flex w-full items-center gap-1.5 px-2.5 py-2 text-left text-[length:var(--ecmp-font-body-size)] font-semibold tracking-wide text-ecmp-text-primary hover:bg-ecmp-secondary-muted"
                  }
                  onClick={() => {
                    void choose(code);
                  }}
                >
                  <FlagIcon locale={code} />
                  <span>{meta.flag}</span>
                </button>
              </li>
            );
          })}
        </ul>
      ) : null}
    </div>
  );
}
