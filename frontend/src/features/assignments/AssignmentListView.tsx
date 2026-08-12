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
  fetchAssignmentHistory,
  fetchAssignmentsList,
  fetchBranches,
  fetchUsers,
  type Branch,
  type UserRef,
} from "@/lib/api";
import type { Assignment, Complaint, Priority } from "@/lib/api/types";
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
  Input,
  PageContainer,
  PageHeader,
  Pagination,
  QuickFilters,
  Select,
  Skeleton,
  Table,
  WorkspaceToolbar,
  type BadgeTone,
  type TableColumn,
  type TableDensity,
} from "@/shared/ui";
import { AssignmentRowActions } from "./AssignmentRowActions";
import {
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

type QuickFilterId = "all" | "new" | "assigned" | "critical" | "inProgress";

function activeQuickFilter(filters: AssignmentListFilters): QuickFilterId {
  if (filters.priority === "CRITICAL" && !filters.status) return "critical";
  if (filters.status === "NEW" && !filters.priority) return "new";
  if (filters.status === "ASSIGNED" && !filters.priority) return "assigned";
  if (filters.status === "IN_PROGRESS" && !filters.priority) return "inProgress";
  if (!filters.status && !filters.priority) return "all";
  return "all";
}

function formatWhen(value: string | null | undefined, locale: string): string {
  if (!value) return "—";
  try {
    return new Intl.DateTimeFormat(locale, {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
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
  const locale = useLocale();
  const t = useTranslations("assignments");
  const tCommon = useTranslations("common");
  const tTable = useTranslations("table");
  const tStatus = useTranslations("status");
  const tPriority = useTranslations("priority");
  const tComplaints = useTranslations("complaints");
  const tErrors = useTranslations("errors");
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
  const [density, setDensity] = useState<TableDensity>("comfortable");
  const [selectedId, setSelectedId] = useState<string | null>(null);

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
        setError(t("noPermission"));
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
          setError(resolveApiErrorMessage(err, tErrors, tCommon));
          setErrorCode(err.code);
        } else {
          setError(resolveApiErrorMessage(err, tErrors, tCommon));
        }
      } finally {
        setLoading(false);
      }
    },
    [canRead, enrichRows, t, tCommon, tErrors],
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

  function applyQuickFilter(id: string): void {
    const base = defaultAssignmentFilters();
    const next: AssignmentListFilters = {
      ...base,
      keyword: filters.keyword,
      branchId: filters.branchId,
      assignedTo: filters.assignedTo,
      sort: filters.sort,
      order: filters.order,
      pageSize: filters.pageSize,
    };
    switch (id as QuickFilterId) {
      case "new":
        next.status = "NEW";
        break;
      case "assigned":
        next.status = "ASSIGNED";
        break;
      case "inProgress":
        next.status = "IN_PROGRESS";
        break;
      case "critical":
        next.priority = "CRITICAL";
        break;
      default:
        break;
    }
    setDraft(next);
    applyFilters(next);
  }

  const currentQuick = activeQuickFilter(filters);

  const refresh = useCallback(() => {
    void load(filters);
  }, [filters, load]);

  const branchNameById = useMemo(() => {
    const map = new Map<string, string>();
    for (const b of branches) map.set(b.id, b.name);
    return map;
  }, [branches]);

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

  const branchOptions = useMemo(
    () => [
      { value: "", label: t("allBranches") },
      ...branches.map((b) => ({ value: b.id, label: b.name })),
    ],
    [branches, t],
  );

  const assigneeOptions = useMemo(
    () => [
      { value: "", label: t("allAssignees") },
      ...users.map((u) => ({ value: u.id, label: u.fullName })),
    ],
    [t, users],
  );

  const columns = useMemo<TableColumn<Complaint>[]>(
    () => [
      {
        key: "complaint",
        header: t("complaintColumn"),
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
        header: t("currentAssigneeColumn"),
        cell: (row) =>
          enrichment[row.id]?.current?.assigneeName?.trim() || tCommon("emDash"),
      },
      {
        key: "previousAssignee",
        header: t("previousAssigneeColumn"),
        cell: (row) =>
          enrichment[row.id]?.previous?.assigneeName?.trim() || tCommon("emDash"),
      },
      {
        key: "assignmentStatus",
        header: t("assignmentColumn"),
        cell: (row) => {
          const active = Boolean(enrichment[row.id]?.current);
          return (
            <Badge tone={assignmentStatusTone(active)}>
              {active ? t("activeLabel") : t("unassignedLabel")}
            </Badge>
          );
        },
      },
      {
        key: "assignedAt",
        header: t("assignedAtColumn"),
        cell: (row) =>
          formatWhen(enrichment[row.id]?.current?.assignedAt, locale),
      },
      {
        key: "branch",
        header: t("branchColumn"),
        cell: (row) =>
          (row.branchId && branchNameById.get(row.branchId)) || tCommon("emDash"),
      },
      {
        key: "priority",
        header: tComplaints("priority"),
        cell: (row) => (
          <Badge tone={priorityTone(row.priority)}>{tPriority(row.priority)}</Badge>
        ),
      },
      {
        key: "actions",
        header: tCommon("actions"),
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
                {t("openRow")}
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
    [branchNameById, enrichment, locale, refresh, router, t, tCommon, tComplaints, tPriority],
  );

  const rangeLabel =
    totalItems === 0
      ? t("zeroResults")
      : tCommon("showingItems", {
          from: (filters.page - 1) * filters.pageSize + 1,
          to: Math.min(filters.page * filters.pageSize, totalItems),
          total: totalItems,
        });

  const pageSummary =
    totalPages > 0
      ? tCommon("pageOf", { page: filters.page, totalPages })
      : t("pageLabel", { page: filters.page });

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        overline={tComplaints("overline")}
        title={t("title")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title") },
        ]}
        description={t("listDescription")}
        actions={
          <Button type="button" variant="outline" onClick={refresh}>
            {tCommon("refresh")}
          </Button>
        }
      />

      <QuickFilters
        label={tComplaints("quickFiltersLabel")}
        onSelect={applyQuickFilter}
        options={[
          { id: "all", label: tComplaints("qfAll"), active: currentQuick === "all" },
          { id: "new", label: tComplaints("qfNew"), active: currentQuick === "new" },
          {
            id: "assigned",
            label: tStatus("ASSIGNED"),
            active: currentQuick === "assigned",
          },
          {
            id: "inProgress",
            label: tComplaints("qfOpen"),
            active: currentQuick === "inProgress",
          },
          {
            id: "critical",
            label: tComplaints("qfCritical"),
            active: currentQuick === "critical",
            tone: "critical",
          },
        ]}
      />

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
                label={t("complaintStatusLabel")}
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
                name="branchId"
                label={t("branchColumn")}
                options={branchOptions}
                value={draft.branchId}
                onChange={(e) =>
                  setDraft((prev) => ({ ...prev, branchId: e.target.value }))
                }
              />
              <Select
                name="assignedTo"
                label={t("assigneeLabel")}
                options={assigneeOptions}
                value={draft.assignedTo}
                onChange={(e) =>
                  setDraft((prev) => ({ ...prev, assignedTo: e.target.value }))
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
                    sort: e.target.value as AssignmentListFilters["sort"],
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
                    order: e.target.value as AssignmentListFilters["order"],
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
          primaryAction={{
            label: t("refreshAssignments"),
            onClick: () => void load(filters),
          }}
          secondaryAction={{
            label: t("clearFilters"),
            onClick: onResetFilters,
          }}
        />
      ) : null}

      {!loading && !error && rows.length > 0 ? (
        <Card padding={false} className="overflow-hidden">
          <CardBody className="space-y-[var(--ecmp-panel-gap)] p-4 md:p-6">
            <WorkspaceToolbar
              summary={tTable("itemsInView", { count: totalItems })}
              density={<DensityToggle value={density} onChange={setDensity} />}
              actions={
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  onClick={refresh}
                >
                  {tCommon("refresh")}
                </Button>
              }
            />
            <Table
              columns={columns}
              rows={rows}
              getRowKey={(row) => row.id}
              caption={t("caption")}
              density={density}
              stickyHeader
              selectedKeys={selectedId ? new Set([selectedId]) : undefined}
              onRowClick={(row) => setSelectedId(row.id)}
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
