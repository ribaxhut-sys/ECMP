"use client";

import { useLocale, useTranslations } from "next-intl";
import { formatDateTime } from "@/i18n/formatting";
import { Button, Skeleton } from "@/shared/ui";
import {
  DASHBOARD_BODY,
  DASHBOARD_CAPTION,
  DASHBOARD_TITLE,
} from "./dashboardUtils";

function greetingKey(hour: number): "greetingMorning" | "greetingAfternoon" | "greetingEvening" {
  if (hour < 12) return "greetingMorning";
  if (hour < 18) return "greetingAfternoon";
  return "greetingEvening";
}

export function CompactHeader({
  displayName,
  loading,
  refreshing = false,
  updatedAt,
  onRefresh,
}: {
  displayName: string;
  loading: boolean;
  refreshing?: boolean;
  updatedAt: Date | null;
  onRefresh: () => void;
}) {
  const t = useTranslations("dashboard");
  const tCommon = useTranslations("common");
  const locale = useLocale();
  const greeting = t(greetingKey(new Date().getHours()));
  const name = displayName || "—";

  return (
    <header
      data-testid="dashboard-compact-header"
      className="flex flex-col gap-4 border-b border-ecmp-border/50 pb-5 sm:flex-row sm:items-end sm:justify-between"
    >
      <div className="min-w-0">
        {loading ? (
          <div className="max-w-md space-y-2" aria-busy="true">
            <Skeleton rows={2} />
          </div>
        ) : (
          <>
            <p className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-primary">
              ECMP
            </p>
            <h1 className={`mt-1 ${DASHBOARD_TITLE}`}>{t("title")}</h1>
            <p className={`mt-2 ${DASHBOARD_BODY}`}>
              <span className="font-medium text-ecmp-text-primary">
                {greeting} {name}.
              </span>{" "}
              <span className={DASHBOARD_CAPTION}>{t("compactSummary")}</span>
            </p>
          </>
        )}
      </div>

      <div className="flex shrink-0 flex-col items-stretch gap-2 sm:items-end">
        <div
          className="inline-flex rounded-full border border-ecmp-border/70 bg-ecmp-surface p-1 shadow-ecmp-sm"
          role="group"
          aria-label={t("periodGroup")}
        >
          <span className="rounded-full bg-ecmp-primary px-3 py-1.5 text-[length:var(--ecmp-font-overline-size)] font-semibold text-ecmp-primary-foreground">
            {t("periodToday")}
          </span>
          <button
            type="button"
            disabled
            title={t("periodUnavailable")}
            className="cursor-not-allowed rounded-full px-3 py-1.5 text-[length:var(--ecmp-font-overline-size)] font-medium text-ecmp-text-secondary opacity-55"
          >
            {t("period7d")}
          </button>
          <button
            type="button"
            disabled
            title={t("periodUnavailable")}
            className="cursor-not-allowed rounded-full px-3 py-1.5 text-[length:var(--ecmp-font-overline-size)] font-medium text-ecmp-text-secondary opacity-55"
          >
            {t("period30d")}
          </button>
        </div>
        <div className="flex items-center justify-end gap-2">
          <span className={DASHBOARD_CAPTION}>
            {updatedAt
              ? `${t("lastSynchronized")} ${formatDateTime(updatedAt, locale, {
                  hour: "2-digit",
                  minute: "2-digit",
                })}`
              : t("syncPending")}
          </span>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onRefresh}
            disabled={loading || refreshing}
            aria-label={
              loading || refreshing ? tCommon("refreshing") : tCommon("refresh")
            }
          >
            {loading || refreshing ? tCommon("refreshing") : tCommon("refresh")}
          </Button>
        </div>
      </div>
    </header>
  );
}
