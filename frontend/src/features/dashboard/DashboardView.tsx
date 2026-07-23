"use client";

import { useEffect } from "react";
import { useAuth } from "@/auth/AuthProvider";
import {
  Button,
  ErrorState,
  PageContainer,
  PageHeader,
} from "@/shared/ui";
import { ComplaintByBranch } from "./ComplaintByBranch";
import { ComplaintByStatus } from "./ComplaintByStatus";
import { LatestComplaints } from "./LatestComplaints";
import { QuickActions } from "./QuickActions";
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
            Signed in as {user?.fullName ?? user?.username}. Live complaint
            summary from report and complaint APIs.
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
          <SummaryCards summary={data?.summary ?? null} loading={loading} />

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

          <div id="latest-complaints">
            <LatestComplaints
              rows={data?.latestComplaints ?? null}
              loading={loading}
            />
          </div>

          <QuickActions onRefresh={() => void reload()} />
        </>
      )}
    </PageContainer>
  );
}
