"use client";

import { useMemo, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import {
  Alert,
  Button,
  Card,
  CardBody,
  DatePicker,
  Empty,
  ErrorState,
  FilterBar,
  Input,
  PageContainer,
  PageHeader,
  Pagination,
  ProgressMeter,
  SectionHeader,
  Select,
  Skeleton,
  Table,
  WorkspaceToolbar,
  type ProgressMeterTone,
  type SelectOption,
  type TableColumn,
} from "@/shared/ui";
import { formatDate } from "@/i18n/formatting";
import { ApiError, downloadInternalComplaintsReportPdf } from "@/lib/api";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { useInternalComplaints } from "./mock/useInternalComplaints";
import {
  defaultInternalListFilters,
  filterInternalComplaints,
  hasActiveInternalFilters,
  sortByMostRecent,
  type InternalListFilters,
} from "./internalComplaintsFilters";
import {
  countByHandlingUnit,
  countByPriority,
  countByStatus,
  maxCount,
  priorityCountsFromSummary,
  statusBucketsFromSummary,
  unitBucketsFromSummary,
} from "./internalReportStats";
import { useInternalReportSummary } from "./useInternalReportSummary";
import {
  CATEGORY_LABEL_KEY,
  INTERNAL_CATEGORIES,
  INTERNAL_PRIORITIES,
  INTERNAL_STATUSES,
  STATUS_LABEL_KEY,
  STATUS_TONE,
  type InternalComplaint,
} from "./types";
import {
  InternalPriorityBadge,
  InternalStatusBadge,
  InternalTransferRequestBadge,
  InternalWithdrawRequestBadge,
} from "./components/InternalBadges";
import { displayInternalUnitCode } from "./transferDirection";

/** Badge tone → progress-bar tone. Internal statuses only use these four. */
const BADGE_TONE_TO_METER_TONE: Record<string, ProgressMeterTone> = {
  info: "normal",
  primary: "normal",
  warning: "attention",
  success: "healthy",
  danger: "critical",
  neutral: "normal",
};

/** Client-side page window over the filtered rows. */
const REPORT_PAGE_SIZE = 25;

export function InternalReportsView() {
  const router = useRouter();
  const t = useTranslations("internalComplaints");
  const tPriority = useTranslations("priority");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const locale = useLocale();
  const { rows, total, truncated, loading, error, reload } = useInternalComplaints();

  const [filters, setFilters] = useState<InternalListFilters>(
    defaultInternalListFilters,
  );
  const [draft, setDraft] = useState<InternalListFilters>(filters);
  const [page, setPage] = useState(1);
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  // One filtered population feeds BOTH the breakdown cards and the table — a
  // report whose charts disagree with the rows under them is worse than none.
  const filtered = useMemo(
    () => sortByMostRecent(filterInternalComplaints(rows, filters)),
    [rows, filters],
  );

  // The cards are counted by the API over the whole visible population; the
  // client-side counters below are the fallback for when that call fails, and
  // they can only see the rows this browser managed to load.
  const {
    summary,
    loading: summaryLoading,
    error: summaryError,
  } = useInternalReportSummary({
    status: filters.status,
    category: filters.category,
    priority: filters.priority,
    dateFrom: filters.dateFrom,
    dateTo: filters.dateTo,
    q: filters.q,
  });

  const statusBuckets = useMemo(
    () =>
      summary
        ? statusBucketsFromSummary(summary.byStatus)
        : countByStatus(filtered),
    [summary, filtered],
  );
  const unitBuckets = useMemo(
    () =>
      (summary
        ? unitBucketsFromSummary(summary.byHandlingUnit)
        : countByHandlingUnit(filtered)
      ).slice(0, 6),
    [summary, filtered],
  );
  const priorityCounts = useMemo(
    () =>
      summary
        ? priorityCountsFromSummary(summary.byPriority)
        : countByPriority(filtered),
    [summary, filtered],
  );
  const breakdownTotal = summary ? summary.totalItems : filtered.length;
  const statusMax = maxCount(statusBuckets);
  const unitMax = maxCount(unitBuckets);
  const priorityMax = maxCount(
    INTERNAL_PRIORITIES.map((p) => ({ count: priorityCounts[p] })),
  );

  const totalPages = Math.max(1, Math.ceil(filtered.length / REPORT_PAGE_SIZE));
  const currentPage = Math.min(page, totalPages);
  const pageRows = useMemo(
    () =>
      filtered.slice(
        (currentPage - 1) * REPORT_PAGE_SIZE,
        currentPage * REPORT_PAGE_SIZE,
      ),
    [filtered, currentPage],
  );

  function onSubmitFilters(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    setFilters(draft);
    setPage(1);
  }

  function onResetFilters(): void {
    const next = defaultInternalListFilters();
    setDraft(next);
    setFilters(next);
    setPage(1);
  }

  /**
   * Server-rendered report PDF (API-553). The filters are sent along, so the
   * document covers the whole filtered population — not just the page on
   * screen — with the agency letterhead and an audit trail behind it.
   */
  async function onExportPdf(): Promise<void> {
    if (exporting) return;
    setExporting(true);
    setExportError(null);
    try {
      await downloadInternalComplaintsReportPdf({
        status: filters.status,
        category: filters.category,
        priority: filters.priority,
        dateFrom: filters.dateFrom,
        dateTo: filters.dateTo,
        q: filters.q,
      });
    } catch (err: unknown) {
      setExportError(
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : t("reportsExportFailed"),
      );
    } finally {
      setExporting(false);
    }
  }

  const statusOptions: SelectOption[] = [
    { value: "", label: tCommon("all") },
    ...INTERNAL_STATUSES.map((s) => ({
      value: s,
      label: t(STATUS_LABEL_KEY[s]),
    })),
  ];
  const categoryOptions: SelectOption[] = [
    { value: "", label: tCommon("all") },
    ...INTERNAL_CATEGORIES.map((c) => ({
      value: c,
      label: t(CATEGORY_LABEL_KEY[c]),
    })),
  ];
  const priorityOptions: SelectOption[] = [
    { value: "", label: tCommon("all") },
    ...INTERNAL_PRIORITIES.map((p) => ({
      value: p,
      label: tPriority(p),
    })),
  ];

  const columns: TableColumn<InternalComplaint>[] = [
    {
      key: "number",
      header: t("number"),
      cell: (row) => (
        <button
          type="button"
          className="cursor-pointer text-left font-medium text-ecmp-primary underline-offset-2 hover:underline"
          onClick={() =>
            router.push(`/internal/complaints/${encodeURIComponent(row.id)}`)
          }
        >
          {row.number}
        </button>
      ),
    },
    { key: "title", header: t("titleField"), cell: (row) => row.title },
    {
      key: "handling",
      header: t("handlingUnit"),
      cell: (row) => displayInternalUnitCode(row.handlingUnitId),
    },
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
    {
      key: "priority",
      header: t("priority"),
      cell: (row) => <InternalPriorityBadge priority={row.priority} />,
    },
    {
      key: "created",
      header: t("createdAt"),
      cell: (row) => formatDate(row.createdAt, locale) || tCommon("emDash"),
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
      {error ? (
        <ErrorState message={error} onRetry={reload} />
      ) : truncated ? (
        <Alert
          tone="warning"
          title={
            summary
              ? t("reportsPartialTableWarning", { loaded: rows.length, total })
              : t("partialDataWarning", { loaded: rows.length, total })
          }
        />
      ) : null}

      {!loading && rows.length === 0 ? (
        <Empty title={t("listEmpty")} description={t("listEmptyDescription")} />
      ) : (
        <>
          <FilterBar
            aria-label={t("filtersAriaLabel")}
            searchPlacement="bottom"
            search={
              <Input
                label={t("search")}
                value={draft.q}
                onChange={(e) => setDraft((d) => ({ ...d, q: e.target.value }))}
                placeholder={t("searchPlaceholder")}
              />
            }
            filters={
              <>
                <Select
                  label={t("status")}
                  options={statusOptions}
                  value={draft.status}
                  onChange={(e) =>
                    setDraft((d) => ({ ...d, status: e.target.value }))
                  }
                />
                <Select
                  label={t("category")}
                  options={categoryOptions}
                  value={draft.category}
                  onChange={(e) =>
                    setDraft((d) => ({ ...d, category: e.target.value }))
                  }
                />
                <Select
                  label={t("priority")}
                  options={priorityOptions}
                  value={draft.priority}
                  onChange={(e) =>
                    setDraft((d) => ({ ...d, priority: e.target.value }))
                  }
                />
                <DatePicker
                  label={t("filterPeriodFrom")}
                  value={draft.dateFrom}
                  max={draft.dateTo || undefined}
                  onChange={(value) =>
                    setDraft((d) => ({ ...d, dateFrom: value }))
                  }
                />
                <DatePicker
                  label={t("filterPeriodTo")}
                  value={draft.dateTo}
                  min={draft.dateFrom || undefined}
                  onChange={(value) => setDraft((d) => ({ ...d, dateTo: value }))}
                />
              </>
            }
            actions={
              <Button type="submit" form="internal-report-filters">
                {tCommon("apply")}
              </Button>
            }
            reset={
              <Button type="button" variant="ghost" onClick={onResetFilters}>
                {tCommon("reset")}
              </Button>
            }
            exportSlot={
              <Button
                type="button"
                variant="outline"
                onClick={() => void onExportPdf()}
                disabled={loading || exporting || filtered.length === 0}
                title={t("reportsExportHint")}
              >
                {exporting ? t("reportsExporting") : t("reportsExportPdf")}
              </Button>
            }
          />
          <form
            id="internal-report-filters"
            onSubmit={onSubmitFilters}
            className="hidden"
          />
          {exportError ? <Alert tone="danger" title={exportError} /> : null}
          {summaryError ? (
            <Alert tone="warning" title={t("reportsSummaryFallback")} />
          ) : null}

          <section className="space-y-[var(--ecmp-panel-gap)]">
            <SectionHeader
              title={t("reportsBreakdownTitle")}
              description={t("reportsBreakdownDescription", {
                total: breakdownTotal,
              })}
            />
            {summaryLoading && !summary ? (
              <Skeleton rows={3} />
            ) : (
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
            )}
          </section>

          <Card>
            <CardBody className="space-y-4">
              <WorkspaceToolbar
                summary={
                  hasActiveInternalFilters(filters)
                    ? t("filteredCount", { count: filtered.length })
                    : t("totalCount", { count: filtered.length })
                }
              />
              {loading ? (
                <Skeleton rows={6} />
              ) : filtered.length === 0 ? (
                <Empty
                  title={t("listEmptyTitle")}
                  description={t("listEmptyFiltered")}
                />
              ) : (
                <>
                  <Table
                    columns={columns}
                    rows={pageRows}
                    getRowKey={(row) => row.id}
                  />
                  <Pagination
                    summary={tCommon("pageOf", {
                      page: currentPage,
                      totalPages,
                    })}
                    previousLabel={tCommon("previous")}
                    nextLabel={tCommon("next")}
                    onPrevious={() => setPage((p) => Math.max(1, p - 1))}
                    onNext={() => setPage((p) => Math.min(totalPages, p + 1))}
                    previousDisabled={currentPage <= 1}
                    nextDisabled={currentPage >= totalPages}
                  />
                </>
              )}
            </CardBody>
          </Card>
        </>
      )}
    </PageContainer>
  );
}
