"use client";

import { useMemo } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import {
  Alert,
  Card,
  CardBody,
  Empty,
  PageContainer,
  PageHeader,
  ProgressMeter,
  SectionHeader,
  Table,
  type ProgressMeterTone,
  type TableColumn,
} from "@/shared/ui";
import { useInternalComplaints } from "./mock/useInternalComplaints";
import { sortByMostRecent } from "./internalComplaintsFilters";
import {
  countByHandlingUnit,
  countByPriority,
  countByStatus,
  maxCount,
} from "./internalReportStats";
import { INTERNAL_PRIORITIES, STATUS_TONE, type InternalComplaint } from "./types";
import {
  InternalStatusBadge,
  InternalTransferRequestBadge,
  InternalWithdrawRequestBadge,
} from "./components/InternalBadges";

/** Badge tone → progress-bar tone. Internal statuses only use these four. */
const BADGE_TONE_TO_METER_TONE: Record<string, ProgressMeterTone> = {
  info: "normal",
  primary: "normal",
  warning: "attention",
  success: "healthy",
  danger: "critical",
  neutral: "normal",
};

export function InternalReportsView() {
  const router = useRouter();
  const t = useTranslations("internalComplaints");
  const tPriority = useTranslations("priority");
  const tCommon = useTranslations("common");
  const { rows, loading, error } = useInternalComplaints();

  const statusBuckets = useMemo(() => countByStatus(rows), [rows]);
  const unitBuckets = useMemo(
    () => countByHandlingUnit(rows).slice(0, 6),
    [rows],
  );
  const priorityCounts = useMemo(() => countByPriority(rows), [rows]);
  const statusMax = maxCount(statusBuckets);
  const unitMax = maxCount(unitBuckets);
  const priorityMax = maxCount(
    INTERNAL_PRIORITIES.map((p) => ({ count: priorityCounts[p] })),
  );

  const sorted = useMemo(() => sortByMostRecent(rows), [rows]);

  const columns: TableColumn<InternalComplaint>[] = [
    {
      key: "number",
      header: t("number"),
      cell: (row) => (
        <button
          type="button"
          className="font-medium text-ecmp-primary underline-offset-2 hover:underline"
          onClick={() =>
            router.push(`/internal/complaints/${encodeURIComponent(row.id)}`)
          }
        >
          {row.number}
        </button>
      ),
    },
    { key: "title", header: t("titleField"), cell: (row) => row.title },
    { key: "handling", header: t("handlingUnit"), cell: (row) => row.handlingUnitId },
    {
      key: "status",
      header: t("status"),
      cell: (row) => (
        <div className="flex flex-wrap gap-1">
          <InternalStatusBadge status={row.status} />
          <InternalTransferRequestBadge status={row.transferRequestStatus} />
          <InternalWithdrawRequestBadge status={row.withdrawRequestStatus} />
        </div>
      ),
    },
  ];

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={t("reportsTitle")}
        description={t("reportsDescription")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title"), href: "/internal" },
          { label: t("reportsTitle") },
        ]}
      />
      {error ? <Alert tone="danger" title={error} /> : null}

      {!loading && rows.length === 0 ? (
        <Empty title={t("listEmpty")} description={t("listEmptyDescription")} />
      ) : (
        <>
          <section className="space-y-[var(--ecmp-panel-gap)]">
            <SectionHeader
              title={t("reportsBreakdownTitle")}
              description={t("reportsBreakdownDescription", { total: rows.length })}
            />
            <div className="grid gap-[var(--ecmp-card-gap)] lg:grid-cols-3">
              <Card>
                <h3 className="mb-3 text-[length:var(--ecmp-font-helper-size)] font-semibold uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                  {t("reportsByStatus")}
                </h3>
                <div className="space-y-3">
                  {statusBuckets.map((bucket) => (
                    <ProgressMeter
                      key={bucket.key}
                      value={bucket.count}
                      max={statusMax || 1}
                      showValue={false}
                      tone={BADGE_TONE_TO_METER_TONE[STATUS_TONE[bucket.key as keyof typeof STATUS_TONE]] ?? "normal"}
                      label={`${t(bucket.labelKey)} · ${bucket.count}`}
                    />
                  ))}
                </div>
              </Card>

              <Card>
                <h3 className="mb-3 text-[length:var(--ecmp-font-helper-size)] font-semibold uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                  {t("reportsByUnit")}
                </h3>
                {unitBuckets.length === 0 ? (
                  <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                    {t("listEmpty")}
                  </p>
                ) : (
                  <div className="space-y-3">
                    {unitBuckets.map((bucket) => (
                      <ProgressMeter
                        key={bucket.unitId}
                        value={bucket.count}
                        max={unitMax || 1}
                        showValue={false}
                        tone="normal"
                        label={`${bucket.unitId} · ${bucket.count}`}
                      />
                    ))}
                  </div>
                )}
              </Card>

              <Card>
                <h3 className="mb-3 text-[length:var(--ecmp-font-helper-size)] font-semibold uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                  {t("reportsByPriority")}
                </h3>
                <div className="space-y-3">
                  {INTERNAL_PRIORITIES.map((priority) => (
                    <ProgressMeter
                      key={priority}
                      value={priorityCounts[priority]}
                      max={priorityMax || 1}
                      showValue={false}
                      tone={
                        priority === "CRITICAL"
                          ? "critical"
                          : priority === "HIGH"
                            ? "attention"
                            : "normal"
                      }
                      label={`${tPriority(priority)} · ${priorityCounts[priority]}`}
                    />
                  ))}
                </div>
              </Card>
            </div>
          </section>

          <Card>
            <CardBody>
              {loading ? (
                <Empty title={tCommon("loading")} description="" />
              ) : (
                <Table columns={columns} rows={sorted} getRowKey={(row) => row.id} />
              )}
            </CardBody>
          </Card>
        </>
      )}
    </PageContainer>
  );
}
