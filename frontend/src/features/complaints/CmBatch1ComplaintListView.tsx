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
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  fetchCmBatch1Complaints,
  type CmBatch1ComplaintResponse,
} from "@/lib/api";
import {
  Badge,
  Button,
  Card,
  CardBody,
  Empty,
  ErrorState,
  FilterBar,
  Input,
  PageContainer,
  PageHeader,
  Select,
  Skeleton,
  Table,
  WorkspaceToolbar,
  type TableColumn,
} from "@/shared/ui";
import {
  cmBatch1FiltersFromSearchParams,
  cmBatch1FiltersToSearchParams,
  defaultCmBatch1ListFilters,
  type CmBatch1ListFilters,
} from "./cmBatch1ListFilters";

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

function customerCellLabel(
  row: CmBatch1ComplaintResponse,
  emDash: string,
): { name: string; id: string | null } {
  const displayName = row.customerDisplayName?.trim() || "";
  const businessId = row.customerNumber?.trim() || "";
  // Never show internal UUID as the primary customer label.
  if (displayName) {
    return {
      name: displayName,
      id: businessId && businessId !== displayName ? businessId : null,
    };
  }
  if (businessId) {
    return { name: businessId, id: null };
  }
  return { name: emDash, id: null };
}

/**
 * DEC-020 coexistence — Aggregate complaint list (API-514) at `/complaints`.
 * Filters: keyword + status (server-side).
 */
