"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  fetchCmBatch1SupervisorQueue,
  type CmBatch1AgingComplaintItem,
  type CmBatch1LaterReviewWorkItem,
  type CmBatch1SupervisorQueueResponse,
} from "@/lib/api";
import {
  Badge,
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
  Table,
  type TableColumn,
} from "@/shared/ui";
import {
  CM_BATCH1_SUPERVISOR_QUEUE_LIMIT_DEFAULT,
  cmBatch1LaterReviewReasonIsUnknown,
  cmBatch1LaterReviewReasonLabel,
  cmBatch1LaterReviewReasonTone,
  cmBatch1SupervisorStatusLabel,
  isCmBatch1AgingPastThreshold,
} from "./cmBatch1SupervisorQueue";

function formatWhen(value: string | null | undefined): string {
  if (!value) return "—";
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

/**
 * Mode A Batch-1 supervisor visibility (API-513).
 * Later-review work items + no-Case aging — read-only; no Case create.
 * Status/reason are contract pass-through (no meaning rewrite).
 */
export function CmBatch1SupervisorQueueView() {
  const { hasPermission } = useAuth();
  const canRead = hasPermission("complaints:read");

  const [data, setData] = useState<CmBatch1SupervisorQueueResponse | null>(
    null,
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [agingHours, setAgingHours] = useState(24);

  const load = useCallback(async () => {
    if (!canRead) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetchCmBatch1SupervisorQueue({
        workItemStatus: "OPEN",
        agingHours,
        limit: CM_BATCH1_SUPERVISOR_QUEUE_LIMIT_DEFAULT,
      });
      setData(res.data);
    } catch (err) {
      setData(null);
      setError(
        err instanceof ApiError
          ? err.message
          : "Unable to load supervisor queue",
      );
    } finally {
      setLoading(false);
    }
  }, [agingHours, canRead]);

  useEffect(() => {
    void load();
  }, [load]);

  const threshold = data?.agingThresholdHours ?? agingHours;

  const laterColumns: TableColumn<CmBatch1LaterReviewWorkItem>[] = [
    {
      key: "workItemId",
      header: "Work item",
      cell: (row) => (
        <span className="font-mono text-sm">{row.workItemId}</span>
      ),
    },
    {
      key: "complaintId",
      header: "Complaint",
      cell: (row) =>
        row.complaintId ? (
          <Link
            href={`/complaints/cm/${encodeURIComponent(row.complaintId)}`}
            className="font-mono text-sm text-ecmp-primary underline-offset-2 hover:underline"
          >
            {row.complaintId}
          </Link>
        ) : (
          <span className="text-ecmp-text-secondary">—</span>
        ),
    },
    {
      key: "customerId",
      header: "Customer",
      cell: (row) => row.customerId,
    },
    {
      key: "reason",
      header: "Reason",
      cell: (row) => (
        <span className="inline-flex flex-wrap items-center gap-1">
          <Badge tone={cmBatch1LaterReviewReasonTone(row.reason)}>
            {cmBatch1LaterReviewReasonLabel(row.reason)}
          </Badge>
          {cmBatch1LaterReviewReasonIsUnknown(row.reason) ? (
            <Badge tone="neutral">unknown type</Badge>
          ) : null}
        </span>
      ),
    },
    {
      key: "status",
      header: "Status",
      cell: (row) => cmBatch1SupervisorStatusLabel(row.status),
    },
    {
      key: "ageHours",
      header: "Age (h)",
      cell: (row) => String(row.ageHours),
    },
    {
      key: "createdAt",
      header: "Created",
      cell: (row) => formatWhen(row.createdAt),
    },
  ];

  const agingColumns: TableColumn<CmBatch1AgingComplaintItem>[] = [
    {
      key: "complaintNumber",
      header: "Complaint",
      cell: (row) => (
        <Link
          href={`/complaints/cm/${encodeURIComponent(row.complaintId)}`}
          className="font-medium text-ecmp-primary underline-offset-2 hover:underline"
        >
          {row.complaintNumber}
        </Link>
      ),
    },
    {
      key: "customerId",
      header: "Customer",
      cell: (row) => row.customerId,
    },
    {
      key: "status",
      header: "Status",
      cell: (row) => cmBatch1SupervisorStatusLabel(row.status),
    },
    {
      key: "subject",
      header: "Subject",
      cell: (row) => row.subject ?? "—",
    },
    {
      key: "priority",
      header: "Priority",
      cell: (row) => row.priority ?? "—",
    },
    {
      key: "caseCreated",
      header: "Case",
      cell: (row) => (row.caseCreated ? "yes" : "false"),
    },
    {
      key: "ageHours",
      header: "Age (h)",
      cell: (row) => (
        <Badge
          tone={
            isCmBatch1AgingPastThreshold(row.ageHours, threshold)
              ? "warning"
              : "neutral"
          }
        >
          {row.ageHours}
        </Badge>
      ),
    },
    {
      key: "createdAt",
      header: "Registered",
      cell: (row) => formatWhen(row.createdAt),
    },
  ];

  if (!canRead) {
    return (
      <PageContainer>
        <PageHeader
          title="Batch-1 supervisor queue"
          breadcrumbs={[
            { label: "Home", href: "/dashboard" },
            { label: "Complaints", href: "/complaints" },
            { label: "Supervisor queue" },
          ]}
        />
        <Empty
          title="Access restricted"
          description="complaints:read is required to view later-review and aging items."
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title="Batch-1 supervisor queue"
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Complaints", href: "/complaints" },
          { label: "Supervisor queue" },
        ]}
        description="Later-review work items and Complaints without Case past the aging threshold (Aggregate /api/v1/cm). Read-only — Case create stays Batch 2. API-513 uses limit cap only (no offset pagination)."
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <label className="flex items-center gap-2 text-sm">
              <span className="text-ecmp-text-secondary">Aging ≥</span>
              <select
                className="rounded border border-ecmp-border bg-ecmp-surface px-2 py-1"
                value={agingHours}
                onChange={(e) => setAgingHours(Number(e.target.value))}
                aria-label="Aging threshold hours"
              >
                <option value={24}>24h</option>
                <option value={48}>48h</option>
                <option value={72}>72h</option>
                <option value={168}>7d</option>
              </select>
            </label>
            <Button type="button" variant="secondary" onClick={() => void load()}>
              Refresh
            </Button>
          </div>
        }
      />

      {error ? (
        <ErrorState title="Unable to load queue" message={error} />
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>Later-review work items</CardTitle>
          <CardDescription>
            Degraded duplicate check (FR-003 E1) and failed attachment bind
            (FR-004 E8). OPEN items only. Reason/status pass-through from
            API-513.
          </CardDescription>
        </CardHeader>
        <CardBody>
          {loading && !data ? (
            <Skeleton className="h-32 w-full" />
          ) : !data?.laterReviewItems.length ? (
            <Empty
              title="No open later-review items"
              description="Queue is empty for the current filter."
            />
          ) : (
            <Table
              columns={laterColumns}
              rows={data.laterReviewItems}
              getRowKey={(row) => row.workItemId}
            />
          )}
        </CardBody>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>No-Case aging</CardTitle>
          <CardDescription>
            REGISTERED Aggregate Complaints older than {threshold}h without Case
            (FR-001 A4 / D-02). Follow-up is Batch 2 — not Mode A Case create.
          </CardDescription>
        </CardHeader>
        <CardBody>
          {loading && !data ? (
            <Skeleton className="h-32 w-full" />
          ) : !data?.agingComplaints.length ? (
            <Empty
              title="No aging Complaints"
              description="No REGISTERED items past the selected threshold."
            />
          ) : (
            <Table
              columns={agingColumns}
              rows={data.agingComplaints}
              getRowKey={(row) => row.complaintId}
            />
          )}
        </CardBody>
      </Card>

      {data ? (
        <p className="text-xs text-ecmp-text-secondary">
          Snapshot as of {formatWhen(data.asOf)} · threshold{" "}
          {data.agingThresholdHours}h · later-review{" "}
          {data.laterReviewItems.length} · aging {data.agingComplaints.length}
        </p>
      ) : null}
    </PageContainer>
  );
}
