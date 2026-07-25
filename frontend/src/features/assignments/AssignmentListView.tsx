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
  fetchAssignmentHistory,
  fetchAssignmentsList,
  fetchBranches,
  fetchUsers,
  type Branch,
  type UserRef,
} from "@/lib/api";
import type { Assignment, Complaint, Priority } from "@/lib/api/types";
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
import { AssignmentRowActions } from "./AssignmentRowActions";
import {
  PAGE_SIZE_OPTIONS,
  PRIORITY_FILTER_OPTIONS,
  SORT_FIELD_OPTIONS,
  SORT_ORDER_OPTIONS,
  STATUS_FILTER_OPTIONS,
  defaultAssignmentFilters,
  filtersFromSearchParams,
  filtersToSearchParams,
  toSearchApiParams,
  type AssignmentListFilters,
} from "./assignmentListFilters";

type RowEnrichment = {
  current: Assignment | null;
  previous: Assignment | null;
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

function assignmentStatusTone(active: boolean): BadgeTone {
  return active ? "primary" : "neutral";
}

export function AssignmentListView() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { hasPermission } = useAuth();
  const canRead = hasPermission("complaints:read");

  const filters = useMemo(
    () => filtersFromSearchParams(new URLSearchParams(searchParams.toString())),
    [searchParams],
  );

  const [draft, setDraft] = useState<AssignmentListFilters>(filters);
  const [rows, setRows] = useState<Complaint[]>([]);
  const [enrichment, setEnrichment] = useState<Record<string, RowEnrichment>>(
    {},
  );
  const [branches, setBranches] = useState<Branch[]>([]);
  const [users, setUsers] = useState<UserRef[]>([]);
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
        const [branchRes, userRes] = await Promise.all([
          fetchBranches(100),
          fetchUsers({ pageSize: 100, isActive: true }).catch(() => null),
        ]);
        if (cancelled) return;
        setBranches(branchRes.data);
        setUsers((userRes?.data ?? []).filter((u) => u.isActive));
      } catch {
        if (!cancelled) {
          setBranches([]);
          setUsers([]);
        }
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
        try {
          const res = await fetchAssignmentHistory(item.id);
          const history = res.data;
          const current = history.find((row) => row.isCurrent) ?? null;
          const previous =
            history.find((row) => !row.isCurrent) ??
            (history.length > 1 && current
              ? history.find((row) => row.id !== current.id) ?? null
              : null);
          return [item.id, { current, previous }] as const;
        } catch {
          return [item.id, { current: null, previous: null }] as const;
        }
      }),
    );

    setEnrichment(Object.fromEntries(results));
  }, []);

  const load = useCallback(
    async (next: AssignmentListFilters) => {
      if (!canRead) {
        setLoading(false);
        setError("You do not have permission to view assignments.");
        setErrorCode("FORBIDDEN");
        setRows([]);
        return;
      }

      setLoading(true);
      setError(null);
      setErrorCode(undefined);
      try {
        const res = await fetchAssignmentsList(toSearchApiParams(next));
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
              : "Unable to load assignments.",
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

  function applyFilters(next: AssignmentListFilters): void {
    const params = filtersToSearchParams(next);
    const query = params.toString();
    router.replace(query ? `${pathname}?${query}` : pathname);
  }

  function onSubmitFilters(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    applyFilters({ ...draft, page: 1 });
  }

  function onResetFilters(): void {
    const next = defaultAssignmentFilters();
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

  const assigneeOptions = [
    { value: "", label: "All assignees" },
    ...users.map((u) => ({ value: u.id, label: u.fullName })),
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
        key: "currentAssignee",
        header: "Current assignee",
        cell: (row) =>
          enrichment[row.id]?.current?.assigneeName?.trim() || "—",
      },
      {
        key: "previousAssignee",
        header: "Previous assignee",
        cell: (row) =>
          enrichment[row.id]?.previous?.assigneeName?.trim() || "—",
      },
      {
        key: "assignmentStatus",
        header: "Assignment",
        cell: (row) => {
          const active = Boolean(enrichment[row.id]?.current);
          return (
            <Badge tone={assignmentStatusTone(active)}>
              {active ? "Active" : "Unassigned"}
            </Badge>
          );
        },
      },
      {
        key: "assignedAt",
        header: "Assigned at",
        cell: (row) =>
          formatWhen(enrichment[row.id]?.current?.assignedAt),
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
              <AssignmentRowActions
                row={{
                  id: row.id,
                  complaintNumber: row.complaintNumber,
                  subject: row.subject,
                  status: row.status,
                  currentAssigneeId: meta?.current?.assigneeId ?? null,
                  currentAssigneeName: meta?.current?.assigneeName ?? null,
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
        title="Assignments"
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Assignments" },
        ]}
        description="Assign, reassign, or cancel complaint handlers. Open a row for complaint detail."
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
            aria-label="Assignment search filters"
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
              label="Complaint status"
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
              name="assignedTo"
              label="Assignee"
              options={assigneeOptions}
              value={draft.assignedTo}
              onChange={(e) =>
                setDraft((prev) => ({ ...prev, assignedTo: e.target.value }))
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
                  sort: e.target.value as AssignmentListFilters["sort"],
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
                  order: e.target.value as AssignmentListFilters["order"],
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
          title="Unable to load assignments"
          message={error}
          code={errorCode}
          onRetry={() => void load(filters)}
        />
      ) : null}

      {!loading && !error && rows.length === 0 ? (
        <Empty
          title="No assignments found"
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
              caption="Assignment list"
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
