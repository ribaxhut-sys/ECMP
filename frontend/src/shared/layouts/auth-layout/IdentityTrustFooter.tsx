"use client";

import { useTranslations } from "next-intl";

export function IdentityTrustFooter() {
  const t = useTranslations("auth");

  return (
    <footer className="space-y-3 text-center">
      <ul
        className="flex flex-col gap-1.5 sm:flex-row sm:flex-wrap sm:justify-center sm:gap-x-4 sm:gap-y-1"
        aria-label={t("trustSignalsLabel")}
      >
        <li className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
          {t("trustSecureInternal")}
        </li>
        <li className="hidden text-ecmp-border sm:inline" aria-hidden>
          ·
        </li>
        <li className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
          {t("trustSessionProtected")}
        </li>
        <li className="hidden text-ecmp-border sm:inline" aria-hidden>
          ·
        </li>
        <li className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
          {t("trustAuthorizedOnly")}
        </li>
      </ul>
      <div className="space-y-0.5 text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
        <p>{t("trustedInternalPlatform")}</p>
        <p>
          {t("productVersion")} · {t("copyright")}
        </p>
      </div>
    </footer>
  );
}
