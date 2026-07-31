"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  fetchReportByBranch,
  fetchReportByStatus,
  fetchReportSummary,
} from "@/lib/api";
import type { BranchCount, ReportSummary, StatusCount } from "@/lib/api/types";
import { ComplaintByBranch } from "@/features/dashboard/ComplaintByBranch";
import { ComplaintByStatus } from "@/features/dashboard/ComplaintByStatus";
import {
  Alert,
  Button,
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  Empty,
  Skeleton,
} from "@/shared/ui";

type LoadState =
  | { status: "loading" }
  | {
      status: "success";
      summary: ReportSummary;
      byStatus: StatusCount[];
      byBranch: BranchCount[];
    }
  | { status: "error"; message: string };

export function ReportsView() {
  const { hasPermission } = useAuth();
  const canRead = hasPermission("reports:read") || hasPermission("*");
  const [state, setState] = useState<LoadState>({ status: "loading" });

  const load = useCallback(async () => {
    if (!canRead) {
      setState({ status: "loading" });
      return;
    }
    setState({ status: "loading" });
    try {
      const [summaryRes, statusRes, branchRes] = await Promise.all([
        fetchReportSummary(),
        fetchReportByStatus(),
        fetchReportByBranch(),
      ]);
      setState({
        status: "success",
        summary: summaryRes.data,
        byStatus: statusRes.data,
        byBranch: branchRes.data,
      });
    } catch (err) {
      setState({
        status: "error",
        message:
          err instanceof ApiError
            ? err.message
            : "Unable to load reports.",
      });
    }
  }, [canRead]);

  useEffect(() => {
    void load();
  }, [load]);

  if (!canRead) {
    return (
      <Alert
        tone="warning"
        title="Access restricted"
        description={
          <>
            You need the <code>reports:read</code> permission to view reports.
          </>
        }
      />
    );
  }

  const loading = state.status === "loading";
  const summary = state.status === "success" ? state.summary : null;
  const byStatus = state.status === "success" ? state.byStatus : null;
  const byBranch = state.status === "success" ? state.byBranch : null;

  return (
    <div className="grid gap-6">
      <div className="flex justify-end">
        <Button
          variant="outline"
          onClick={() => void load()}
          disabled={loading}
        >
          {loading ? "Refreshing…" : "Refresh"}
        </Button>
      </div>

      {state.status === "error" ? (
        <Alert
          tone="danger"
          title="Unable to load reports"
          description={state.message}
        />
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>Summary</CardTitle>
        </CardHeader>
        <CardBody>
          {loading ? (
            <Skeleton rows={2} />
          ) : summary ? (
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
                  Total complaints
                </p>
                <p className="mt-1 text-[length:var(--ecmp-font-heading-size)] font-semibold tabular-nums">
                  {summary.total}
                </p>
              </div>
              <div>
                <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
                  Status buckets
                </p>
                <p className="mt-1 text-[length:var(--ecmp-font-heading-size)] font-semibold tabular-nums">
                  {summary.byStatus.length}
                </p>
              </div>
            </div>
          ) : (
            <Empty
              title="No summary"
              description="Report summary will appear once complaints exist."
            />
          )}
        </CardBody>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <ComplaintByStatus rows={byStatus} loading={loading} />
        <ComplaintByBranch rows={byBranch} loading={loading} />
      </div>
    </div>
  );
}
