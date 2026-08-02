"use client";

import { useEffect } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  Button,
  Empty,
  ErrorState,
  PageContainer,
  PageHeader,
} from "@/shared/ui";
import { ComplaintByBranch } from "./ComplaintByBranch";
import { ComplaintByStatus } from "./ComplaintByStatus";
import { LatestComplaints } from "./LatestComplaints";
import { QuickActions } from "./QuickActions";
import { RecentActivity } from "./RecentActivity";
import { SlaCards } from "./SlaCards";
import { SummaryCards } from "./SummaryCards";
import { useDashboardData } from "./useDashboardData";

export function DashboardView() {
  const { user, hasPermission } = useAuth();
  const t = useTranslations("dashboard");
  const tCommon = useTranslations("common");
  const canRead = hasPermission("dashboard:read");
  const { state, reload } = useDashboardData();
  const loading = state.status === "loading";
  const data = state.status === "success" ? state.data : null;

  useEffect(() => {
    if (!canRead) return;
    void reload();
  }, [canRead, reload]);

  if (!canRead) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <PageHeader
          title={t("title")}
          breadcrumbs={[
            { label: tCommon("home"), href: "/dashboard" },
            { label: t("title") },
          ]}
        />
        <Empty
          title={t("accessRestricted")}
          description={t("accessRestrictedDescription")}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer className="space-y-[var(--ecmp-dashboard-gap)]">
      <PageHeader
        title={t("title")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title") },
        ]}
        description={t("signedInAs", {
          name: user?.fullName ?? user?.username ?? "",
        })}
        actions={
          <Button
            variant="outline"
            onClick={() => void reload()}
            disabled={loading}
          >
            {loading ? tCommon("refreshing") : tCommon("refresh")}
          </Button>
        }
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
          {/* Top — operational KPIs */}
          <SummaryCards header={data?.header ?? null} loading={loading} />

          {/* Middle — operational widgets */}
          <div className="space-y-[var(--ecmp-section-gap)]">
            <SlaCards sla={data?.sla ?? null} loading={loading} />
            <div className="grid grid-cols-1 gap-[var(--ecmp-card-gap)] lg:grid-cols-2">
              <ComplaintByStatus
                rows={data?.byStatus ?? null}
                loading={loading}
              />
              <ComplaintByBranch
                rows={data?.byBranch ?? null}
                loading={loading}
              />
            </div>
            <LatestComplaints
              rows={data?.latestComplaints ?? null}
              loading={loading}
            />
            <QuickActions onRefresh={() => void reload()} />
          </div>

          {/* Bottom — recent activity */}
          <div id="recent-activity">
            <RecentActivity
              rows={data?.recentActivity ?? null}
              loading={loading}
            />
          </div>
        </>
      )}
    </PageContainer>
  );
}
