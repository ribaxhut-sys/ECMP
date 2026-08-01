"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { useRouter } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import { ApiError, fetchCmCase, type CmCase } from "@/lib/api";
import {
  Alert,
  Button,
  Empty,
  ErrorState,
  PageContainer,
  PageHeader,
  Skeleton,
  Toast,
} from "@/shared/ui";
import { CaseSummaryCard } from "./CaseSummaryCard";
import { CreateCaseDialog } from "./CreateCaseDialog";
import { listKnownCaseIds, rememberCaseId } from "./caseSessionRegistry";

/**
 * Case List for a Complaint — Mode A has no List API.
 * Loads Case IDs remembered in session (created/added in this browser) and
 * hydrates each via GET /api/v1/cm/cases/{caseId}.
 */
export function CaseListView({ complaintId }: { complaintId: string }) {
  const t = useTranslations("cases");
  const router = useRouter();
  const { hasPermission } = useAuth();
  const canRead = hasPermission("complaints:read");
  const canCreate = hasPermission("complaints:create");

  const [cases, setCases] = useState<CmCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [addOpen, setAddOpen] = useState(false);
  const [toastOpen, setToastOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState("");

  const reload = useCallback(async () => {
    if (!canRead || !complaintId.trim()) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    const ids = listKnownCaseIds(complaintId);
    const loaded: CmCase[] = [];
    const failures: string[] = [];
    for (const id of ids) {
      try {
        const res = await fetchCmCase(id, { complaintId });
        loaded.push(res.data);
      } catch (err) {
        failures.push(
          err instanceof ApiError ? `${id}: ${err.message}` : `${id}: ${t("unableToLoad")}`,
        );
      }
    }
    setCases(loaded);
    if (failures.length && loaded.length === 0) {
      setError(failures.join("; "));
    }
    setLoading(false);
  }, [canRead, complaintId]);

  useEffect(() => {
    void reload();
  }, [reload]);

  function onCreated(caseData: CmCase) {
    rememberCaseId(complaintId, caseData.caseId);
    setToastMessage(t("created", { number: caseData.caseNumber }));
    setToastOpen(true);
    void reload();
  }

  if (!canRead) {
    return (
      <PageContainer className="space-y-6">
        <PageHeader
          title={t("title")}
          breadcrumbs={[
            { label: t("back"), href: "/dashboard" },
            { label: t("confirmation"), href: "/complaints" },
            { label: t("title") },
          ]}
        />
        <Empty
          title={t("accessDenied")}
          description={t("readPermission")}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title={t("title")}
        description={t("modeADescription", { id: complaintId })}
        breadcrumbs={[
          { label: t("back"), href: "/dashboard" },
          { label: t("confirmation"), href: "/complaints" },
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
              onClick={() =>
                router.push(
                  `/complaints/cm/${encodeURIComponent(complaintId)}`,
                )
              }
            >{t("back")}            </Button>
            {canCreate ? (
              <>
                <Button type="button" onClick={() => setCreateOpen(true)}>{t("create")}                </Button>
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => setAddOpen(true)}
                >{t("add")}                </Button>
              </>
            ) : null}
          </div>
        }
      />

      {loading ? <Skeleton rows={4} /> : null}
      {error ? (
        <ErrorState title={t("unableToLoadList")} message={error} />
      ) : null}
      {!loading && !error && cases.length === 0 ? (
        <Empty
          title={t("noSessionCases")}
          description={t("noSessionCasesDescription")}
          action={
            canCreate ? (
              <Button type="button" onClick={() => setCreateOpen(true)}>
                {t("create")}
              </Button>
            ) : undefined
          }
        />
      ) : null}
      {!loading && cases.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2">
          {cases.map((c) => (
            <CaseSummaryCard key={c.caseId} caseData={c} />
          ))}
        </div>
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
        onClose={() => setCreateOpen(false)}
        complaintId={complaintId}
        mode="create"
        onCreated={onCreated}
      />
      <CreateCaseDialog
        open={addOpen}
        onClose={() => setAddOpen(false)}
        complaintId={complaintId}
        mode="add"
        onCreated={onCreated}
      />
      <Toast
        open={toastOpen}
        onClose={() => setToastOpen(false)}
        title={t("success")}
        description={toastMessage}
        tone="success"
      />
    </PageContainer>
  );
}
