"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import { Alert } from "@/shared/ui";

/**
 * DEC-025 §3.6 — mark Foundation surfaces as legacy without deleting routes.
 */
export function FoundationLegacyBanner() {
  const t = useTranslations("complaints");

  return (
    <Alert
      tone="info"
      data-testid="foundation-legacy-banner"
      title={t("foundationLegacyTitle")}
      description={t("foundationLegacyBody")}
      actions={
        <>
          <Link
            href="/complaints"
            className="inline-flex h-9 items-center rounded-[var(--ecmp-radius-button)] border border-ecmp-border bg-[color-mix(in_srgb,var(--ecmp-color-text-primary)_5%,transparent)] px-3 text-[length:var(--ecmp-font-body-small-size)] font-medium text-ecmp-text-primary hover:border-ecmp-secondary hover:bg-ecmp-hover"
          >
            {t("foundationLegacyComplaints")}
          </Link>
          <Link
            href="/complaints/cm/cases"
            className="inline-flex h-9 items-center rounded-[var(--ecmp-radius-button)] border border-ecmp-border bg-[color-mix(in_srgb,var(--ecmp-color-text-primary)_5%,transparent)] px-3 text-[length:var(--ecmp-font-body-small-size)] font-medium text-ecmp-text-primary hover:border-ecmp-secondary hover:bg-ecmp-hover"
          >
            {t("foundationLegacyCases")}
          </Link>
        </>
      }
    />
  );
}
