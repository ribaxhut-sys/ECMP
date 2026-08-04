"use client";

import { useEffect, useMemo, useState } from "react";
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
import { DASHBOARD_CARD_GAP, DASHBOARD_SHELL } from "./dashboardUtils";
import { LiveStatusBar } from "./LiveStatusBar";
import { OperationBriefing } from "./OperationBriefing";
import { OperatorRail } from "./OperatorRail";
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
  const { state, reload } = useDashboardData();
  const loading = state.status === "loading";
  const data = state.status === "success" ? state.data : null;
  const [updatedAt, setUpdatedAt] = useState<Date | null>(null);

  useEffect(() => {
    if (!canRead) return;
    void reload();
  }, [canRead, reload]);

  useEffect(() => {
    if (state.status === "success") {
      setUpdatedAt(new Date());
    }
  }, [state.status, data]);

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
  const refreshing = loading && Boolean(data);

  return (
    <div className={DASHBOARD_SHELL}>
      <LiveStatusBar
        sla={data?.sla ?? null}
        loading={firstLoad}
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
          <OperationBriefing
            header={data?.header ?? null}
            sla={data?.sla ?? null}
            byStatus={data?.byStatus ?? null}
            loading={firstLoad}
            refreshing={refreshing}
            onRefresh={() => void reload()}
          />

          <SummaryCards
            header={data?.header ?? null}
            sla={data?.sla ?? null}
            byStatus={data?.byStatus ?? null}
            loading={firstLoad}
            onRefresh={() => void reload()}
          />

          {/* Queue Health = visual anchor */}
          <div className={`grid grid-cols-1 ${DASHBOARD_CARD_GAP} xl:grid-cols-12`}>
            <div className="xl:col-span-8">
              <QueueHealth
                header={data?.header ?? null}
                sla={data?.sla ?? null}
                byStatus={data?.byStatus ?? null}
                loading={firstLoad}
                onRefresh={() => void reload()}
              />
            </div>
            <div className="xl:col-span-4">
              <ComplaintByStatus
                rows={data?.byStatus ?? null}
                loading={firstLoad}
                onRefresh={() => void reload()}
              />
            </div>
          </div>

          <CriticalAlerts
            sla={data?.sla ?? null}
            byStatus={data?.byStatus ?? null}
            loading={firstLoad}
            onRefresh={() => void reload()}
          />

          {/* Operator Rail + Recent Activity */}
          <div className={`grid grid-cols-1 ${DASHBOARD_CARD_GAP} xl:grid-cols-12`}>
            <div className="xl:col-span-4">
              <OperatorRail onRefresh={() => void reload()} />
            </div>
            <div className="xl:col-span-8">
              <RecentActivity
                rows={data?.recentActivity ?? null}
                loading={firstLoad}
                onRefresh={() => void reload()}
              />
            </div>
          </div>

          <div className={`grid grid-cols-1 ${DASHBOARD_CARD_GAP} xl:grid-cols-12`}>
            <div className="xl:col-span-6">
              <ComplaintByBranch
                rows={data?.byBranch ?? null}
                loading={firstLoad}
                onRefresh={() => void reload()}
              />
            </div>
            <div className="xl:col-span-6">
              <SlaCards
                sla={data?.sla ?? null}
                loading={firstLoad}
                onRefresh={() => void reload()}
              />
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
