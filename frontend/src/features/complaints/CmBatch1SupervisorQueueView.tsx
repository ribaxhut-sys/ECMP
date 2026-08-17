"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import Link from "next/link";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  fetchCmBatch1SupervisorQueue,
  type CmBatch1AgingComplaintItem,
  type CmBatch1LaterReviewWorkItem,
  type CmBatch1SupervisorQueueResponse,
} from "@/lib/api";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import {
  Badge,
  Button,
  Card,
  CardBody,
  DensityToggle,
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
  WorkspaceToolbar,
  type TableColumn,
  type TableDensity,
} from "@/shared/ui";
import {
  CM_BATCH1_SUPERVISOR_QUEUE_LIMIT_DEFAULT,
  cmBatch1LaterReviewReasonIsUnknown,
  cmBatch1LaterReviewReasonLabel,
  cmBatch1LaterReviewReasonTone,
  cmBatch1SupervisorStatusLabel,
  isCmBatch1AgingPastThreshold,
} from "./cmBatch1SupervisorQueue";
import { formatDateTime24 } from "@/shared/utils/datetime";

/**
 * Mode A Batch-1 supervisor visibility (API-513).
 * Later-review work items + no-Case aging — read-only; no Case create.
 * Status/reason are contract pass-through (no meaning rewrite).
 */
