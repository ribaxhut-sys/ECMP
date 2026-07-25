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
  fetchBranches,
  fetchFinalResolutionDetail,
  fetchResolution,
  fetchResolutionAssignee,
  fetchResolutionEscalations,
  fetchResolutionsList,
  type Branch,
} from "@/lib/api";
import type {
  Complaint,
  ComplaintStatus,
  Escalation,
  FinalResolutionDetail,
  Priority,
  Resolution,
} from "@/lib/api/types";
import {
  Badge,
  Button,
  Card,
  CardBody,
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
import { ResolutionRowActions } from "./ResolutionRowActions";
import {
  ESCALATED_FILTER_OPTIONS,
  PAGE_SIZE_OPTIONS,
  PRIORITY_FILTER_OPTIONS,
  SORT_FIELD_OPTIONS,
  SORT_ORDER_OPTIONS,
  STATUS_FILTER_OPTIONS,
  defaultResolutionFilters,
  filtersFromSearchParams,
  filtersToSearchParams,
  toSearchApiParams,
  type ResolutionListFilters,
} from "./resolutionListFilters";

type RowEnrichment = {
  assigneeName: string | null;
  resolution: Resolution | null;
  finalResolution: FinalResolutionDetail | null;
  escalation: Escalation | null;
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

function pickEscalation(rows: Escalation[]): Escalation | null {
  if (rows.length === 0) return null;
  return (
    rows.find((row) => row.status.toUpperCase() === "REQUESTED") ??
    rows.find((row) => row.status.toUpperCase() === "APPROVED") ??
    rows.find((row) => row.status.toUpperCase() === "CLOSED") ??
    rows[0] ??
    null
  );
}

export function ResolutionListView() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { hasPermission } = useAuth();
  const canRead = hasPermission("complaints:read");

  const filters = useMemo(
    () => filtersFromSearchParams(new URLSearchParams(searchParams.toString())),
    [searchParams],
  );

  const [draft, setDraft] = useState<ResolutionListFilters>(filters);
  const [rows, setRows] = useState<Complaint[]>([]);
  const [enrichment, setEnrichment] = useState<Record<string, RowEnrichment>>(
    {},
  );
  const [branches, setBranches] = useState<Branch[]>([]);
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

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetchBranches(100);
        if (!cancelled) setBranches(res.data);
      } catch {
        if (!cancelled) setBranches([]);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const enrichRows = useCallback(async (items: Complaint[]) => {
    if (items.length === 0) {
      setEnrichment({});
      return;
    }

    const results = await Promise.all(
      items.map(async (item) => {
        const [assignRes, resolutionRes, finalRes, escalationRes] =
          await Promise.allSettled([
            fetchResolutionAssignee(item.id),
            fetchResolution(item.id),
            fetchFinalResolutionDetail(item.id),
            fetchResolutionEscalations(item.id),
          ]);

        let assigneeName: string | null = null;
        if (assignRes.status === "fulfilled") {
          const current =
            assignRes.value.data.find((row) => row.isCurrent) ?? null;
          assigneeName = current?.assigneeName?.trim() || null;
        }

        let resolution: Resolution | null = null;
        if (resolutionRes.status === "fulfilled") {
          resolution = resolutionRes.value.data;
        } else if (
          resolutionRes.status === "rejected" &&
          !(
            resolutionRes.reason instanceof ApiError &&
            resolutionRes.reason.status === 404
          )
        ) {
          resolution = null;
        }

        let finalResolution: FinalResolutionDetail | null = null;
        if (finalRes.status === "fulfilled") {
          finalResolution = finalRes.value.data;
        }

        let escalation: Escalation | null = null;
        if (escalationRes.status === "fulfilled") {
          escalation = pickEscalation(escalationRes.value.data);
        }

        return [
          item.id,
          { assigneeName, resolution, finalResolution, escalation },
        ] as const;
      }),
    );

    setEnrichment(Object.fromEntries(results));
  }, []);

  const load = useCallback(
    async (next: ResolutionListFilters) => {
      if (!canRead) {
        setLoading(false);
        setError("You do not have permission to view resolutions.");
        setErrorCode("FORBIDDEN");
        setRows([]);
        return;
      }

      setLoading(true);
      setError(null);
      setErrorCode(undefined);
      try {
        const res = await fetchResolutionsList(toSearchApiParams(next));
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
            err instanceof Error
              ? err.message
              : "Unable to load resolutions.",
          );
        }
      } finally {
        setLoading(false);
      }
    },
    [canRead, enrichRows],
  );

  useEffect(() => {
    void load(filters);
  }, [filters, load]);

  function applyFilters(next: ResolutionListFilters): void {
    const params = filtersToSearchParams(next);
    const query = params.toString();
    router.replace(query ? `${pathname}?${query}` : pathname);
  }

  function onSubmitFilters(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    applyFilters({ ...draft, page: 1 });
  }

  function onResetFilters(): void {
    const next = defaultResolutionFilters();
    setDraft(next);
    applyFilters(next);
  }

  const refresh = useCallback(() => {
    void load(filters);
  }, [filters, load]);

  const branchNameById = useMemo(() => {
    const map = new Map<string, string>();
    for (const b of branches) map.set(b.id, b.name);
    return map;
  }, [branches]);

  const branchOptions = [
    { value: "", label: "All branches" },
    ...branches.map((b) => ({ value: b.id, label: b.name })),
  ];

  const columns = useMemo<TableColumn<Complaint>[]>(
    () => [
      {
        key: "complaint",
        header: "Complaint",
        cell: (row) => (
          <div className="min-w-0 space-y-1">
            <Link
              href={`/complaints/${row.id}`}
              className="font-medium text-ecmp-primary hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-focus"
            >
              {row.complaintNumber}
            </Link>
            <p className="line-clamp-2 max-w-xs text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
              {row.subject}
            </p>
          </div>
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
        key: "resolutionStatus",
        header: "Resolution",
        cell: (row) => {
          const has = Boolean(enrichment[row.id]?.resolution);
          return (
            <Badge tone={has ? "success" : "neutral"}>
              {has ? "Submitted" : "None"}
            </Badge>
          );
        },
      },
      {
        key: "resolvedAt",
        header: "Resolved at",
        cell: (row) =>
          formatWhen(enrichment[row.id]?.resolution?.resolvedAt),
      },
      {
        key: "finalResolution",
        header: "Final resolution",
        cell: (row) => {
          const final = enrichment[row.id]?.finalResolution;
          if (!final) return "—";
          return (
            <Badge tone="success">
              {final.status.replaceAll("_", " ")}
            </Badge>
          );
        },
      },
      {
        key: "escalation",
        header: "Escalation",
        cell: (row) => {
          const esc = enrichment[row.id]?.escalation;
          if (!esc) return "—";
          return (
            <Badge
              tone={
                esc.status.toUpperCase() === "CLOSED"
                  ? "neutral"
                  : esc.status.toUpperCase() === "APPROVED"
                    ? "success"
                    : "warning"
              }
            >
              {esc.status.replaceAll("_", " ")}
            </Badge>
          );
        },
      },
      {
        key: "branch",
        header: "Branch",
        cell: (row) =>
          (row.branchId && branchNameById.get(row.branchId)) || "—",
      },
      {
        key: "priority",
        header: "Priority",
        cell: (row) => (
          <Badge tone={priorityTone(row.priority)}>{row.priority}</Badge>
        ),
      },
      {
        key: "actions",
        header: "Actions",
        hideOnMobile: false,
        cell: (row) => {
          const meta = enrichment[row.id];
          return (
            <div className="flex flex-wrap gap-2">
              <Button
                type="button"
                size="sm"
                variant="outline"
                onClick={() => router.push(`/complaints/${row.id}`)}
              >
                Open
              </Button>
              <ResolutionRowActions
                row={{
                  id: row.id,
                  complaintNumber: row.complaintNumber,
                  subject: row.subject,
                  status: row.status,
                  closedAt: row.closedAt,
                  resolution: meta?.resolution ?? null,
                  finalResolution: meta?.finalResolution ?? null,
                  escalation: meta?.escalation ?? null,
                }}
                onChanged={refresh}
              />
            </div>
          );
        },
      },
    ],
    [branchNameById, enrichment, refresh, router],
  );

  const rangeLabel =
    totalItems === 0
      ? "0 results"
      : `Showing ${(filters.page - 1) * filters.pageSize + 1}–${Math.min(filters.page * filters.pageSize, totalItems)} of ${totalItems}`;

  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title="Resolutions"
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Resolutions" },
        ]}
        description="Submit resolutions, final resolutions, escalations, and closures. Open a row for complaint detail."
        actions={
          <Button type="button" variant="outline" onClick={refresh}>
            Refresh
          </Button>
        }
      />

      <Card>
        <CardBody>
          <form
            onSubmit={onSubmitFilters}
            className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4"
            aria-label="Resolution search filters"
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
              name="branchId"
              label="Branch"
              options={branchOptions}
              value={draft.branchId}
              onChange={(e) =>
                setDraft((prev) => ({ ...prev, branchId: e.target.value }))
              }
            />
            <Select
              name="escalated"
              label="Escalation"
              options={[...ESCALATED_FILTER_OPTIONS]}
              value={draft.escalated}
              onChange={(e) =>
                setDraft((prev) => ({ ...prev, escalated: e.target.value }))
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
                  sort: e.target.value as ResolutionListFilters["sort"],
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
                  order: e.target.value as ResolutionListFilters["order"],
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
          title="Unable to load resolutions"
          message={error}
          code={errorCode}
          onRetry={() => void load(filters)}
        />
      ) : null}

      {!loading && !error && rows.length === 0 ? (
        <Empty
          title="No resolutions found"
          description="Try adjusting filters, or open the complaint queue."
          action={
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push("/queue")}
            >
              Open queue
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
              caption="Resolution list"
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
