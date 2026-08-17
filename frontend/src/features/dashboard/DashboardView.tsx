"use client";

import { useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  Empty,
  ErrorState,
  PageContainer,
  PageHeader,
} from "@/shared/ui";
import { ComplaintByBranch } from "./ComplaintByBranch";
import { ComplaintByStatus } from "./ComplaintByStatus";
import { CriticalAlerts } from "./CriticalAlerts";
import {
  countByStatus,
  DASHBOARD_CARD_GAP,
  DASHBOARD_SHELL,
  DASHBOARD_TILE_GRID,
  DASHBOARD_ZONE_LABEL,
} from "./dashboardUtils";
import { LiveStatusBar } from "./LiveStatusBar";
import { QueueHealth } from "./QueueHealth";
import { RecentActivity } from "./RecentActivity";
import { SlaCards } from "./SlaCards";
import { SummaryCards } from "./SummaryCards";
import { useDashboardData } from "./useDashboardData";

export function DashboardView() {
  const router = useRouter();
  const { hasPermission } = useAuth();
  const t = useTranslations("dashboard");
  const tCommon = useTranslations("common");
  const canRead = hasPermission("dashboard:read");
  const { state, reload, updatedAt, isFetching } = useDashboardData();
  const loading = state.status === "loading";
  const data = state.status === "success" ? state.data : null;

  useEffect(() => {
    if (!canRead) return;
    void reload();
    // Single mount-time load — useDashboardData owns the recurring poll.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [canRead]);

  const breadcrumbs = useMemo(
    () => [
      { label: tCommon("home"), href: "/dashboard" },
      { label: t("title") },
    ],
    [t, tCommon],
  );

  if (!canRead) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <PageHeader
          overline={t("overline")}
          title={t("title")}
          breadcrumbs={breadcrumbs}
        />
        <Empty
          title={t("accessRestricted")}
          description={t("accessRestrictedDescription")}
          primaryAction={{
            label: tCommon("goHome"),
            onClick: () => router.push("/dashboard"),
          }}
        />
      </PageContainer>
    );
  }

  const firstLoad = loading && !data;

  return (
    <div className={DASHBOARD_SHELL}>
      {/*
        Single refresh control for the whole page. Auto-refreshes every 60s
        (paused off-tab) via useDashboardData — no section below duplicates
        it (see dashboard nav-target audit: every button used to also point
        somewhere else on this same page).
      */}
      <LiveStatusBar
        sla={data?.sla ?? null}
        waitingAssignment={countByStatus(data?.byStatus, "NEW") ?? 0}
        escalatePending={countByStatus(data?.byStatus, "ESCALATED") ?? 0}
        loading={firstLoad || isFetching}
        error={state.status === "error"}
        updatedAt={updatedAt}
        onRefresh={() => void reload()}
      />

      {state.status === "error" ? (
        <ErrorState
          title={t("unableToLoad")}
          message={state.error}
          code={state.code}
          onRetry={() => void reload()}
        />
      ) : (
        <>
          {/*
            Decision zone — one seamless command-center panel: hero number
            and "needs action" fused with hairline dividers, not two
            separate floating cards.
          */}
          <div className={`grid grid-cols-1 xl:grid-cols-12 ${DASHBOARD_TILE_GRID}`}>
            <div className="xl:col-span-8">
              <SummaryCards
                header={data?.header ?? null}
                byStatus={data?.byStatus ?? null}
                trend={data?.trend ?? null}
                loading={firstLoad}
              />
            </div>
            <div className="xl:col-span-4">
              <CriticalAlerts
                byStatus={data?.byStatus ?? null}
                loading={firstLoad}
              />
            </div>
          </div>

          <p className={`${DASHBOARD_ZONE_LABEL} pt-1`}>{t("operationalContext")}</p>

          {/* Queue Health = visual anchor */}
          <div className={`grid grid-cols-1 xl:grid-cols-12 ${DASHBOARD_TILE_GRID}`}>
            <div className="xl:col-span-8">
              <QueueHealth
                header={data?.header ?? null}
                byStatus={data?.byStatus ?? null}
                loading={firstLoad}
              />
            </div>
            <div className="xl:col-span-4">
              <ComplaintByStatus
                rows={data?.byStatus ?? null}
                loading={firstLoad}
              />
            </div>
          </div>

          <RecentActivity />

          <div className={`grid grid-cols-1 ${DASHBOARD_CARD_GAP} xl:grid-cols-12`}>
            <div className="xl:col-span-6">
              <ComplaintByBranch />
            </div>
            <div className="xl:col-span-6">
              <SlaCards sla={data?.sla ?? null} loading={firstLoad} />
            </div>
          </div>
        </>
      )}

      <span className="sr-only" aria-live="polite">
        {updatedAt ? t("lastUpdated") : null}
      </span>
    </div>
  );
}
