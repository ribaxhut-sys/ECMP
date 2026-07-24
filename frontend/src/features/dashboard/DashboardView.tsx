"use client";

import { useEffect } from "react";
import { useAuth } from "@/auth/AuthProvider";
import {
  Button,
  ErrorState,
  PageContainer,
  PageHeader,
} from "@/shared/ui";
import { QuickActions } from "./QuickActions";
import { RecentActivity } from "./RecentActivity";
import { SlaCards } from "./SlaCards";
import { SummaryCards } from "./SummaryCards";
import { useDashboardData } from "./useDashboardData";

export function DashboardView() {
  const { user } = useAuth();
  const { state, reload } = useDashboardData();
  const loading = state.status === "loading";
  const data = state.status === "success" ? state.data : null;

  useEffect(() => {
    void reload();
  }, [reload]);

  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title="Dashboard"
        breadcrumbs={[{ label: "Home", href: "/dashboard" }, { label: "Dashboard" }]}
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
