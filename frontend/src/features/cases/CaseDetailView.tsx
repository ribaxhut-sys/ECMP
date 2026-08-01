"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/auth/AuthProvider";
import { ApiError, fetchCmCase, type CmCase } from "@/lib/api";
import {
  Alert,
  Button,
  Card,
  CardBody,
  CardDescription,
  CardHeader,
  CardTitle,
  Empty,
  ErrorState,
  PageContainer,
  PageHeader,
  Skeleton,
  Toast,
} from "@/shared/ui";
import { CaseStatusBadge } from "./CaseStatusBadge";
import { CloseCaseDialog } from "./CloseCaseDialog";
import { ResolveCaseDialog } from "./ResolveCaseDialog";
import { UpdateStatusDialog } from "./UpdateStatusDialog";
import { rememberCaseId } from "./caseSessionRegistry";
import { allowedStatusTargets, canClose, canResolve } from "./caseStatus";

export function CaseDetailView({ caseId }: { caseId: string }) {
  const router = useRouter();
  const { hasPermission } = useAuth();
  const canRead = hasPermission("complaints:read");
  const canUpdate = hasPermission("complaints:update");

  const [data, setData] = useState<CmCase | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusOpen, setStatusOpen] = useState(false);
  const [resolveOpen, setResolveOpen] = useState(false);
  const [closeOpen, setCloseOpen] = useState(false);
  const [toastOpen, setToastOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState("");

  const reload = useCallback(async () => {
    if (!canRead || !caseId.trim()) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetchCmCase(caseId.trim());
      setData(res.data);
      rememberCaseId(res.data.complaintId, res.data.caseId);
    } catch (err) {
      setData(null);
      setError(
        err instanceof ApiError ? err.message : "Unable to load case.",
      );
    } finally {
      setLoading(false);
    }
  }, [canRead, caseId]);

  useEffect(() => {
    void reload();
  }, [reload]);

  function showSuccess(message: string) {
    setToastMessage(message);
    setToastOpen(true);
  }

  if (!canRead) {
    return (
      <PageContainer className="space-y-6">
        <PageHeader
          title="Case"
          breadcrumbs={[
            { label: "Home", href: "/dashboard" },
            { label: "Complaints", href: "/complaints" },
            { label: "Case" },
          ]}
        />
        <Empty
          title="Permission denied"
          description="complaints:read is required to view a case."
        />
      </PageContainer>
    );
  }

  const statusTargets = data ? allowedStatusTargets(data.status) : [];
  const showStatus = Boolean(data && canUpdate && statusTargets.length > 0);
  const showResolve = Boolean(data && canUpdate && canResolve(data.status));
  const showClose = Boolean(data && canUpdate && canClose(data.status));

  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title={data?.caseNumber ?? "Case"}
        description={data?.subject}
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Complaints", href: "/complaints" },
          ...(data
            ? [
                {
                  label: "Cases",
                  href: `/complaints/cm/${encodeURIComponent(data.complaintId)}/cases`,
                },
              ]
            : []),
          { label: data?.caseNumber ?? "Detail" },
        ]}
        actions={
          <div className="flex flex-wrap gap-2">
            {data ? (
              <Button
                type="button"
                variant="outline"
                onClick={() =>
                  router.push(
                    `/complaints/cm/${encodeURIComponent(data.complaintId)}/cases`,
                  )
                }
              >
                Case list
              </Button>
            ) : null}
            {showStatus ? (
              <Button type="button" onClick={() => setStatusOpen(true)}>
                Update status
              </Button>
            ) : null}
            {showResolve ? (
              <Button type="button" onClick={() => setResolveOpen(true)}>
                Resolve
              </Button>
            ) : null}
            {showClose ? (
              <Button type="button" onClick={() => setCloseOpen(true)}>
                Close case
              </Button>
            ) : null}
          </div>
        }
      />

      {loading ? <Skeleton rows={6} /> : null}
      {!loading && error ? (
        <ErrorState title="Unable to load case" message={error} />
      ) : null}

      {!loading && data ? (
        <>
          <Card>
            <CardHeader className="flex flex-row flex-wrap items-start justify-between gap-3">
              <div className="space-y-1">
                <CardTitle>{data.caseNumber}</CardTitle>
                <CardDescription>
                  Case ID {data.caseId} · Complaint {data.complaintId}
                </CardDescription>
              </div>
              <CaseStatusBadge status={data.status} />
            </CardHeader>
            <CardBody>
              <dl className="grid gap-3 text-[length:var(--ecmp-font-body-size)] sm:grid-cols-2">
                <div>
                  <dt className="text-ecmp-text-secondary">Type</dt>
                  <dd>{data.caseType}</dd>
                </div>
                <div>
                  <dt className="text-ecmp-text-secondary">Priority</dt>
                  <dd>{data.priority}</dd>
                </div>
                <div>
                  <dt className="text-ecmp-text-secondary">Category</dt>
                  <dd>{data.category ?? "—"}</dd>
                </div>
                <div>
                  <dt className="text-ecmp-text-secondary">Owning unit</dt>
                  <dd>{data.owningUnitId ?? "—"}</dd>
                </div>
                <div>
                  <dt className="text-ecmp-text-secondary">Customer</dt>
                  <dd className="font-mono text-xs">{data.customerId}</dd>
                </div>
                <div>
                  <dt className="text-ecmp-text-secondary">Created</dt>
                  <dd>{data.createdAt}</dd>
                </div>
                <div className="sm:col-span-2">
                  <dt className="text-ecmp-text-secondary">Subject</dt>
                  <dd>{data.subject}</dd>
                </div>
                <div className="sm:col-span-2">
                  <dt className="text-ecmp-text-secondary">Description</dt>
                  <dd className="whitespace-pre-wrap">{data.description}</dd>
                </div>
                {data.cancelReason ? (
                  <div>
                    <dt className="text-ecmp-text-secondary">Cancel reason</dt>
                    <dd>{data.cancelReason}</dd>
                  </div>
                ) : null}
                {data.closedAt ? (
                  <div>
                    <dt className="text-ecmp-text-secondary">Closed at</dt>
                    <dd>{data.closedAt}</dd>
                  </div>
                ) : null}
              </dl>
            </CardBody>
          </Card>

          {data.resolution ? (
            <Card>
              <CardHeader>
                <CardTitle>Resolution</CardTitle>
                <CardDescription>
                  {data.resolution.status} · {data.resolution.resolutionCode}
                </CardDescription>
              </CardHeader>
              <CardBody className="space-y-2 text-[length:var(--ecmp-font-body-size)]">
                <p>{data.resolution.summary}</p>
                {data.resolution.detail ? (
                  <p className="text-ecmp-text-secondary whitespace-pre-wrap">
                    {data.resolution.detail}
                  </p>
                ) : null}
                <p className="text-ecmp-text-secondary">
                  Comment: {data.resolution.comment}
                </p>
              </CardBody>
            </Card>
          ) : null}

          {!canUpdate ? (
            <Alert
              tone="info"
              title="Read only"
              description="complaints:update is required to change status, resolve, or close."
            />
          ) : null}
        </>
      ) : null}

      {data ? (
        <>
          <UpdateStatusDialog
            open={statusOpen}
            onClose={() => setStatusOpen(false)}
            caseData={data}
            onUpdated={(next) => {
              setData(next);
              showSuccess(`Status updated to ${next.status}.`);
            }}
          />
          <ResolveCaseDialog
            open={resolveOpen}
            onClose={() => setResolveOpen(false)}
            caseId={data.caseId}
            onResolved={(next) => {
              setData(next);
              showSuccess(`Case ${next.caseNumber} resolved (${next.status}).`);
            }}
          />
          <CloseCaseDialog
            open={closeOpen}
            onClose={() => setCloseOpen(false)}
            caseId={data.caseId}
            onClosed={(next) => {
              setData(next);
              showSuccess(`Case ${next.caseNumber} closed.`);
            }}
          />
        </>
      ) : null}

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
