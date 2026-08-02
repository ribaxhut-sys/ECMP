"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";

export default function NotFound() {
  const t = useTranslations("common");

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-[var(--ecmp-panel-gap)] bg-ecmp-background px-[var(--ecmp-page-gutter)] text-center">
      <p className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
        404
      </p>
      <h1 className="text-[length:var(--ecmp-font-page-title-size)] font-[number:var(--ecmp-font-page-title-weight)] leading-[var(--ecmp-font-page-title-line)] tracking-tight text-ecmp-text-primary">
        {t("notFoundTitle")}
      </h1>
      <p className="max-w-md text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
        {t("notFoundDescription")}
      </p>
      <Link
        href="/dashboard"
        className="inline-flex min-h-[var(--ecmp-touch-min)] items-center justify-center rounded-[var(--ecmp-radius-button)] border border-transparent bg-ecmp-primary px-4 text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-primary-foreground shadow-ecmp-raised hover:bg-[color-mix(in_srgb,var(--ecmp-color-primary)_88%,black)] hover:shadow-ecmp-hover focus-visible:outline-none focus-visible:ring-[length:var(--ecmp-focus-ring-width)] focus-visible:ring-ecmp-focus focus-visible:ring-offset-[length:var(--ecmp-focus-ring-offset)]"
      >
        {t("goHome")}
      </Link>
    </main>
  );
}