export function CmBatch1ComplaintListView() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const t = useTranslations("complaints");
  const tCases = useTranslations("cases");
  const tCommon = useTranslations("common");
  const tTable = useTranslations("table");
  const tPriority = useTranslations("priority");
  const { hasPermission } = useAuth();
  const canRead = hasPermission("complaints:read");
  const canCreate = hasPermission("complaints:create");

  const filters = useMemo(
    () => cmBatch1FiltersFromSearchParams(searchParams),
    [searchParams],
  );
  const [draft, setDraft] = useState<CmBatch1ListFilters>(filters);

  useEffect(() => {
    setDraft(filters);
  }, [filters]);

  const [rows, setRows] = useState<CmBatch1ComplaintResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!canRead) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetchCmBatch1Complaints({
        page: filters.page,
        pageSize: filters.pageSize,
        keyword: filters.keyword,
        status: filters.status,
        intakeDisposition: filters.intakeDisposition,
        createdBy: filters.createdBy,
        decidedBy: filters.decidedBy,
      });
      setRows(res.data ?? []);
      setTotal(res.meta?.totalItems ?? res.data?.length ?? 0);
    } catch (err) {
      setRows([]);
      setTotal(0);
      setError(
        err instanceof ApiError
          ? err.message
          : t("unableToLoadAggregateList"),
      );
    } finally {
      setLoading(false);
    }
  }, [canRead, filters, t]);

  useEffect(() => {
    void load();
  }, [load]);

  function applyFilters(next: CmBatch1ListFilters): void {
    const params = cmBatch1FiltersToSearchParams(next);
    const query = params.toString();
    router.replace(query ? `${pathname}?${query}` : pathname);
  }

  function onSubmitFilters(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    applyFilters({ ...draft, page: 1 });
  }

  function onResetFilters(): void {
    const next = defaultCmBatch1ListFilters();
    setDraft(next);
    applyFilters(next);
  }

  const statusFilterOptions = useMemo(
    () => [
      { value: "", label: t("statusFilterAll") },
      { value: "REGISTERED", label: t("statusOpen") },
      { value: "CLOSED", label: t("statusClosed") },
    ],
    [t],
  );

  const intakeDispositionFilterOptions = useMemo(
    () => [
      { value: "", label: t("intakeDispositionFilterAll") },
      { value: "ESCALATE_PENDING_APPROVAL", label: t("awaitingApproval") },
      { value: "ESCALATE_APPROVED", label: t("escalationApproved") },
      { value: "ESCALATE_REJECTED", label: t("escalationRejected") },
      { value: "ESCALATE_CANCELLED", label: t("escalationCancelled") },
      { value: "RETURNED_TO_BRANCH", label: t("returnedToBranch") },
      { value: "HQ_SCHEDULED", label: t("hqScheduled") },
    ],
    [t],
  );

  if (!canRead) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <PageHeader
          title={t("aggregateListTitle")}
          breadcrumbs={[
            { label: tCommon("home"), href: "/dashboard" },
            { label: t("title") },
          ]}
        />
        <Empty
          title={tCommon("accessRestricted")}
          description={t("aggregateListAccessDescription")}
          primaryAction={{
            label: tCommon("goHome"),
            onClick: () => router.push("/dashboard"),
          }}
        />
      </PageContainer>
    );
  }

  const columns: TableColumn<CmBatch1ComplaintResponse>[] = [
    {
      key: "complaintNumber",
      header: t("complaintNumber"),
      cell: (row) => (
        <div className="min-w-0">
          <Link
            href={`/complaints/cm/${encodeURIComponent(row.complaintId)}`}
            className="font-medium text-ecmp-primary underline-offset-2 hover:underline"
          >
            {row.complaintNumber}
          </Link>
          <div className="truncate text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
            {row.createdByName?.trim() || tCommon("emDash")}
          </div>
        </div>
      ),
    },
    {
      key: "subject",
      header: t("subject"),
      cell: (row) => row.subject?.trim() || "—",
    },
    {
      key: "status",
      header: t("status"),
      cell: (row) => (
        <div className="flex flex-col items-start gap-1">
          <Badge tone={row.status === "CLOSED" ? "success" : "info"}>
            {row.status === "CLOSED"
              ? t("statusClosed")
              : t("statusOpen")}
          </Badge>
          {row.status !== "CLOSED" &&
          row.intakeDisposition === "ESCALATE_PENDING_APPROVAL" ? (
            <Badge tone="warning">{t("awaitingApproval")}</Badge>
          ) : null}
          {row.status !== "CLOSED" &&
          row.intakeDisposition === "ESCALATE_APPROVED" ? (
            <Badge tone="info">{t("escalationApproved")}</Badge>
          ) : null}
          {row.status !== "CLOSED" &&
          row.intakeDisposition === "ESCALATE_REJECTED" ? (
            <Badge tone="neutral">{t("escalationRejected")}</Badge>
          ) : null}
          {row.status !== "CLOSED" &&
          row.intakeDisposition === "ESCALATE_CANCELLED" ? (
            <Badge tone="neutral">{t("escalationCancelled")}</Badge>
          ) : null}
          {row.status !== "CLOSED" &&
          row.intakeDisposition === "RETURNED_TO_BRANCH" ? (
            <Badge tone="warning">{t("returnedToBranch")}</Badge>
          ) : null}
          {row.status !== "CLOSED" &&
          row.intakeDisposition === "HQ_SCHEDULED" ? (
            <Badge tone="warning">{t("hqScheduled")}</Badge>
          ) : null}
        </div>
      ),
    },
    {
      key: "priority",
      header: t("priority"),
      cell: (row) => {
        const p = (row.priority || "").toUpperCase();
        if (!p || row.status === "CLOSED") {
          return (
            <span className="text-ecmp-text-secondary">{tCommon("emDash")}</span>
          );
        }
        const known = ["LOW", "MEDIUM", "HIGH", "CRITICAL"] as const;
        const label = (known as readonly string[]).includes(p)
          ? tPriority(p as (typeof known)[number])
          : p;
        return (
          <Badge tone={p === "CRITICAL" || p === "HIGH" ? "danger" : "neutral"}>
            {label}
          </Badge>
        );
      },
    },
    {
      key: "customer",
      header: t("customer"),
      cell: (row) => {
        const { name, id } = customerCellLabel(row, tCommon("emDash"));
        return (
          <div className="min-w-0">
            <div className="truncate font-medium text-ecmp-text-primary">
              {name}
            </div>
            {id ? (
              <div className="truncate font-mono text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                {id}
              </div>
            ) : null}
          </div>
        );
      },
    },
    {
      key: "createdAt",
      header: t("createdAt"),
      cell: (row) => formatWhen(row.createdAt),
    },
    {
      key: "open",
      header: tCommon("actions"),
      cell: (row) => (
        <Button
          type="button"
          size="sm"
          variant="outline"
          onClick={() =>
            router.push(
              `/complaints/cm/${encodeURIComponent(row.complaintId)}`,
            )
          }
        >
          {t("openComplaint")}
        </Button>
      ),
    },
  ];

  const totalPages = Math.max(1, Math.ceil(total / filters.pageSize));
  const hasActiveFilters = Boolean(
    filters.keyword.trim() || filters.status || filters.intakeDisposition,
  );

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        overline={t("overline")}
        title={t("aggregateListTitle")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title") },
        ]}
        description={t("aggregateListDescription")}
        actions={
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push("/complaints/cm/cases")}
            >
              {tCases("inboxTitle")}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push("/complaints/cm/supervisor")}
            >
              {t("supervisorQueue")}
            </Button>
            {canCreate ? (
              <Button
                type="button"
                onClick={() => router.push("/complaints/new")}
              >
                {t("create")}
              </Button>
            ) : null}
          </div>
        }
      />

      <form onSubmit={onSubmitFilters} aria-label={t("filtersAriaLabel")}>
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
                label={t("status")}
                options={statusFilterOptions}
                value={draft.status}
                onChange={(e) =>
                  setDraft((prev) => ({ ...prev, status: e.target.value }))
                }
              />
              <Select
                name="intakeDisposition"
                label={t("intakeDispositionFilter")}
                options={intakeDispositionFilterOptions}
                value={draft.intakeDisposition}
                onChange={(e) =>
                  setDraft((prev) => ({
                    ...prev,
                    intakeDisposition: e.target.value,
                  }))
                }
              />
            </>
          }
          actions={<Button type="submit">{t("applyFilters")}</Button>}
        />
      </form>

      {filters.createdBy || filters.decidedBy ? (
        <div className="flex flex-wrap items-center justify-between gap-2 rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface-sunken px-4 py-2 text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
          <span>
            {filters.decidedBy
              ? t("workStatsFilterActiveDecided")
              : t("workStatsFilterActiveCreated")}
          </span>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() =>
              applyFilters({
                ...filters,
                createdBy: "",
                decidedBy: "",
                page: 1,
              })
            }
          >
            {tCommon("clear")}
          </Button>
        </div>
      ) : null}

      {error ? (
        <ErrorState
          title={t("unableToLoadAggregateList")}
          message={error}
          onRetry={() => void load()}
        />
      ) : null}

      <Card padding={false} className="overflow-hidden">
        <CardBody className="space-y-[var(--ecmp-panel-gap)] p-4 md:p-6">
          {loading && rows.length === 0 ? (
            <Skeleton rows={6} />
          ) : !error && rows.length === 0 ? (
            <Empty
              title={t("aggregateListEmpty")}
              description={
                hasActiveFilters
                  ? t("aggregateListEmptyFiltered")
                  : t("aggregateListEmptyDescription")
              }
              primaryAction={
                hasActiveFilters
                  ? {
                      label: t("clearFilters"),
                      onClick: onResetFilters,
                    }
                  : canCreate
                    ? {
                        label: t("create"),
                        onClick: () => router.push("/complaints/new"),
                      }
                    : {
                        label: tCommon("refresh"),
                        onClick: () => void load(),
                      }
              }
              secondaryAction={
                hasActiveFilters && canCreate
                  ? {
                      label: t("create"),
                      onClick: () => router.push("/complaints/new"),
                    }
                  : undefined
              }
            />
          ) : (
            <>
              <WorkspaceToolbar
                summary={tTable("itemsInView", { count: rows.length })}
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
                columns={columns}
                rows={rows}
                getRowKey={(row) => row.complaintId}
                stickyHeader
              />
              {totalPages > 1 ? (
                <div className="flex items-center justify-between gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    disabled={filters.page <= 1 || loading}
                    onClick={() =>
                      applyFilters({
                        ...filters,
                        page: Math.max(1, filters.page - 1),
                      })
                    }
                  >
                    {tCommon("previous")}
                  </Button>
                  <span className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                    {tCommon("pageOf", { page: filters.page, totalPages })}
                  </span>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    disabled={filters.page >= totalPages || loading}
                    onClick={() =>
                      applyFilters({
                        ...filters,
                        page: Math.min(totalPages, filters.page + 1),
                      })
                    }
                  >
                    {tCommon("next")}
                  </Button>
                </div>
              ) : null}
            </>
          )}
        </CardBody>
      </Card>
    </PageContainer>
  );
}
