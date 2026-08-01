"use client";

import { useCallback, useEffect, useState } from "react";
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
          err instanceof ApiError ? `${id}: ${err.message}` : `${id}: failed`,
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
    setToastMessage(`Case ${caseData.caseNumber} created.`);
    setToastOpen(true);
    void reload();
  }

  if (!canRead) {
    return (
      <PageContainer className="space-y-6">
        <PageHeader
          title="Cases"
          breadcrumbs={[
            { label: "Home", href: "/dashboard" },
            { label: "Complaints", href: "/complaints" },
            { label: "Cases" },
          ]}
        />
        <Empty
          title="Permission denied"
          description="complaints:read is required to view cases."
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title="Cases"
        description={`Complaint ${complaintId} — CAP-008 Mode A (session-known cases; no List API).`}
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Complaints", href: "/complaints" },
          {
            label: "Confirmation",
            href: `/complaints/cm/${encodeURIComponent(complaintId)}`,
          },
          { label: "Cases" },
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
            >
              Back
            </Button>
            {canCreate ? (
              <>
                <Button type="button" onClick={() => setCreateOpen(true)}>
                  Create Case
                </Button>
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => setAddOpen(true)}
                >
                  Add Case
                </Button>
              </>
            ) : null}
          </div>
        }
      />

      {loading ? <Skeleton rows={4} /> : null}
      {error ? (
        <ErrorState title="Unable to load cases" message={error} />
      ) : null}
      {!loading && !error && cases.length === 0 ? (
        <Empty
          title="No cases in this session"
          description="Mode A has no Case List API. Create or Add a Case, or open a Case by ID from confirmation."
          action={
            canCreate ? (
              <Button type="button" onClick={() => setCreateOpen(true)}>
                Create Case
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
          title="Create restricted"
          description="Create/Add Case requires complaints:create permission."
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
        title="Success"
        description={toastMessage}
        tone="success"
      />
    </PageContainer>
  );
}
