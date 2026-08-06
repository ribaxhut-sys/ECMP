"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  fetchCmCases,
  type CmCaseSummary,
} from "@/lib/api";
import {
  Button,
  Empty,
  ErrorState,
  PageContainer,
  PageHeader,
  Skeleton,
  WorkspaceToolbar,
} from "@/shared/ui";
import { CaseSummaryCard } from "./CaseSummaryCard";

/**
 * DEC-024 / API-536 — visibility-scoped Case inbox for the signed-in principal.
 */
export function CaseInboxListView() {
  const t = useTranslations("cases");
  const tCommon = useTranslations("common");
  const tTable = useTranslations("table");
  const router = useRouter();
  const { hasPermission } = useAuth();
  const canRead = hasPermission("complaints:read");

  const [rows, setRows] = useState<CmCaseSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const pageSize = 20;

  const load = useCallback(async () => {
    if (!canRead) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetchCmCases({ page, pageSize });
      setRows(res.data ?? []);
      setTotal(res.meta?.totalItems ?? res.data?.length ?? 0);
    } catch (err) {
      setRows([]);
      setTotal(0);
      setError(
        err instanceof ApiError ? err.message : t("unableToLoadList"),
      );
    } finally {
      setLoading(false);
    }
  }, [canRead, page, t]);

  useEffect(() => {
    void load();
  }, [load]);

  if (!canRead) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <PageHeader title={t("inboxTitle")} />
        <Empty
          title={t("accessDenied")}
          description={t("readPermission")}
          primaryAction={{
            label: tCommon("goHome"),
            onClick: () => router.push("/dashboard"),
          }}
        />
      </PageContainer>
    );
  }

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={t("inboxTitle")}
        description={t("inboxDescription")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("inboxTitle") },
        ]}
        actions={
          <Button
            type="button"
            variant="outline"
            onClick={() => router.push("/complaints")}
          >
            {t("goToComplaints")}
          </Button>
        }
      />

      {error ? (
        <ErrorState
          title={t("unableToLoadList")}
          message={error}
          onRetry={() => void load()}
        />
      ) : null}

      {loading && rows.length === 0 ? <Skeleton rows={6} /> : null}

      {!loading && !error && rows.length === 0 ? (
        <Empty
          title={t("inboxEmpty")}
          description={t("inboxEmptyDescription")}
          primaryAction={{
            label: t("goToComplaints"),
            onClick: () => router.push("/complaints"),
          }}
        />
      ) : null}

      {!loading && rows.length > 0 ? (
        <>
          <WorkspaceToolbar
            summary={tTable("itemsInView", { count: rows.length })}
            actions={
              <Button
                type="button"
                size="sm"
                variant="outline"
                onClick={() => void load()}
              >
                {tCommon("refresh")}
              </Button>
            }
          />
          <div className="grid gap-[var(--ecmp-card-gap)] md:grid-cols-2">
            {rows.map((c) => (
              <CaseSummaryCard key={c.caseId} caseData={c} />
            ))}
          </div>
          {totalPages > 1 ? (
            <div className="flex items-center justify-between gap-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={page <= 1 || loading}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
              >
                {tCommon("previous")}
              </Button>
              <span className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                {tCommon("pageOf", { page, totalPages })}
              </span>
              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={page >= totalPages || loading}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              >
                {tCommon("next")}
              </Button>
            </div>
          ) : null}
        </>
      ) : null}
    </PageContainer>
  );
}
