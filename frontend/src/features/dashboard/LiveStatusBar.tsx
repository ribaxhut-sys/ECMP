"use client";

import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import type { DashboardResolutionSla } from "@/lib/api/types";
import { IconComplaints } from "@/shared/icons";
import { Skeleton } from "@/shared/ui";
import {
  dashboardEnvironmentLabel,
  resolveSystemHealth,
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
  waitingAssignment = 0,
  escalatePending = 0,
  escalateScheduled = 0,
  pusatQueue = 0,
  pusatFollowUp = 0,
  hqScheduleToday = 0,
  loading,
  refreshing = false,
  error,
  updatedAt,
  onRefresh,
}: {
  sla: DashboardResolutionSla | null;
  waitingAssignment?: number;
  escalatePending?: number;
  escalateScheduled?: number;
  pusatQueue?: number;
  pusatFollowUp?: number;
  hqScheduleToday?: number;
  /** First-load only — drives skeleton + "syncing" health. */
  loading: boolean;
  /** Background / manual refresh — button label only, not health pulse. */
  refreshing?: boolean;
  error: boolean;
  updatedAt: Date | null;
  onRefresh?: () => void;
}) {
  const t = useTranslations("dashboard");
  const tCommon = useTranslations("common");
  const router = useRouter();
  const { hasPermission } = useAuth();
  const canCreate = hasPermission("complaints:create");

  const health = resolveSystemHealth({
    loading,
    error,
    sla,
    waitingAssignment,
    escalatePending,
    escalateScheduled,
    pusatQueue,
    pusatFollowUp,
    hqScheduleToday,
  });
  const env = dashboardEnvironmentLabel();

  const healthLabel =
    health === "healthy"
      ? t("systemHealthy")
      : health === "attention"
        ? t("systemAttention")
        : health === "syncing"
          ? t("systemSyncing")
          : t("systemDegraded");

  const busy = loading || refreshing;

  return (
    // Command bar: scoped to the app's own dark palette (`.dark` cascades
    // --ecmp-* overrides to this subtree only) so it's a deliberate fixed
    // dark accent, independent of whatever theme the rest of the page uses.
    <section
      data-testid="dashboard-live-status"
      aria-label={t("liveStatusBar")}
      className="dark flex h-11 items-center rounded-[var(--ecmp-radius-lg)] bg-ecmp-surface px-4"
    >
      {loading && !updatedAt ? (
        <div className="w-full" aria-busy="true">
          <Skeleton rows={1} />
        </div>
      ) : (
        <div className="flex w-full min-w-0 items-center justify-between gap-3 font-mono text-[12px]">
          <div className="flex min-w-0 flex-wrap items-center gap-x-5 gap-y-0.5">
            <p
              className={`inline-flex items-center gap-1.5 font-medium uppercase tracking-[0.06em] ${HEALTH_TEXT[health]}`}
            >
              <span
                className={`size-1.5 shrink-0 rounded-full ${HEALTH_DOT[health]}`}
                aria-hidden
              />
              <span className="truncate">{healthLabel}</span>
            </p>
          </div>

          <div className="flex shrink-0 items-center gap-3">
            <p className="hidden text-ecmp-text-secondary md:inline">
              {env === "lab"
                ? t("envLab")
                : env === "production"
                  ? t("envProduction")
                  : t("envDevelopment")}
            </p>
            {canCreate ? (
              <button
                type="button"
                onClick={() => router.push("/complaints/new")}
                className="flex items-center gap-1.5 rounded bg-ecmp-primary px-2.5 py-1 font-medium text-ecmp-primary-foreground hover:opacity-90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ecmp-focus"
              >
                <IconComplaints className="size-3.5 shrink-0" aria-hidden />
                {t("createComplaint")}
              </button>
            ) : null}
            {onRefresh ? (
              <button
                type="button"
                onClick={onRefresh}
                disabled={busy}
                className="rounded px-1.5 py-0.5 font-medium text-ecmp-primary hover:bg-ecmp-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ecmp-focus disabled:opacity-50"
                aria-label={
                  busy ? tCommon("refreshing") : tCommon("refresh")
                }
              >
                {busy ? tCommon("refreshing") : tCommon("refresh")}
              </button>
            ) : null}
          </div>
        </div>
      )}
    </section>
  );
}
