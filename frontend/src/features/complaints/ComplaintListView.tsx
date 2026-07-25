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
  searchComplaints,
  type Branch,
} from "@/lib/api";
import type { Complaint, ComplaintStatus, Priority } from "@/lib/api/types";
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
import {
  PAGE_SIZE_OPTIONS,
  PRIORITY_FILTER_OPTIONS,
  SORT_FIELD_OPTIONS,
  SORT_ORDER_OPTIONS,
  STATUS_FILTER_OPTIONS,
  defaultListFilters,
  filtersFromSearchParams,
  filtersToSearchParams,
  toSearchApiParams,
  type ComplaintListFilters,
} from "./complaintListFilters";

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

export function ComplaintListView() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { hasPermission } = useAuth();
  const canUpdate = hasPermission("complaints:update");

  const filters = useMemo(
    () => filtersFromSearchParams(new URLSearchParams(searchParams.toString())),
    [searchParams],
  );

  const [draft, setDraft] = useState<ComplaintListFilters>(filters);
  const [rows, setRows] = useState<Complaint[]>([]);
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrevious, setHasPrevious] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [errorCode, setErrorCode] = useState<string | undefined>();
  const [branches, setBranches] = useState<Branch[]>([]);

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

  const load = useCallback(async (next: ComplaintListFilters) => {
    setLoading(true);
    setError(null);
    setErrorCode(undefined);
    try {
      const res = await searchComplaints(toSearchApiParams(next));
      setRows(res.items);
      setTotalItems(res.pagination.totalItems);
      setTotalPages(res.pagination.totalPages);
      setHasNext(res.pagination.hasNext);
      setHasPrevious(res.pagination.hasPrevious);
    } catch (err) {
      setRows([]);
      setTotalItems(0);
      setTotalPages(0);
      setHasNext(false);
      setHasPrevious(false);
      if (err instanceof ApiError) {
        setError(err.message);
        setErrorCode(err.code);
      } else {
        setError(
          err instanceof Error ? err.message : "Unable to load complaints.",
        );
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load(filters);
  }, [filters, load]);

  function applyFilters(next: ComplaintListFilters): void {
    const params = filtersToSearchParams(next);
    const query = params.toString();
    router.replace(query ? `${pathname}?${query}` : pathname);
  }

  function onSubmitFilters(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    applyFilters({ ...draft, page: 1 });
  }

  function onResetFilters(): void {
    const next = defaultListFilters();
    setDraft(next);
    applyFilters(next);
  }

  const branchOptions = [
    { value: "", label: "All branches" },
    ...branches.map((b) => ({ value: b.id, label: b.name })),
  ];

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
        key: "priority",
        header: "Priority",
        cell: (row) => (
          <Badge tone={priorityTone(row.priority)}>{row.priority}</Badge>
        ),
      },
      {
        key: "category",
        header: "Category",
        cell: (row) => row.category?.trim() || "—",
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
              View
            </Button>
            {canUpdate ? (
              <Button
                type="button"
                size="sm"
                variant="ghost"
                onClick={() => router.push(`/complaints/${row.id}/edit`)}
              >
                Edit
              </Button>
            ) : null}
          </div>
        ),
      },
    ],
    [canUpdate, router],
  );

  const rangeLabel =
    totalItems === 0
      ? "0 results"
      : `Showing ${(filters.page - 1) * filters.pageSize + 1}–${Math.min(filters.page * filters.pageSize, totalItems)} of ${totalItems}`;

  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title="Complaints"
        breadcrumbs={[
          { label: "Home", href: "/dashboard" },
          { label: "Complaints" },
        ]}
        description="Search, filter, and open customer complaints."
        actions={
          <Button type="button" onClick={() => router.push("/complaints/new")}>
            Create Complaint
          </Button>
        }
      />

      <Card>
        <CardBody>
          <form
            onSubmit={onSubmitFilters}
            className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4"
            aria-label="Complaint search filters"
          >
            <div className="md:col-span-2 xl:col-span-2">
              <Input
                name="keyword"
                label="Search"
                placeholder="Number, subject, description, reporter…"
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
            <Input
              name="category"
              label="Category"
              value={draft.category}
              onChange={(e) =>
                setDraft((prev) => ({ ...prev, category: e.target.value }))
              }
              maxLength={64}
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
              name="sort"
              label="Sort by"
              options={SORT_FIELD_OPTIONS}
              value={draft.sort}
              onChange={(e) =>
                setDraft((prev) => ({
                  ...prev,
                  sort: e.target.value as ComplaintListFilters["sort"],
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
                  order: e.target.value as ComplaintListFilters["order"],
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
          title="Unable to load complaints"
          message={error}
          code={errorCode}
          onRetry={() => void load(filters)}
        />
      ) : null}

      {!loading && !error && rows.length === 0 ? (
        <Empty
          title="No complaints found"
          description="Try adjusting filters, or create a new complaint."
          action={
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push("/complaints/new")}
            >
              Create Complaint
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
              caption="Complaint list"
            />
            <div className="flex flex-col-reverse gap-2 border-t border-ecmp-border pt-4 sm:flex-row sm:justify-end">
              <Button
                type="button"
                variant="outline"
                disabled={!hasPrevious}
                onClick={() =>
                  applyFilters({ ...filters, page: Math.max(1, filters.page - 1) })
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
