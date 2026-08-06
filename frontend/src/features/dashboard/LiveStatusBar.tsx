"use client";

import { useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { formatDateTime } from "@/i18n/formatting";
import type { DashboardSlaSummary } from "@/lib/api/types";
import { Skeleton } from "@/shared/ui";
import {
  DASHBOARD_STRIP,
  dashboardEnvironmentLabel,
  resolveSystemHealth,
  secondsSince,
  type SystemHealthKind,
} from "./dashboardUtils";

const HEALTH_DOT: Record<SystemHealthKind, string> = {
  healthy: "bg-ecmp-success",
  attention: "bg-ecmp-warning",
  syncing: "bg-ecmp-info motion-safe:animate-pulse",
  degraded: "bg-ecmp-danger",
};

const HEALTH_TEXT: Record<SystemHealthKind, string> = {
  healthy: "text-ecmp-success-text",
  attention: "text-ecmp-warning-text",
  syncing: "text-ecmp-info-text",
  degraded: "text-ecmp-danger-text",
};

export function LiveStatusBar({
  sla,
  loading,
  error,
  updatedAt,
  onRefresh,
}: {
  sla: DashboardSlaSummary | null;
  loading: boolean;
  error: boolean;
  updatedAt: Date | null;
  onRefresh?: () => void;
}) {
  const t = useTranslations("dashboard");
  const tCommon = useTranslations("common");
  const locale = useLocale();
  const [nowMs, setNowMs] = useState(() => Date.now());

  useEffect(() => {
    const id = window.setInterval(() => setNowMs(Date.now()), 1000);
    return () => window.clearInterval(id);
  }, []);

  const health = resolveSystemHealth({ loading, error, sla });
  const syncSource = updatedAt ?? (loading ? null : new Date(nowMs));
  const ageSec = secondsSince(syncSource, nowMs);
  const env = dashboardEnvironmentLabel();

  const healthLabel =
    health === "healthy"
      ? t("systemHealthy")
      : health === "attention"
        ? t("systemAttention")
        : health === "syncing"
          ? t("systemSyncing")
          : t("systemDegraded");

  return (
    <section
      data-testid="dashboard-live-status"
      aria-label={t("liveStatusBar")}
      className={`${DASHBOARD_STRIP} flex h-9 items-center px-0.5`}
    >
      {loading && !updatedAt ? (
        <div className="w-full" aria-busy="true">
          <Skeleton rows={1} />
        </div>
      ) : (
        <div className="flex w-full min-w-0 items-center justify-between gap-3 text-[12px]">
          <div className="flex min-w-0 flex-wrap items-center gap-x-4 gap-y-0.5">
            <p
              className={`inline-flex items-center gap-1.5 font-medium ${HEALTH_TEXT[health]}`}
            >
              <span
                className={`size-1.5 shrink-0 rounded-full ${HEALTH_DOT[health]}`}
                aria-hidden
              />
              <span className="truncate">{healthLabel}</span>
            </p>

            <p className="hidden tabular-nums text-ecmp-text-secondary sm:inline">
              {syncSource
                ? formatDateTime(syncSource, locale, {
                    hour: "2-digit",
                    minute: "2-digit",
                  })
                : t("syncPending")}
            </p>

            <p
              className="tabular-nums text-ecmp-text-secondary"
              aria-live="polite"
            >
              {ageSec === null
                ? t("syncPending")
                : t("updatedSecondsAgo", { count: ageSec })}
            </p>
          </div>

          <div className="flex shrink-0 items-center gap-3">
            <p className="hidden text-ecmp-text-secondary md:inline">
              {env === "production"
                ? t("envProduction")
                : t("envDevelopment")}
            </p>
            {onRefresh ? (
              <button
                type="button"
                onClick={onRefresh}
                disabled={loading}
                className="rounded px-1 py-0.5 font-medium text-ecmp-primary hover:bg-ecmp-primary-muted/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ecmp-focus disabled:opacity-50"
                aria-label={
                  loading ? tCommon("refreshing") : tCommon("refresh")
                }
              >
                {loading ? tCommon("refreshing") : tCommon("refresh")}
              </button>
            ) : null}
          </div>
        </div>
      )}
    </section>
  );
}
