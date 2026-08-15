"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  Button,
  Empty,
  ErrorState,
  PageContainer,
  PageHeader,
} from "@/shared/ui";
import { BranchPerformancePanel } from "./BranchPerformancePanel";
import { InsightsPanel } from "./InsightsPanel";
import { OperationalHealthPanel } from "./OperationalHealthPanel";
import { ReportSummaryCards } from "./ReportSummaryCards";
import { ResolutionEffectivenessPanel } from "./ResolutionEffectivenessPanel";
import { useReportsData } from "./useReportsData";

export function ReportsWorkspace() {
  const router = useRouter();
  const { hasPermission } = useAuth();
  const t = useTranslations("reports");
  const tCommon = useTranslations("common");
  const canRead = hasPermission("reports:read") || hasPermission("*");
  const { state, reload } = useReportsData();
  const loading = state.status === "loading" || state.status === "idle";
  const data = state.status === "success" ? state.data : null;

  useEffect(() => {
    if (!canRead) return;
    void reload();
  }, [canRead, reload]);

  const refreshAction = (
    <Button
      variant="outline"
      onClick={() => void reload()}
      disabled={loading}
      className="min-h-[var(--ecmp-touch-min)]"
    >
      {loading ? tCommon("refreshing") : t("refreshReport")}
    </Button>
  );

  if (!canRead) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <PageHeader
          overline={t("overline")}
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
          primaryAction={{
            label: tCommon("goHome"),
            onClick: () => router.push("/dashboard"),
          }}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        overline={t("overline")}
        title={t("title")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title") },
        ]}
        description={t("singleSourceDescription")}
        actions={refreshAction}
      />

      {state.status === "error" ? (
        <ErrorState
          title={t("unableToLoad")}
          message={state.error}
          actionLabel={t("refreshReport")}
          onRetry={() => void reload()}
        />
      ) : (
        <div className="flex flex-col gap-[var(--ecmp-section-gap)]">
          <ReportSummaryCards
            summary={data?.summary ?? null}
            loading={loading}
          />

          <BranchPerformancePanel
            rows={data?.byBranch ?? null}
            loading={loading}
          />

          <ResolutionEffectivenessPanel
            rows={data?.byStatus ?? data?.summary?.byStatus ?? null}
            loading={loading}
          />

          <OperationalHealthPanel
            summary={data?.summary ?? null}
            loading={loading}
          />

          <InsightsPanel
            byStatus={data?.byStatus ?? data?.summary?.byStatus ?? null}
            byBranch={data?.byBranch ?? null}
            loading={loading}
          />
        </div>
      )}
    </PageContainer>
  );
}
