"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";

export default function NotFound() {
  const t = useTranslations("common");

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 bg-ecmp-background px-4 text-center">
      <p className="text-[length:var(--ecmp-font-caption-size)] font-medium tracking-wide text-ecmp-text-secondary">
        404
      </p>
      <h1 className="text-[length:var(--ecmp-font-heading-size)] font-semibold tracking-tight text-ecmp-text-primary">
        {t("notFoundTitle")}
      </h1>
      <p className="max-w-md text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
        {t("notFoundDescription")}
      </p>
      <Link
        href="/dashboard"
        className="inline-flex min-h-[44px] items-center justify-center rounded-[var(--ecmp-radius-md)] border border-transparent bg-ecmp-primary px-4 text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-primary-foreground transition-opacity hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-focus"
      >
        {t("goHome")}
      </Link>
    </main>
  );
}
