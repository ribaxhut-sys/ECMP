"use client";

import { useTranslations } from "next-intl";
import { PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH } from "./passwordPolicy";

export function PasswordRequirements({
  password = "",
}: {
  password?: string;
}) {
  const t = useTranslations("auth");
  const longEnough = password.length >= PASSWORD_MIN_LENGTH;
  const withinMax = password.length <= PASSWORD_MAX_LENGTH;
  const hasValue = password.length > 0;

  return (
    <div
      className="rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface-sunken p-3"
      aria-live="polite"
    >
      <p className="text-[length:var(--ecmp-font-caption-size)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
        {t("passwordRequirements")}
      </p>
      <ul className="mt-2 space-y-1.5 text-[length:var(--ecmp-font-helper-size)]">
        <li
          className={
            !hasValue
              ? "text-ecmp-text-secondary"
              : longEnough
                ? "text-ecmp-success-text"
                : "text-ecmp-danger-text"
          }
        >
          {t("passwordRequirementMin", { min: PASSWORD_MIN_LENGTH })}
        </li>
        <li
          className={
            !hasValue
              ? "text-ecmp-text-secondary"
              : withinMax
                ? "text-ecmp-success-text"
                : "text-ecmp-danger-text"
          }
        >
          {t("passwordRequirementMax", { max: PASSWORD_MAX_LENGTH })}
        </li>
        <li className="text-ecmp-text-secondary">
          {t("passwordRequirementConfirm")}
        </li>
      </ul>
    </div>
  );
}
