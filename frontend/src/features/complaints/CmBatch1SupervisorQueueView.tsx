"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
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
  Empty,
  ErrorState,
  FilterBar,
  PageContainer,
  PageHeader,
  SectionHeader,
  Select,
  Skeleton,
  StatCard,
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
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
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
          : t("unableToLoadQueue"),
      );
    } finally {
      setLoading(false);
    }
  }, [agingHours, canRead, t]);

  useEffect(() => {
    void load();
  }, [load]);

  const threshold = data?.agingThresholdHours ?? agingHours;

  const laterColumns: TableColumn<CmBatch1LaterReviewWorkItem>[] = [
    {
      key: "workItemId",
      header: t("workItem"),
      cell: (row) => (
        <span className="font-mono text-[length:var(--ecmp-font-body-small-size)]">{row.workItemId}</span>
      ),
    },
    {
      key: "complaintId",
      header: t("title"),
      cell: (row) =>
        row.complaintId ? (
          <Link
            href={`/complaints/cm/${encodeURIComponent(row.complaintId)}`}
            className="font-mono text-[length:var(--ecmp-font-body-small-size)] text-ecmp-primary underline-offset-2 hover:underline"
          >
            {row.complaintId}
          </Link>
        ) : (
          <span className="text-ecmp-text-secondary">—</span>
        ),
    },
    {
      key: "customerId",
      header: t("customer"),
      cell: (row) => row.customerId,
    },
    {
      key: "reason",
      header: t("reason"),
      cell: (row) => (
        <span className="inline-flex flex-wrap items-center gap-1">
          <Badge tone={cmBatch1LaterReviewReasonTone(row.reason)}>
            {(row.reason ?? "").trim()
              ? cmBatch1LaterReviewReasonLabel(row.reason)
              : t("emptyReason")}
          </Badge>
          {cmBatch1LaterReviewReasonIsUnknown(row.reason) ? (
            <Badge tone="neutral">{t("unknownType")}</Badge>
          ) : null}
        </span>
      ),
    },
    {
      key: "status",
      header: t("status"),
      cell: (row) => cmBatch1SupervisorStatusLabel(row.status),
    },
    {
      key: "ageHours",
      header: t("ageHours"),
      cell: (row) => String(row.ageHours),
    },
    {
      key: "createdAt",
      header: t("createdAt"),
      cell: (row) => formatWhen(row.createdAt),
    },
  ];

  const agingColumns: TableColumn<CmBatch1AgingComplaintItem>[] = [
    {
      key: "complaintNumber",
      header: t("title"),
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
      header: t("customer"),
      cell: (row) => row.customerId,
    },
    {
      key: "status",
      header: t("status"),
      cell: (row) => cmBatch1SupervisorStatusLabel(row.status),
    },
    {
      key: "subject",
      header: t("subject"),
      cell: (row) => row.subject ?? "—",
    },
    {
      key: "priority",
      header: t("priority"),
      cell: (row) => row.priority ?? "—",
    },
    {
      key: "caseCreated",
      header: t("caseCreatedColumn"),
      cell: (row) => (row.caseCreated ? tCommon("yes") : tCommon("no")),
    },
    {
      key: "ageHours",
      header: t("ageHours"),
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
      header: t("registered"),
      cell: (row) => formatWhen(row.createdAt),
    },
  ];

  if (!canRead) {
    return (
      <PageContainer>
        <PageHeader
          title={t("batchSupervisorQueue")}
          breadcrumbs={[
            { label: t("home"), href: "/dashboard" },
            { label: t("title"), href: "/complaints" },
            { label: t("batchSupervisorQueue") },
          ]}
        />
        <Empty
          title={t("accessRestricted")}
          description={t("noPermissionToView")}
        />
      </PageContainer>
    );
  }

  const laterCount = data?.laterReviewItems.length ?? 0;
  const agingCount = data?.agingComplaints.length ?? 0;

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={t("batchSupervisorQueue")}
        breadcrumbs={[
          { label: t("home"), href: "/dashboard" },
          { label: t("title"), href: "/complaints" },
          { label: t("batchSupervisorQueue") },
        ]}
        description={t("laterReviewDescription")}
        actions={
          <Button type="button" variant="secondary" onClick={() => void load()}>
            {tCommon("refresh")}
          </Button>
        }
      />

      <FilterBar
        filters={
          <Select
            name="agingHours"
            label={t("agingThreshold")}
            value={String(agingHours)}
            onChange={(e) => setAgingHours(Number(e.target.value))}
            options={[
              { value: "24", label: "24h" },
              { value: "48", label: "48h" },
              { value: "72", label: "72h" },
              { value: "168", label: "7d" },
            ]}
          />
        }
      />

      {error ? (
        <ErrorState title={t("unableToLoadQueue")} message={error} />
      ) : null}

      {data ? (
        <div className="grid grid-cols-1 gap-[var(--ecmp-card-gap)] sm:grid-cols-2">
          <StatCard
            title={t("laterReviewItems")}
            value={<span className="tabular-nums">{laterCount}</span>}
          />
          <StatCard
            title={t("noCaseAging")}
            value={<span className="tabular-nums">{agingCount}</span>}
            variant={agingCount > 0 ? "emphasis" : "default"}
          />
        </div>
      ) : null}

      <section className="space-y-[var(--ecmp-panel-gap)]">
        <SectionHeader
          title={t("laterReviewItems")}
          description={t("laterReviewDescription")}
        />
        <Card>
          <CardBody>
            {loading && !data ? (
              <Skeleton className="h-32 w-full" />
            ) : !data?.laterReviewItems.length ? (
              <Empty
                title={t("noOpenLaterReview")}
                description={t("queueEmptyForFilter")}
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
      </section>

      <section className="space-y-[var(--ecmp-panel-gap)]">
        <SectionHeader
          title={t("noCaseAging")}
          description={t("noCaseAgingDescription", { hours: threshold })}
        />
        <Card>
          <CardBody>
            {loading && !data ? (
              <Skeleton className="h-32 w-full" />
            ) : !data?.agingComplaints.length ? (
              <Empty
                title={t("noAgingComplaints")}
                description={t("noRegisteredPastThreshold")}
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
      </section>

      {data ? (
        <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
          {t("snapshotAsOf", {
            date: formatWhen(data.asOf),
            hours: data.agingThresholdHours,
            later: data.laterReviewItems.length,
            aging: data.agingComplaints.length,
          })}
        </p>
      ) : null}
    </PageContainer>
  );
}
