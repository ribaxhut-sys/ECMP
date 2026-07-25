"use client";

import { useEffect } from "react";
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
      <PageContainer className="space-y-6">
        <PageHeader
          title="Dashboard"
          breadcrumbs={[
            { label: "Home", href: "/dashboard" },
            { label: "Dashboard" },
          ]}
        />
        <Empty
          title="Access restricted"
          description="You need the dashboard:read permission to view the dashboard."
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title="Dashboard"
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Dashboard" },
        ]}
        description={
          <>
            Signed in as {user?.fullName ?? user?.username}. Live summary from
            the Dashboard API.
          </>
        }
        actions={
          <Button
            variant="outline"
            onClick={() => void reload()}
            disabled={loading}
          >
            {loading ? "Refreshing…" : "Refresh"}
          </Button>
        }
      />

      {state.status === "error" ? (
        <ErrorState
          title="Unable to load dashboard"
          message={state.error}
          code={state.code}
          onRetry={() => void reload()}
        />
      ) : (
        <>
          <SummaryCards header={data?.header ?? null} loading={loading} />
          <SlaCards sla={data?.sla ?? null} loading={loading} />
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
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
          <div id="recent-activity">
            <RecentActivity
              rows={data?.recentActivity ?? null}
              loading={loading}
            />
          </div>
          <QuickActions onRefresh={() => void reload()} />
        </>
      )}
    </PageContainer>
  );
}
