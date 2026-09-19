"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  fetchCmCases,
  type CmCaseSummary,
} from "@/lib/api";
import {
  Alert,
  Button,
  Empty,
  ErrorState,
  PageContainer,
  PageHeader,
  SectionHeader,
  Skeleton,
  WorkspaceToolbar,
} from "@/shared/ui";
import { useToast } from "@/shared/providers";
import { CaseSummaryCard } from "./CaseSummaryCard";
import { CreateCaseDialog } from "./CreateCaseDialog";
import {
  takeCaseCreatePrefill,
  type CaseCreatePrefill,
} from "./caseCreatePrefill";
import type { CreateCaseFormValues } from "./caseForms";
import { rememberCaseId } from "./caseSessionRegistry";

/**
 * Case List for a Complaint — API-536 with complaintId filter (DEC-024).
 * `?createCase=1` opens handling (create Case) once after Aggregate create, with optional prefill.
 */
export function CaseListView({ complaintId }: { complaintId: string }) {
  const t = useTranslations("cases");
  const tCommon = useTranslations("common");
  const tNav = useTranslations("nav");
  const tErrors = useTranslations("errors");
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { hasPermission } = useAuth();
  const { pushSuccess } = useToast();
  const canRead = hasPermission("complaints:read");
  const canCreate = hasPermission("complaints:create");

  const [cases, setCases] = useState<CmCaseSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [addOpen, setAddOpen] = useState(false);
  const [createInitial, setCreateInitial] = useState<Partial<CreateCaseFormValues> | null>(
    null,
  );
  const autoCreateHandled = useRef(false);

  const reload = useCallback(async () => {
    if (!canRead || !complaintId.trim()) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetchCmCases({
        complaintId: complaintId.trim(),
        page: 1,
        pageSize: 50,
      });
      setCases(res.data ?? []);
    } catch (err) {
      setCases([]);
      setError(
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : t("unableToLoadList"),
      );
    } finally {
      setLoading(false);
    }
  }, [canRead, complaintId, t, tErrors, tCommon]);

  useEffect(() => {
    void reload();
  }, [reload]);

  useEffect(() => {
    if (autoCreateHandled.current) return;
    if (searchParams.get("createCase") !== "1") return;
    if (!canCreate || loading) return;

    autoCreateHandled.current = true;
    const clearQuery = () => {
      router.replace(pathname);
    };

    if (cases.length > 0) {
      clearQuery();
      return;
    }

    const prefill: CaseCreatePrefill | null = takeCaseCreatePrefill(complaintId);
    if (prefill) {
      setCreateInitial({
        caseType: prefill.caseType,
        category: prefill.category,
        subject: prefill.subject,
        description: prefill.description,
        priority: prefill.priority,
        destinationUnitId: prefill.destinationUnitId,
      });
    } else {
      setCreateInitial(null);
    }
    setCreateOpen(true);
    clearQuery();
  }, [
    canCreate,
    cases.length,
    complaintId,
    loading,
    pathname,
    router,
    searchParams,
  ]);

  function onCreated(caseData: { caseId: string; caseNumber: string }) {
    rememberCaseId(complaintId, caseData.caseId);
    pushSuccess(t("success"), t("created", { number: caseData.caseNumber }));
    setCreateInitial(null);
    void reload();
  }

  if (!canRead) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <PageHeader
          title={t("title")}
          breadcrumbs={[
            { label: tCommon("home"), href: "/dashboard" },
            { label: tNav("complaints"), href: "/complaints" },
            { label: t("title") },
          ]}
        />
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

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={t("title")}
        description={t("modeADescription", { id: complaintId })}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: tNav("complaints"), href: "/complaints" },
          {
            label: t("confirmation"),
            href: `/complaints/cm/${encodeURIComponent(complaintId)}`,
          },
          { label: t("title") },
        ]}
        actions={
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push("/complaints/cm/cases")}
            >
              {t("inboxTitle")}
            </Button>
            {canCreate ? (
              <>
                <Button
                  type="button"
                  onClick={() => {
                    setCreateInitial(null);
                    setCreateOpen(true);
                  }}
                >
                  {t("create")}
                </Button>
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => setAddOpen(true)}
                >
                  {t("add")}
                </Button>
              </>
            ) : null}
          </div>
        }
      />

      {loading ? <Skeleton rows={6} /> : null}
      {error ? (
        <ErrorState
          title={t("unableToLoadList")}
          message={error}
          onRetry={() => void reload()}
        />
      ) : null}
      {!loading && !error && cases.length === 0 ? (
        <Empty
          title={t("noCases")}
          description={t("noCasesDescription")}
          primaryAction={
            canCreate
              ? {
                  label: t("create"),
                  onClick: () => {
                    setCreateInitial(null);
                    setCreateOpen(true);
                  },
                }
              : {
                  label: tCommon("refresh"),
                  onClick: () => void reload(),
                }
          }
          secondaryAction={{
            label: t("goToComplaints"),
            onClick: () => router.push("/complaints"),
          }}
        />
      ) : null}
      {!loading && cases.length > 0 ? (
        <section className="space-y-[var(--ecmp-panel-gap)]">
          <SectionHeader
            title={t("title")}
            description={t("modeADescription", { id: complaintId })}
          />
          <WorkspaceToolbar
            summary={tCommon("showingItems", {
              from: cases.length === 0 ? 0 : 1,
              to: cases.length,
              total: cases.length,
            })}
            actions={
              <Button
                type="button"
                size="sm"
                variant="outline"
                onClick={() => void reload()}
              >
                {tCommon("refresh")}
              </Button>
            }
          />
          <div className="grid gap-[var(--ecmp-card-gap)] md:grid-cols-2">
            {cases.map((c) => (
              <CaseSummaryCard key={c.caseId} caseData={c} />
            ))}
          </div>
        </section>
      ) : null}

      {!canCreate ? (
        <Alert
          tone="info"
          title={t("createRestricted")}
          description={t("createPermission")}
        />
      ) : null}

      <CreateCaseDialog
        open={createOpen}
        onClose={() => {
          setCreateOpen(false);
          setCreateInitial(null);
        }}
        complaintId={complaintId}
        mode="create"
        initialValues={createInitial}
        onCreated={onCreated}
      />
      <CreateCaseDialog
        open={addOpen}
        onClose={() => setAddOpen(false)}
        complaintId={complaintId}
        mode="add"
        onCreated={onCreated}
      />
    </PageContainer>
  );
}
