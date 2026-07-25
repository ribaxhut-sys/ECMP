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
import {
  Badge,
  Button,
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  Empty,
  ErrorState,
  Input,
  PageContainer,
  PageHeader,
  Select,
  Skeleton,
  Table,
  type BadgeTone,
  type TableColumn,
} from "@/shared/ui";
import { QueueRowActions } from "./QueueRowActions";
import {
  PAGE_SIZE_OPTIONS,
  PRIORITY_FILTER_OPTIONS,
  SLA_STATUS_FILTER_OPTIONS,
  SORT_FIELD_OPTIONS,
  SORT_ORDER_OPTIONS,
  STATUS_FILTER_OPTIONS,
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
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Unable to load queue summary.",
      );
    }
  }, [canReadDashboard]);

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
        setError("You do not have permission to view the queue.");
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
          setError(err.message);
          setErrorCode(err.code);
        } else {
          setError(
            err instanceof Error ? err.message : "Unable to load queue.",
          );
        }
      } finally {
        setLoading(false);
      }
    },
    [canRead, enrichRows, userId],
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

  const columns = useMemo<TableColumn<Complaint>[]>(
    () => [
      {
        key: "complaintNumber",
        header: "Number",
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
        header: "Subject",
        cell: (row) => (
          <span className="line-clamp-2 max-w-xs">{row.subject}</span>
        ),
      },
      {
        key: "status",
        header: "Status",
        cell: (row) => (
          <Badge tone={statusTone(row.status)}>
            {row.status.replaceAll("_", " ")}
          </Badge>
        ),
      },
      {
        key: "assignee",
        header: "Assignee",
        cell: (row) => enrichment[row.id]?.assigneeName?.trim() || "—",
      },
      {
        key: "priority",
        header: "Priority",
        cell: (row) => (
          <Badge tone={priorityTone(row.priority)}>{row.priority}</Badge>
        ),
      },
      {
        key: "sla",
        header: "SLA",
        cell: (row) => {
          const sla = enrichment[row.id]?.slaStatus ?? null;
          if (!sla) return "—";
          return (
            <Badge tone={slaTone(sla)}>{sla.replaceAll("_", " ")}</Badge>
          );
        },
      },
      {
        key: "createdAt",
        header: "Created",
        cell: (row) => formatWhen(row.createdAt),
      },
      {
        key: "actions",
        header: "Actions",
        hideOnMobile: false,
        cell: (row) => (
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              size="sm"
              variant="outline"
              onClick={() => router.push(`/complaints/${row.id}`)}
            >
              Open
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
    [enrichment, refreshAll, router],
  );

  const rangeLabel =
    totalItems === 0
      ? "0 results"
      : `Showing ${(filters.page - 1) * filters.pageSize + 1}–${Math.min(filters.page * filters.pageSize, totalItems)} of ${totalItems}`;

  const summaryCards = summary
    ? [
        { label: "Open", value: summary.openComplaints },
        { label: "Pending", value: summary.pendingComplaints },
        { label: "Overdue", value: summary.overdueComplaints },
        { label: "Escalated", value: summary.escalatedComplaints },
        { label: "Today", value: summary.todayComplaints },
        { label: "Total", value: summary.totalComplaints },
      ]
    : [];

  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title="Queue"
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Queue" },
        ]}
        description="Work queue of complaints — filter, take, release, or open detail."
        actions={
          <Button type="button" variant="outline" onClick={refreshAll}>
            Refresh
          </Button>
        }
      />

      {canReadDashboard ? (
        <Card>
          <CardHeader>
            <CardTitle>Queue summary</CardTitle>
          </CardHeader>
          <CardBody>
            {summaryError ? (
              <AlertBlock
                message={summaryError}
                onRetry={() => void loadSummary()}
              />
            ) : !summary ? (
              <Skeleton rows={2} />
            ) : (
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-6">
                {summaryCards.map((card) => (
                  <div
                    key={card.label}
                    className="rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-background px-4 py-4"
                  >
                    <p className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary">
                      {card.label}
                    </p>
                    <p className="mt-2 text-[length:var(--ecmp-font-heading-size)] font-semibold tabular-nums text-ecmp-text-primary">
                      {card.value}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </CardBody>
        </Card>
      ) : null}

      <Card>
        <CardBody>
          <form
            onSubmit={onSubmitFilters}
            className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4"
            aria-label="Queue search filters"
          >
            <div className="md:col-span-2 xl:col-span-2">
              <Input
                name="keyword"
                label="Search"
                placeholder="Number, subject, description…"
                value={draft.keyword}
                onChange={(e) =>
                  setDraft((prev) => ({ ...prev, keyword: e.target.value }))
                }
                maxLength={200}
              />
            </div>
            <Select
              name="status"
              label="Status"
              options={[...STATUS_FILTER_OPTIONS]}
              value={draft.status}
              onChange={(e) =>
                setDraft((prev) => ({ ...prev, status: e.target.value }))
              }
            />
            <Select
              name="priority"
              label="Priority"
              options={[...PRIORITY_FILTER_OPTIONS]}
              value={draft.priority}
              onChange={(e) =>
                setDraft((prev) => ({ ...prev, priority: e.target.value }))
              }
            />
            <Select
              name="slaStatus"
              label="SLA status"
              options={[...SLA_STATUS_FILTER_OPTIONS]}
              value={draft.slaStatus}
              onChange={(e) =>
                setDraft((prev) => ({ ...prev, slaStatus: e.target.value }))
              }
            />
            <Select
              name="sort"
              label="Sort by"
              options={SORT_FIELD_OPTIONS}
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
              label="Order"
              options={SORT_ORDER_OPTIONS}
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
              label="Page size"
              options={[...PAGE_SIZE_OPTIONS]}
              value={String(draft.pageSize)}
              onChange={(e) =>
                setDraft((prev) => ({
                  ...prev,
                  pageSize: Number(e.target.value) || 20,
                }))
              }
            />
            <label className="flex items-end gap-2 pb-2 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
              <input
                type="checkbox"
                className="size-4 rounded border-ecmp-border"
                checked={draft.mineOnly}
                onChange={(e) =>
                  setDraft((prev) => ({
                    ...prev,
                    mineOnly: e.target.checked,
                    assignedTo: e.target.checked ? "" : prev.assignedTo,
                  }))
                }
              />
              My queue only
            </label>
            <div className="flex flex-col-reverse gap-2 sm:flex-row sm:items-end md:col-span-2 xl:col-span-4">
              <Button type="submit">Apply filters</Button>
              <Button type="button" variant="outline" onClick={onResetFilters}>
                Reset
              </Button>
            </div>
          </form>
        </CardBody>
      </Card>

      {loading ? <Skeleton rows={6} /> : null}

      {!loading && error ? (
        <ErrorState
          title="Unable to load queue"
          message={error}
          code={errorCode}
          onRetry={() => void load(filters)}
        />
      ) : null}

      {!loading && !error && rows.length === 0 ? (
        <Empty
          title="No queue items found"
          description="Try adjusting filters, or refresh the queue."
          action={
            <Button type="button" variant="outline" onClick={refreshAll}>
              Refresh
            </Button>
          }
        />
      ) : null}

      {!loading && !error && rows.length > 0 ? (
        <Card>
          <CardBody className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-2 text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
              <span>{rangeLabel}</span>
              <span>
                Page {filters.page}
                {totalPages > 0 ? ` of ${totalPages}` : ""}
              </span>
            </div>
            <Table
              columns={columns}
              rows={rows}
              getRowKey={(row) => row.id}
              caption="Queue list"
            />
            <div className="flex flex-col-reverse gap-2 border-t border-ecmp-border pt-4 sm:flex-row sm:justify-end">
              <Button
                type="button"
                variant="outline"
                disabled={!hasPrevious}
                onClick={() =>
                  applyFilters({
                    ...filters,
                    page: Math.max(1, filters.page - 1),
                  })
                }
              >
                Previous
              </Button>
              <Button
                type="button"
                variant="outline"
                disabled={!hasNext}
                onClick={() =>
                  applyFilters({ ...filters, page: filters.page + 1 })
                }
              >
                Next
              </Button>
            </div>
          </CardBody>
        </Card>
      ) : null}
    </PageContainer>
  );
}

function AlertBlock({
  message,
  onRetry,
}: {
  message: string;
  onRetry: () => void;
}) {
  return (
    <div className="space-y-3">
      <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-danger">
        {message}
      </p>
      <Button type="button" size="sm" variant="outline" onClick={onRetry}>
        Retry summary
      </Button>
    </div>
  );
}