export function CmBatch1SupervisorQueueView() {
  const router = useRouter();
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const locale = useLocale();
  const { hasPermission } = useAuth();
  const canRead = hasPermission("complaints:read");

  const [data, setData] = useState<CmBatch1SupervisorQueueResponse | null>(
    null,
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [agingHours, setAgingHours] = useState(24);
  const [workItemStatus, setWorkItemStatus] = useState<
    "OPEN" | "CLOSED" | "ALL"
  >("OPEN");
  const [density, setDensity] = useState<TableDensity>("comfortable");

  const load = useCallback(async () => {
    if (!canRead) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetchCmBatch1SupervisorQueue({
        workItemStatus,
        agingHours,
        limit: CM_BATCH1_SUPERVISOR_QUEUE_LIMIT_DEFAULT,
      });
      setData(res.data);
    } catch (err) {
      setData(null);
      setError(
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : t("unableToLoadQueue"),
      );
    } finally {
      setLoading(false);
    }
  }, [agingHours, canRead, t, tErrors, tCommon, workItemStatus]);

  useEffect(() => {
    void load();
  }, [load]);

  const threshold = data?.agingThresholdHours ?? agingHours;

  function humanReason(reason: string): string {
    const raw = (reason ?? "").trim();
    if (raw === "duplicate_check_degraded") return t("reasonDuplicateCheckLimited");
    if (raw === "attachment_bind_failed") return t("reasonAttachmentBindFailed");
    return cmBatch1LaterReviewReasonLabel(raw) || t("emptyReason");
  }

  function humanStatus(status: string): string {
    const raw = cmBatch1SupervisorStatusLabel(status);
    if (raw === "REGISTERED") return t("registered");
    if (raw === "OPEN") return t("statusOpen");
    if (raw === "CLOSED") return t("statusClosed");
    return raw;
  }

  const laterColumns: TableColumn<CmBatch1LaterReviewWorkItem>[] = [
    {
      key: "complaintId",
      header: t("title"),
      cell: (row) =>
        row.complaintId ? (
          <Link
            href={`/complaints/cm/${encodeURIComponent(row.complaintId)}`}
            className="font-medium text-ecmp-primary underline-offset-2 hover:underline"
          >
            {t("openComplaint")}
          </Link>
        ) : (
          <span className="text-ecmp-text-secondary">—</span>
        ),
    },
    {
      key: "reason",
      header: t("reason"),
      cell: (row) => (
        <span className="inline-flex flex-wrap items-center gap-1">
          <Badge tone={cmBatch1LaterReviewReasonTone(row.reason)}>
            {humanReason(row.reason)}
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
      cell: (row) => humanStatus(row.status),
    },
    {
      key: "ageHours",
      header: t("ageHours"),
      cell: (row) => String(row.ageHours),
    },
    {
      key: "createdAt",
      header: t("createdAt"),
      cell: (row) => formatDateTime24(row.createdAt, locale, "—"),
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
      key: "status",
      header: t("status"),
      cell: (row) => humanStatus(row.status),
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
      cell: (row) => formatDateTime24(row.createdAt, locale, "—"),
    },
  ];

  if (!canRead) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <PageHeader
          overline={t("overline")}
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
          primaryAction={{
            label: tCommon("goHome"),
            onClick: () => router.push("/dashboard"),
          }}
        />
      </PageContainer>
    );
  }

  const laterCount = data?.laterReviewItems.length ?? 0;
  const agingCount = data?.agingComplaints.length ?? 0;

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        overline={t("overline")}
        title={t("batchSupervisorQueue")}
        breadcrumbs={[
          { label: t("home"), href: "/dashboard" },
          { label: t("title"), href: "/complaints" },
          { label: t("batchSupervisorQueue") },
        ]}
        description={t("laterReviewDescription")}
        actions={
          <Button type="button" variant="outline" onClick={() => void load()}>
            {tCommon("refresh")}
          </Button>
        }
      />

      <FilterBar
        filters={
          <>
            <Select
              name="workItemStatus"
              label={t("laterReviewStatusFilter")}
              value={workItemStatus}
              onChange={(e) =>
                setWorkItemStatus(
                  e.target.value as "OPEN" | "CLOSED" | "ALL",
                )
              }
              options={[
                { value: "OPEN", label: t("statusOpen") },
                { value: "CLOSED", label: t("statusClosed") },
                { value: "ALL", label: t("statusAll") },
              ]}
            />
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
          </>
        }
      />

      {error ? (
        <ErrorState
          title={t("unableToLoadQueue")}
          message={error}
          onRetry={() => void load()}
        />
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
        <Card padding={false} className="overflow-hidden">
          <CardBody className="space-y-[var(--ecmp-panel-gap)] p-4 md:p-6">
            {loading && !data ? (
              <Skeleton rows={6} />
            ) : !data?.laterReviewItems.length ? (
              <Empty
                title={
                  workItemStatus === "CLOSED"
                    ? t("noClosedLaterReview")
                    : workItemStatus === "ALL"
                      ? t("noLaterReviewItems")
                      : t("noOpenLaterReview")
                }
                description={t("queueEmptyForFilter")}
                primaryAction={{
                  label: tCommon("refreshPage"),
                  onClick: () => void load(),
                }}
                secondaryAction={{
                  label: tCommon("goToComplaints"),
                  onClick: () => router.push("/complaints"),
                }}
              />
            ) : (
              <>
                <WorkspaceToolbar
                  summary={tCommon("showingItems", {
                    from: laterCount === 0 ? 0 : 1,
                    to: laterCount,
                    total: laterCount,
                  })}
                  density={
                    <DensityToggle value={density} onChange={setDensity} />
                  }
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
                <Table
                  columns={laterColumns}
                  rows={data.laterReviewItems}
                  getRowKey={(row) => row.workItemId}
                  density={density}
                  stickyHeader
                />
              </>
            )}
          </CardBody>
        </Card>
      </section>

      <section className="space-y-[var(--ecmp-panel-gap)]">
        <SectionHeader
          title={t("noCaseAging")}
          description={t("noCaseAgingDescription", { hours: threshold })}
        />
        <Card padding={false} className="overflow-hidden">
          <CardBody className="space-y-[var(--ecmp-panel-gap)] p-4 md:p-6">
            {loading && !data ? (
              <Skeleton rows={6} />
            ) : !data?.agingComplaints.length ? (
              <Empty
                title={t("noAgingComplaints")}
                description={t("noRegisteredPastThreshold")}
                primaryAction={{
                  label: tCommon("refreshPage"),
                  onClick: () => void load(),
                }}
                secondaryAction={{
                  label: t("clearFilters"),
                  onClick: () => setAgingHours(24),
                }}
              />
            ) : (
              <>
                <WorkspaceToolbar
                  summary={tCommon("showingItems", {
                    from: agingCount === 0 ? 0 : 1,
                    to: agingCount,
                    total: agingCount,
                  })}
                  density={
                    <DensityToggle value={density} onChange={setDensity} />
                  }
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
                <Table
                  columns={agingColumns}
                  rows={data.agingComplaints}
                  getRowKey={(row) => row.complaintId}
                  density={density}
                  stickyHeader
                />
              </>
            )}
          </CardBody>
        </Card>
      </section>

      {data ? (
        <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
          {t("snapshotAsOf", {
            date: formatDateTime24(data.asOf, locale),
            hours: data.agingThresholdHours,
            later: data.laterReviewItems.length,
            aging: data.agingComplaints.length,
          })}
        </p>
      ) : null}
    </PageContainer>
  );
}
