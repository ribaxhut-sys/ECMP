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
  fetchBranches,
  searchComplaints,
  type Branch,
} from "@/lib/api";
import type { Complaint, ComplaintStatus, Priority } from "@/lib/api/types";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
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
  defaultListFilters,
  filtersFromSearchParams,
  filtersToSearchParams,
  toSearchApiParams,
  type ComplaintListFilters,
} from "./complaintListFilters";

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

export function ComplaintListView() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const locale = useLocale();
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  const tTable = useTranslations("table");
  const tStatus = useTranslations("status");
  const tPriority = useTranslations("priority");
  const tErrors = useTranslations("errors");
  const { hasPermission } = useAuth();
  const canRead = hasPermission("complaints:read");
  const canCreate = hasPermission("complaints:create");
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

  const load = useCallback(
    async (next: ComplaintListFilters) => {
      if (!canRead) {
        setLoading(false);
        setError(t("noPermissionToView"));
        setErrorCode("FORBIDDEN");
        setRows([]);
        return;
      }

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
          setError(resolveApiErrorMessage(err, tErrors, tCommon, "unexpectedError"));
          setErrorCode(err.code);
        } else {
          setError(resolveApiErrorMessage(err, tErrors, tCommon, "unexpectedError"));
        }
      } finally {
        setLoading(false);
      }
    },
    [canRead, t, tCommon, tErrors],
  );

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

  const statusFilterOptions = useMemo(
    () => [
      { value: "", label: tTable("allStatuses") },
      { value: "NEW", label: tStatus("NEW") },
      { value: "ASSIGNED", label: tStatus("ASSIGNED") },
      { value: "IN_PROGRESS", label: tStatus("IN_PROGRESS") },
      { value: "PENDING", label: tStatus("PENDING") },
      { value: "ESCALATED", label: tStatus("ESCALATED") },
      { value: "RESOLVED", label: tStatus("RESOLVED") },
      { value: "CLOSED", label: tStatus("CLOSED") },
    ],
    [tStatus, tTable],
  );

  const priorityFilterOptions = useMemo(
    () => [
      { value: "", label: tTable("allPriorities") },
      { value: "LOW", label: tPriority("LOW") },
      { value: "MEDIUM", label: tPriority("MEDIUM") },
      { value: "HIGH", label: tPriority("HIGH") },
      { value: "CRITICAL", label: tPriority("CRITICAL") },
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
        header: t("status"),
        cell: (row) => (
          <Badge tone={statusTone(row.status)}>
            {tStatus(row.status)}
          </Badge>
        ),
      },
      {
        key: "priority",
        header: t("priority"),
        cell: (row) => (
          <Badge tone={priorityTone(row.priority)}>
            {tPriority(row.priority)}
          </Badge>
        ),
      },
      {
        key: "category",
        header: t("category"),
        cell: (row) => row.category?.trim() || tCommon("emDash"),
      },
      {
        key: "createdAt",
        header: t("createdAt"),
        cell: (row) => formatWhen(row.createdAt, locale),
      },
      {
        key: "actions",
        header: tCommon("actions"),
        hideOnMobile: false,
        cell: (row) => (
          <div className="flex flex-wrap gap-2">
            {canRead ? (
              <Button
                type="button"
                size="sm"
                variant="outline"
                onClick={() => router.push(`/complaints/${row.id}`)}
              >
                {tCommon("view")}
              </Button>
            ) : null}
            {canUpdate ? (
              <Button
                type="button"
                size="sm"
                variant="ghost"
                onClick={() => router.push(`/complaints/${row.id}/edit`)}
              >
                {tCommon("edit")}
              </Button>
            ) : null}
          </div>
        ),
      },
    ],
    [
      canRead,
      canUpdate,
      locale,
      router,
      t,
      tCommon,
      tPriority,
      tStatus,
    ],
  );

  const rangeLabel =
    totalItems === 0
      ? t("zeroResults")
      : tCommon("showingItems", {
          from: (filters.page - 1) * filters.pageSize + 1,
          to: Math.min(filters.page * filters.pageSize, totalItems),
          total: totalItems,
        });

  return (
    <PageContainer className="space-y-6">
      <PageHeader
        title={t("title")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title") },
        ]}
        description={t("listDescription")}
        actions={
          canCreate || canRead ? (
            <div className="flex flex-wrap gap-2">
              {canRead ? (
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.push("/complaints/cm/supervisor")}
                >
                  {t("supervisorQueue")}
                </Button>
              ) : null}
              {canCreate ? (
                <Button
                  type="button"
                  onClick={() => router.push("/complaints/new")}
                >
                  {t("create")}
                </Button>
              ) : null}
            </div>
          ) : undefined
        }
      />

      <Card>
        <CardBody>
          <form
            onSubmit={onSubmitFilters}
            className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4"
            aria-label={t("filtersAriaLabel")}
          >
            <div className="md:col-span-2 xl:col-span-2">
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
            </div>
            <Select
              name="status"
              label={t("status")}
              options={statusFilterOptions}
              value={draft.status}
              onChange={(e) =>
                setDraft((prev) => ({ ...prev, status: e.target.value }))
              }
            />
            <Select
              name="priority"
              label={t("priority")}
              options={priorityFilterOptions}
              value={draft.priority}
              onChange={(e) =>
                setDraft((prev) => ({ ...prev, priority: e.target.value }))
              }
            />
            <Input
              name="category"
              label={t("category")}
              value={draft.category}
              onChange={(e) =>
                setDraft((prev) => ({ ...prev, category: e.target.value }))
              }
              maxLength={64}
            />
            <Select
              name="branchId"
              label={t("branch")}
              options={branchOptions}
              value={draft.branchId}
              onChange={(e) =>
                setDraft((prev) => ({ ...prev, branchId: e.target.value }))
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
                  sort: e.target.value as ComplaintListFilters["sort"],
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
                  order: e.target.value as ComplaintListFilters["order"],
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
            <div className="flex flex-col-reverse gap-2 sm:flex-row sm:items-end md:col-span-2 xl:col-span-4">
              <Button type="submit">{t("applyFilters")}</Button>
              <Button type="button" variant="outline" onClick={onResetFilters}>
                {tCommon("reset")}
              </Button>
            </div>
          </form>
        </CardBody>
      </Card>

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
          title={t("noResults")}
          description={
            canCreate ? t("noResultsDescription") : t("noResultsTryFilters")
          }
          action={
            canCreate ? (
              <Button
                type="button"
                variant="outline"
                onClick={() => router.push("/complaints/new")}
              >
                {t("create")}
              </Button>
            ) : undefined
          }
        />
      ) : null}

      {!loading && !error && rows.length > 0 ? (
        <Card>
          <CardBody className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-2 text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
              <span>{rangeLabel}</span>
              <span>
                {totalPages > 0
                  ? tCommon("pageOf", {
                      page: filters.page,
                      totalPages,
                    })
                  : t("pageOnly", { page: filters.page })}
              </span>
            </div>
            <Table
              columns={columns}
              rows={rows}
              getRowKey={(row) => row.id}
              caption={t("listCaption")}
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
                {tCommon("previous")}
              </Button>
              <Button
                type="button"
                variant="outline"
                disabled={!hasNext}
                onClick={() =>
                  applyFilters({ ...filters, page: filters.page + 1 })
                }
              >
                {tCommon("next")}
              </Button>
            </div>
          </CardBody>
        </Card>
      ) : null}
    </PageContainer>
  );
}
