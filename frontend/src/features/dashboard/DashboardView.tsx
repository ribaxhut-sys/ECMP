"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import { ComplaintByBranch } from "./ComplaintByBranch";
import { ComplaintByStatus } from "./ComplaintByStatus";
import { LatestComplaints } from "./LatestComplaints";
import { QuickActions } from "./QuickActions";
import { SummaryCards } from "./SummaryCards";
import { ErrorBanner } from "./ui";
import { useDashboardData } from "./useDashboardData";

export function DashboardView() {
  const router = useRouter();
  const { status, user, logout } = useAuth();
  const { state, reload } = useDashboardData();
  const loading = state.status === "loading";
  const data = state.status === "success" ? state.data : null;

  useEffect(() => {
    if (status === "unauthenticated") {
      router.replace("/login");
    }
  }, [status, router]);

  useEffect(() => {
    if (status === "authenticated") {
      void reload();
    }
  }, [status, reload]);

  if (status === "loading" || status === "unauthenticated") {
    return (
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-8">
        <p className="text-sm text-[var(--muted)]">Loading session…</p>
      </div>
    );
  }

  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-8 sm:px-6 lg:px-8">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-[var(--accent)]">
            ECMP v1.0
          </p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">
            Dashboard
          </h1>
          <p className="mt-2 max-w-2xl text-sm text-[var(--muted)] sm:text-base">
            Signed in as {user?.fullName ?? user?.username}. Live complaint
            summary from report and complaint APIs.
          </p>
        </div>
        <div className="flex flex-wrap gap-2 self-start">
          <button
            type="button"
            onClick={() => void reload()}
            disabled={loading}
            className="rounded-lg border border-white/15 bg-white/5 px-4 py-2 text-sm font-medium transition hover:bg-white/10 disabled:opacity-50"
          >
            {loading ? "Refreshing…" : "Refresh"}
          </button>
          <button
            type="button"
            onClick={() => {
              void logout().then(() => router.replace("/login"));
            }}
            className="rounded-lg border border-white/15 bg-white/5 px-4 py-2 text-sm font-medium transition hover:bg-white/10"
          >
            Sign out
          </button>
        </div>
      </header>

      {state.status === "error" ? (
        <ErrorBanner
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
    </div>
  );
}
