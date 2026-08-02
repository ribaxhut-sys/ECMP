"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type FormEvent,
} from "react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  fetchQueueAssignments,
  fetchQueueList,
  fetchQueueSla,
  fetchQueueSummary,
} from "@/lib/api";
import type {
  Complaint,
  ComplaintStatus,
  DashboardComplaintSummary,
  Priority,
  SlaStatus,
} from "@/lib/api/types";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import {
  Alert,
  Badge,
  Button,
  Card,
  CardBody,
  Checkbox,
  Empty,
  ErrorState,
  FilterBar,
  Input,
  PageContainer,
  PageHeader,
  Pagination,
  SectionHeader,
  Select,
  Skeleton,
  StatCard,
  Table,
  type BadgeTone,
  type TableColumn,
} from "@/shared/ui";
import { QueueRowActions } from "./QueueRowActions";
import {
  defaultQueueFilters,
  filtersFromSearchParams,
  filtersToSearchParams,
  toSearchApiParams,
  type QueueListFilters,
} from "./queueListFilters";

type RowEnrichment = {
  assigneeId: string | null;
  assigneeName: string | null;
  slaStatus: SlaStatus | null;
};

function formatWhen(value: string | null | undefined, locale: string): string {
  if (!value) return "—";
  try {
    return new Intl.DateTimeFormat(locale, {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

function statusTone(status: ComplaintStatus): BadgeTone {
  switch (status) {
    case "RESOLVED":
      return "success";
    case "CLOSED":
      return "neutral";
    case "ESCALATED":
      return "danger";
    case "PENDING":
    case "IN_PROGRESS":
      return "warning";
    case "ASSIGNED":
      return "primary";
    default:
      return "info";
  }
}

function priorityTone(priority: Priority): BadgeTone {
  switch (priority) {
    case "CRITICAL":
      return "danger";
    case "HIGH":
      return "warning";
    case "MEDIUM":
      return "info";
    default:
      return "neutral";
  }
}

function slaTone(status: SlaStatus | null): BadgeTone {
  switch (status) {
    case "BREACHED":
      return "danger";
    case "ON_TIME":
      return "success";
    case "COMPLETED":
      return "neutral";
    case "PENDING":
      return "warning";
    default:
      return "neutral";
  }
}

export function QueueDashboardView() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const locale = useLocale();
  const t = useTranslations("queue");
  const tCommon = useTranslations("common");
  const tTable = useTranslations("table");
  const tStatus = useTranslations("status");
  const tPriority = useTranslations("priority");
  const tComplaints = useTranslations("complaints");
  const tErrors = useTranslations("errors");
  const { hasPermission, userId } = useAuth();
  const canRead = hasPermission("complaints:read");
  const canReadDashboard = hasPermission("dashboard:read");

  const filters = useMemo(
    () => filtersFromSearchParams(new URLSearchParams(searchParams.toString())),
    [searchParams],
  );

  const [draft, setDraft] = useState<QueueListFilters>(filters);
  const [rows, setRows] = useState<Complaint[]>([]);
  const [enrichment, setEnrichment] = useState<Record<string, RowEnrichment>>(
    {},
  );
  const [summary, setSummary] = useState<DashboardComplaintSummary | null>(
    null,
  );
  const [summaryError, setSummaryError] = useState<string | null>(null);
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrevious, setHasPrevious] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [errorCode, setErrorCode] = useState<string | undefined>();

  useEffect(() => {
    setDraft(filters);
  }, [filters]);

  const loadSummary = useCallback(async () => {
    if (!canReadDashboard) {
      setSummary(null);
      setSummaryError(null);
      return;
    }
    try {
      const res = await fetchQueueSummary();
      setSummary(res.data);
      setSummaryError(null);
    } catch (err) {
      setSummary(null);
      setSummaryError(
        resolveApiErrorMessage(err, tErrors, tCommon),
      );
    }
  }, [canReadDashboard, tCommon, tErrors]);

  const enrichRows = useCallback(async (items: Complaint[]) => {
    if (items.length === 0) {
      setEnrichment({});
      return;
    }

    const results = await Promise.all(
      items.map(async (item) => {
        const [assignRes, slaRes] = await Promise.allSettled([
          fetchQueueAssignments(item.id),
          fetchQueueSla(item.id),
        ]);

        let assigneeId: string | null = null;
        let assigneeName: string | null = null;
        if (assignRes.status === "fulfilled") {
          const current =
            assignRes.value.data.find((row) => row.isCurrent) ?? null;
          assigneeId = current?.assigneeId ?? null;
          assigneeName = current?.assigneeName?.trim() || null;
        }

        let slaStatus: SlaStatus | null = null;
        if (slaRes.status === "fulfilled") {
          slaStatus = slaRes.value.data.overallStatus;
        }

        return [
          item.id,
          { assigneeId, assigneeName, slaStatus },
        ] as const;
      }),
    );

    setEnrichment(Object.fromEntries(results));
  }, []);

  const load = useCallback(
    async (next: QueueListFilters) => {
      if (!canRead) {
        setLoading(false);
        setError(t("noPermission"));
        setErrorCode("FORBIDDEN");
        setRows([]);
        return;
      }

      setLoading(true);
      setError(null);
      setErrorCode(undefined);
      try {
        const res = await fetchQueueList(toSearchApiParams(next, userId));
        setRows(res.items);
        setTotalItems(res.pagination.totalItems);
        setTotalPages(res.pagination.totalPages);
        setHasNext(res.pagination.hasNext);
        setHasPrevious(res.pagination.hasPrevious);
        void enrichRows(res.items);
      } catch (err) {
        setRows([]);
        setEnrichment({});
        setTotalItems(0);
        setTotalPages(0);
        setHasNext(false);
        setHasPrevious(false);
        if (err instanceof ApiError) {
          setError(resolveApiErrorMessage(err, tErrors, tCommon));
          setErrorCode(err.code);
        } else {
          setError(resolveApiErrorMessage(err, tErrors, tCommon));
        }
      } finally {
        setLoading(false);
      }
    },
    [canRead, enrichRows, t, tCommon, tErrors, userId],
  );

  const refreshAll = useCallback(() => {
    void loadSummary();
    void load(filters);
  }, [filters, load, loadSummary]);

  useEffect(() => {
    void loadSummary();
  }, [loadSummary]);

  useEffect(() => {
    void load(filters);
  }, [filters, load]);

  function applyFilters(next: QueueListFilters): void {
    const params = filtersToSearchParams(next);
    const query = params.toString();
    router.replace(query ? `${pathname}?${query}` : pathname);
  }

  function onSubmitFilters(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    applyFilters({ ...draft, page: 1 });
  }

  function onResetFilters(): void {
    const next = defaultQueueFilters();
    setDraft(next);
    applyFilters(next);
  }

  const statusFilterOptions = useMemo(
    () => [
      { value: "", label: tTable("allStatuses") },
      ...(["NEW", "ASSIGNED", "IN_PROGRESS", "PENDING", "ESCALATED", "RESOLVED", "CLOSED"] as const).map(
        (value) => ({ value, label: tStatus(value) }),
      ),
    ],
    [tStatus, tTable],
  );

  const priorityFilterOptions = useMemo(
    () => [
      { value: "", label: tTable("allPriorities") },
      ...(["LOW", "MEDIUM", "HIGH", "CRITICAL"] as const).map((value) => ({
        value,
        label: tPriority(value),
      })),
    ],
    [tPriority, tTable],
  );

  const slaStatusFilterOptions = useMemo(
    () => [
      { value: "", label: tTable("allSla") },
      ...(["PENDING", "ON_TIME", "BREACHED", "COMPLETED"] as const).map(
        (value) => ({ value, label: tStatus(value) }),
      ),
    ],
    [tStatus, tTable],
  );

  const sortFieldOptions = useMemo(
    () => [
      { value: "createdAt", label: tTable("sortCreatedAt") },
      { value: "updatedAt", label: tTable("sortUpdatedAt") },
      { value: "priority", label: tTable("sortPriority") },
      { value: "status", label: tTable("sortStatus") },
      { value: "slaDueDate", label: tTable("sortSlaDueDate") },
    ],
    [tTable],
  );

  const sortOrderOptions = useMemo(
    () => [
      { value: "desc", label: tTable("sortOrderDesc") },
      { value: "asc", label: tTable("sortOrderAsc") },
    ],
    [tTable],
  );

  const pageSizeOptions = useMemo(
    () =>
      [10, 20, 50].map((count) => ({
        value: String(count),
        label: tTable("perPage", { count }),
      })),
    [tTable],
  );

  const columns = useMemo<TableColumn<Complaint>[]>(
    () => [
      {
        key: "complaintNumber",
        header: t("number"),
        cell: (row) => (
          <Link
            href={`/complaints/${row.id}`}
            className="font-medium text-ecmp-primary hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-focus"
          >
            {row.complaintNumber}
          </Link>
        ),
      },
      {
        key: "subject",
        header: t("subject"),
        cell: (row) => (
          <span className="line-clamp-2 max-w-xs">{row.subject}</span>
        ),
      },
      {
        key: "status",
        header: tComplaints("status"),
        cell: (row) => (
          <Badge tone={statusTone(row.status)}>
            {tStatus(row.status)}
          </Badge>
        ),
      },
      {
        key: "assignee",
        header: t("assignee"),
        cell: (row) => enrichment[row.id]?.assigneeName?.trim() || tCommon("emDash"),
      },
      {
        key: "priority",
        header: tComplaints("priority"),
        cell: (row) => (
          <Badge tone={priorityTone(row.priority)}>{tPriority(row.priority)}</Badge>
        ),
      },
      {
        key: "sla",
        header: t("sla"),
        cell: (row) => {
          const sla = enrichment[row.id]?.slaStatus ?? null;
          if (!sla) return tCommon("emDash");
          return (
            <Badge tone={slaTone(sla)}>{tStatus(sla)}</Badge>
          );
        },
      },
      {
        key: "createdAt",
        header: t("created"),
        cell: (row) => formatWhen(row.createdAt, locale),
      },
      {
        key: "actions",
        header: tCommon("actions"),
        hideOnMobile: false,
        cell: (row) => (
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              size="sm"
              variant="outline"
              onClick={() => router.push(`/complaints/${row.id}`)}
            >
              {t("open")}
            </Button>
            <QueueRowActions
              row={{
                id: row.id,
                complaintNumber: row.complaintNumber,
                status: row.status,
                assigneeId: enrichment[row.id]?.assigneeId ?? null,
                assigneeName: enrichment[row.id]?.assigneeName ?? null,
              }}
              onChanged={refreshAll}
            />
          </div>
        ),
      },
    ],
    [enrichment, locale, refreshAll, router, t, tCommon, tComplaints, tPriority, tStatus],
  );

  const rangeLabel =
    totalItems === 0
      ? t("zeroResults")
      : tCommon("showingItems", {
          from: (filters.page - 1) * filters.pageSize + 1,
          to: Math.min(filters.page * filters.pageSize, totalItems),
          total: totalItems,
        });

  const summaryCards = summary
    ? [
        { label: t("openLabel"), value: summary.openComplaints },
        { label: t("pendingLabel"), value: summary.pendingComplaints },
        { label: t("overdueLabel"), value: summary.overdueComplaints },
        { label: t("escalatedLabel"), value: summary.escalatedComplaints },
        { label: t("todayLabel"), value: summary.todayComplaints },
        { label: t("totalLabel"), value: summary.totalComplaints },
      ]
    : [];

  const pageSummary =
    totalPages > 0
      ? tCommon("pageOf", { page: filters.page, totalPages })
      : t("pageLabel", { page: filters.page });

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={t("title")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title") },
        ]}
        description={t("description")}
        actions={
          <Button type="button" variant="outline" onClick={refreshAll}>
            {tCommon("refresh")}
          </Button>
        }
      />

      {canReadDashboard ? (
        <section className="space-y-[var(--ecmp-panel-gap)]" aria-label={t("summary")}>
          <SectionHeader title={t("summary")} />
          {summaryError ? (
            <Alert
              tone="danger"
              title={t("unableToLoad")}
              description={summaryError}
              actionLabel={t("retrySummary")}
              onAction={() => void loadSummary()}
            />
          ) : !summary ? (
            <Skeleton rows={2} />
          ) : (
            <div className="grid grid-cols-2 gap-[var(--ecmp-card-gap)] sm:grid-cols-3 xl:grid-cols-6">
              {summaryCards.map((card) => (
                <StatCard
                  key={card.label}
                  title={card.label}
                  value={<span className="tabular-nums">{card.value}</span>}
                />
              ))}
            </div>
          )}
        </section>
      ) : null}

      <form onSubmit={onSubmitFilters} aria-label={t("searchFiltersAriaLabel")}>
        <FilterBar
          search={
            <Input
              name="keyword"
              label={tCommon("search")}
              placeholder={t("searchPlaceholder")}
              value={draft.keyword}
              onChange={(e) =>
                setDraft((prev) => ({ ...prev, keyword: e.target.value }))
              }
              maxLength={200}
            />
          }
          filters={
            <>
              <Select
                name="status"
                label={tComplaints("status")}
                options={statusFilterOptions}
                value={draft.status}
                onChange={(e) =>
                  setDraft((prev) => ({ ...prev, status: e.target.value }))
                }
              />
              <Select
                name="priority"
                label={tComplaints("priority")}
                options={priorityFilterOptions}
                value={draft.priority}
                onChange={(e) =>
                  setDraft((prev) => ({ ...prev, priority: e.target.value }))
                }
              />
              <Select
                name="slaStatus"
                label={t("slaStatusLabel")}
                options={slaStatusFilterOptions}
                value={draft.slaStatus}
                onChange={(e) =>
                  setDraft((prev) => ({ ...prev, slaStatus: e.target.value }))
                }
              />
              <Select
                name="sort"
                label={tTable("sortBy")}
                options={sortFieldOptions}
                value={draft.sort}
                onChange={(e) =>
                  setDraft((prev) => ({
                    ...prev,
                    sort: e.target.value as QueueListFilters["sort"],
                  }))
                }
              />
              <Select
                name="order"
                label={tTable("order")}
                options={sortOrderOptions}
                value={draft.order}
                onChange={(e) =>
                  setDraft((prev) => ({
                    ...prev,
                    order: e.target.value as QueueListFilters["order"],
                  }))
                }
              />
              <Select
                name="pageSize"
                label={tTable("pageSize")}
                options={pageSizeOptions}
                value={String(draft.pageSize)}
                onChange={(e) =>
                  setDraft((prev) => ({
                    ...prev,
                    pageSize: Number(e.target.value) || 20,
                  }))
                }
              />
              <Checkbox
                name="mineOnly"
                label={t("mineOnlyLabel")}
                checked={draft.mineOnly}
                onChange={(e) =>
                  setDraft((prev) => ({
                    ...prev,
                    mineOnly: e.target.checked,
                    assignedTo: e.target.checked ? "" : prev.assignedTo,
                  }))
                }
              />
            </>
          }
          actions={<Button type="submit">{tCommon("apply")}</Button>}
          reset={
            <Button type="button" variant="outline" onClick={onResetFilters}>
              {tCommon("reset")}
            </Button>
          }
        />
      </form>

      {loading ? <Skeleton rows={6} /> : null}

      {!loading && error ? (
        <ErrorState
          title={t("unableToLoad")}
          message={error}
          code={errorCode}
          onRetry={() => void load(filters)}
        />
      ) : null}

      {!loading && !error && rows.length === 0 ? (
        <Empty
          title={t("noItems")}
          description={t("noItemsDescription")}
          action={
            <Button type="button" variant="outline" onClick={refreshAll}>
              {tCommon("refresh")}
            </Button>
          }
        />
      ) : null}

      {!loading && !error && rows.length > 0 ? (
        <Card>
          <CardBody className="space-y-[var(--ecmp-panel-gap)]">
            <Table
              columns={columns}
              rows={rows}
              getRowKey={(row) => row.id}
              caption={t("caption")}
              density="comfortable"
            />
            <Pagination
              summary={
                <span>
                  {rangeLabel}
                  <span className="mx-2 text-ecmp-border">·</span>
                  {pageSummary}
                </span>
              }
              previousLabel={tCommon("previous")}
              nextLabel={tCommon("next")}
              previousDisabled={!hasPrevious}
              nextDisabled={!hasNext}
              onPrevious={() =>
                applyFilters({
                  ...filters,
                  page: Math.max(1, filters.page - 1),
                })
              }
              onNext={() =>
                applyFilters({ ...filters, page: filters.page + 1 })
              }
            />
          </CardBody>
        </Card>
      ) : null}
    </PageContainer>
  );
}
