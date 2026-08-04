"use client";

import { useTranslations } from "next-intl";

export function IdentityBrand({
  eyebrow,
  title,
  subtitle,
}: {
  eyebrow?: string;
  title: string;
  subtitle: string;
}) {
  const t = useTranslations("auth");

  return (
    <header className="space-y-3 text-center">
      <div className="space-y-1">
        <p className="text-[length:var(--ecmp-font-display-size)] font-[number:var(--ecmp-font-page-title-weight)] tracking-tight text-ecmp-text-primary">
          {t("brandName")}
        </p>
        <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
          {t("brandProduct")}
        </p>
      </div>
      {eyebrow ? (
        <p className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-primary">
          {eyebrow}
        </p>
      ) : null}
      <div className="space-y-1">
        <h1 className="text-[length:var(--ecmp-font-page-title-size)] font-[number:var(--ecmp-font-page-title-weight)] leading-[var(--ecmp-font-page-title-line)] tracking-tight text-ecmp-text-primary">
          {title}
        </h1>
        <p className="mx-auto max-w-md text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
          {subtitle}
        </p>
      </div>
    </header>
  );
}
