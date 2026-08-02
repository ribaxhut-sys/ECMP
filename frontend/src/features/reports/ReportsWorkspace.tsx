"use client";

import { useEffect } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { ComplaintByBranch } from "@/features/dashboard/ComplaintByBranch";
import { ComplaintByStatus } from "@/features/dashboard/ComplaintByStatus";
import {
  Button,
  Empty,
  ErrorState,
  PageContainer,
  PageHeader,
} from "@/shared/ui";
import { ReportSummaryCards } from "./ReportSummaryCards";
import { useReportsData } from "./useReportsData";

export function ReportsWorkspace() {
  const { hasPermission } = useAuth();
  const t = useTranslations("reports");
  const tCommon = useTranslations("common");
  const canRead = hasPermission("reports:read") || hasPermission("*");
  const { state, reload } = useReportsData();
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
          description={t("description")}
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
        description={t("description")}
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
          <ReportSummaryCards
            summary={data?.summary ?? null}
            loading={loading}
          />
          <div className="grid grid-cols-1 gap-[var(--ecmp-card-gap)] lg:grid-cols-2">
            <ComplaintByStatus
              rows={data?.byStatus ?? data?.summary?.byStatus ?? null}
              loading={loading}
            />
            <ComplaintByBranch
              rows={data?.byBranch ?? null}
              loading={loading}
            />
          </div>
        </>
      )}
    </PageContainer>
  );
}
