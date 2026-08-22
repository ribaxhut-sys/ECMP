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
  fetchCmBatch1Complaints,
  fetchCmCases,
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
  Pagination,
  Select,
  Skeleton,
  Table,
  WorkspaceToolbar,
  type TableColumn,
} from "@/shared/ui";
import { formatDateTime24 } from "@/shared/utils/datetime";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import {
  cmBatch1FiltersFromSearchParams,
  cmBatch1FiltersToSearchParams,
  defaultCmBatch1ListFilters,
  type CmBatch1ListFilters,
} from "./cmBatch1ListFilters";
import {
  hqPathCopyKeys,
  penangananCountsFromCases,
  resolveHqPathPhase,
  resolvePenangananContextKind,
} from "./penangananGroups";

type PenangananListCounts = {
  open: number;
  pusat: number;
  done: number;
};

function customerCellLabel(
  row: CmBatch1ComplaintResponse,
  emDash: string,
): { name: string; id: string | null } {
  const displayName = row.customerDisplayName?.trim() || "";
  const businessId = row.customerNumber?.trim() || "";
  // Never show internal UUID as the primary taxpayer label.
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
 * CM Aggregate complaint list (API-514) at `/complaints` (DEC-026 Single SoT).
 * Filters: keyword + status (server-side).
 */
export function CmBatch1ComplaintListView() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const t = useTranslations("complaints");
  const tCases = useTranslations("cases");
  const tCommon = useTranslations("common");
  const tPriority = useTranslations("priority");
  const tErrors = useTranslations("errors");
  const locale = useLocale();
  const { hasPermission } = useAuth();
  const canRead = hasPermission("complaints:read");

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
  const [penangananByComplaint, setPenangananByComplaint] = useState<
    Record<string, PenangananListCounts | "loading" | "error">
  >({});

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
      setPenangananByComplaint({});
      setError(
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : t("unableToLoadAggregateList"),
      );
    } finally {
      setLoading(false);
    }
  }, [canRead, filters, t, tErrors, tCommon]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (!canRead || rows.length === 0) {
      setPenangananByComplaint({});
      return;
    }
    let cancelled = false;
    const pending: Record<string, PenangananListCounts | "loading" | "error"> =
      {};
    for (const row of rows) {
      pending[row.complaintId] = "loading";
    }
    setPenangananByComplaint(pending);

    void (async () => {
      const entries = await Promise.all(
        rows.map(async (row) => {
          try {
            const res = await fetchCmCases({
              complaintId: row.complaintId,
              page: 1,
              pageSize: 50,
            });
            const cases = res.data ?? [];
            const counts = penangananCountsFromCases(
              cases,
              row.intakeDisposition,
            );
            return [
              row.complaintId,
              {
                open: counts.open,
                pusat: counts.pusat,
                done: counts.done,
              } satisfies PenangananListCounts,
            ] as const;
          } catch {
            return [row.complaintId, "error" as const] as const;
          }
        }),
      );
      if (cancelled) return;
      const next: Record<string, PenangananListCounts | "loading" | "error"> =
        {};
      for (const [id, value] of entries) {
        next[id] = value;
      }
      setPenangananByComplaint(next);
    })();

    return () => {
      cancelled = true;
    };
  }, [canRead, rows]);

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
      { value: "IN_PROGRESS", label: t("statusInProgress") },
      { value: "CLOSED", label: t("statusClosed") },
    ],
    [t],
  );

  const intakeDispositionFilterOptions = useMemo(
    () => [
      { value: "", label: t("intakeDispositionFilterAll") },
      { value: "UNESCALATED", label: t("intakeUnescalated") },
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
      className: "whitespace-nowrap",
      headerClassName: "whitespace-nowrap",
      cell: (row) => (
        <div className="min-w-0">
          <Link
            href={`/complaints/cm/${encodeURIComponent(row.complaintId)}`}
            className="whitespace-nowrap font-medium tabular-nums text-ecmp-primary underline-offset-2 hover:underline"
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
        <Badge
          tone={
            row.status === "CLOSED"
              ? "success"
              : row.status === "IN_PROGRESS"
                ? "warning"
                : "info"
          }
        >
          {row.status === "CLOSED"
            ? t("statusClosed")
            : row.status === "IN_PROGRESS"
              ? t("statusInProgress")
              : t("statusOpen")}
        </Badge>
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
      cell: (row) => formatDateTime24(row.createdAt, locale, tCommon("emDash")),
    },
    {
      key: "penanganan",
      header: t("penangananColumn"),
      cell: (row) => {
        const summary = penangananByComplaint[row.complaintId];
        if (summary === undefined || summary === "loading") {
          return (
            <span className="text-ecmp-text-secondary">
              {tCommon("emDash")}
            </span>
          );
        }
        if (summary === "error") {
          return (
            <span className="text-ecmp-text-secondary">
              {t("penangananListUnavailable")}
            </span>
          );
        }
        const kind = resolvePenangananContextKind({
          complaintStatus: row.status,
          intakeDisposition: row.intakeDisposition,
          counts: summary,
        });
        if (kind === "closed") {
          return <Badge tone="success">{t("penangananListClosed")}</Badge>;
        }
        if (kind === "hq_waiting") {
          const phase = resolveHqPathPhase({
            intakeDisposition: row.intakeDisposition,
            hqAcceptedAt: row.hqAcceptedAt,
          });
          const copy = phase
            ? hqPathCopyKeys(phase)
            : hqPathCopyKeys("pending_approval");
          return (
            <Badge tone={phase === "scheduled" ? "info" : "warning"}>
              {t(copy.list as "penangananListHqWaiting")}
            </Badge>
          );
        }
        if (kind === "none") {
          return (
            <Badge tone="warning">{t("penangananListNone")}</Badge>
          );
        }
        return <Badge tone="info">{t("penangananInProgress")}</Badge>;
      },
    },
  ];

  const totalPages = Math.max(1, Math.ceil(total / filters.pageSize));
  const rangeFrom =
    total === 0 ? 0 : (filters.page - 1) * filters.pageSize + 1;
  const rangeTo = Math.min(filters.page * filters.pageSize, total);
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
        actions={
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push("/complaints/cm/cases")}
            >
              {tCases("inboxTitle")}
            </Button>
            {canRead ? (
              <Button
                type="button"
                variant="outline"
                onClick={() => router.push("/complaints/cm/supervisor")}
              >
                {t("supervisorQueue")}
              </Button>
            ) : null}
            <Button
              type="button"
              onClick={() => router.push("/complaints/new")}
            >
              {t("create")}
            </Button>
          </div>
        }
      />

      <form onSubmit={onSubmitFilters} aria-label={t("filtersAriaLabel")}>
        <FilterBar
          inline
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
              <div className="w-[11.5rem] shrink-0">
                <Select
                  name="status"
                  label={t("status")}
                  options={statusFilterOptions}
                  value={draft.status}
                  onChange={(e) =>
                    setDraft((prev) => ({ ...prev, status: e.target.value }))
                  }
                />
              </div>
              <div className="w-[14rem] shrink-0">
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
              </div>
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
                  : {
                      label: t("create"),
                      onClick: () => router.push("/complaints/new"),
                    }
              }
              secondaryAction={
                hasActiveFilters
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
                summary={tCommon("showingItems", {
                  from: rangeFrom,
                  to: rangeTo,
                  total,
                })}
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
                density="compact"
                stickyHeader
                className="[--ecmp-font-table-size:0.9375rem]"
              />
              <Pagination
                summary={tCommon("pageOf", {
                  page: filters.page,
                  totalPages,
                })}
                previousLabel={tCommon("previous")}
                nextLabel={tCommon("next")}
                previousDisabled={filters.page <= 1 || loading}
                nextDisabled={filters.page >= totalPages || loading}
                onPrevious={() =>
                  applyFilters({
                    ...filters,
                    page: Math.max(1, filters.page - 1),
                  })
                }
                onNext={() =>
                  applyFilters({
                    ...filters,
                    page: Math.min(totalPages, filters.page + 1),
                  })
                }
              />
            </>
          )}
        </CardBody>
      </Card>
    </PageContainer>
  );
}
