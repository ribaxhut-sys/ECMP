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
import { useOrgUnitCode } from "@/features/announcements/useOrgUnitCode";
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
  Pagination,
  Select,
  Skeleton,
  Table,
  WorkspaceToolbar,
  type TableColumn,
} from "@/shared/ui";
import { formatDateTime24 } from "@/shared/utils/datetime";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { prefersComplaintNumberIdentity } from "./cmBatch1ComplaintListIdentity";
import {
  cmBatch1FiltersFromSearchParams,
  cmBatch1FiltersToSearchParams,
  defaultCmBatch1ListFilters,
  type CmBatch1ListFilters,
} from "./cmBatch1ListFilters";
import { ComplaintSlaBadge } from "./ComplaintSlaBadge";
import {
  expandComplaintsToCaseRows,
  type CmBatch1ComplaintListCases,
  type CmBatch1ComplaintListRow,
} from "./cmBatch1ComplaintListRows";
import {
  hqPathCopyKeys,
  penangananCountsFromCases,
  resolveHqPathPhase,
  resolvePenangananContextKind,
} from "./penangananGroups";

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
 * CM Aggregate list API (API-514 / DEC-026) at `/complaints`.
 * Pusat: Case number primary, complaint secondary.
 * Cabang (unit-scoped): complaint number primary, Case secondary.
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
  const orgUnitCode = useOrgUnitCode();
  const complaintNumberFirst = prefersComplaintNumberIdentity(orgUnitCode);

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
        needsPusatHandling: filters.needsPusatHandling || undefined,
      });
      setRows(res.data ?? []);
      setTotal(res.meta?.totalItems ?? res.data?.length ?? 0);
    } catch (err) {
      setRows([]);
      setTotal(0);
      setError(
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : t("unableToLoadAggregateList"),
      );
    } finally {
      setLoading(false);
    }
    // i18n helpers are stable enough for error copy; omit from deps so this
    // callback does not churn every render.
    // eslint-disable-next-line react-hooks/exhaustive-deps -- t/tErrors/tCommon
  }, [canRead, filters]);

  useEffect(() => {
    void load();
  }, [load]);

  // Case column uses parent-scoped `cases` embedded in API-514 list response
  // (no N+1 /api/v1/cm/cases). Avoids false "Belum ada case" from race/visibility.
  const casesByComplaint = useMemo(() => {
    const next: Record<string, CmBatch1ComplaintListCases> = {};
    for (const row of rows) {
      next[row.complaintId] = Array.isArray(row.cases) ? row.cases : [];
    }
    return next;
  }, [rows]);

  const listRows = useMemo(
    () => expandComplaintsToCaseRows(rows, casesByComplaint),
    [rows, casesByComplaint],
  );

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

  const columns: TableColumn<CmBatch1ComplaintListRow>[] = [
    {
      key: "caseNumber",
      header: complaintNumberFirst
        ? t("listComplaintNumberColumn")
        : t("listCaseColumn"),
      className: "whitespace-nowrap",
      headerClassName: "whitespace-nowrap",
      cell: (row) => {
        const caseItem = row.caseItem;
        const complaintHref = `/complaints/cm/${encodeURIComponent(row.complaint.complaintId)}`;
        const caseHref = caseItem
          ? `/complaints/cm/cases/${encodeURIComponent(caseItem.caseId)}`
          : complaintHref;
        const caseLabel =
          row.casesState === "loading"
            ? tCommon("emDash")
            : row.casesState === "error"
              ? t("penangananListUnavailable")
              : caseItem?.caseNumber
                ? caseItem.caseNumber
                : row.complaint.caseCreated
                  ? // Cases exist but none are in this viewer's scope (e.g. Pusat
                    // after filtering branch-closed siblings) — not "no Case yet".
                    tCommon("emDash")
                  : t("noCaseYet");
        const complaintLabel = row.complaint.complaintNumber;
        if (complaintNumberFirst) {
          return (
            <div className="min-w-0">
              <Link
                href={complaintHref}
                className={
                  row.complaint.needsPusatHandling
                    ? "whitespace-nowrap font-semibold tabular-nums text-ecmp-primary underline-offset-2 hover:underline"
                    : "whitespace-nowrap font-medium tabular-nums text-ecmp-primary underline-offset-2 hover:underline"
                }
              >
                {complaintLabel}
              </Link>
              <Link
                href={caseHref}
                className="mt-0.5 block truncate font-mono text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary underline-offset-2 hover:underline hover:text-ecmp-primary"
              >
                {caseLabel}
              </Link>
            </div>
          );
        }
        return (
          <div className="min-w-0">
            <Link
              href={caseHref}
              className={
                row.complaint.needsPusatHandling
                  ? "whitespace-nowrap font-semibold tabular-nums text-ecmp-primary underline-offset-2 hover:underline"
                  : "whitespace-nowrap font-medium tabular-nums text-ecmp-primary underline-offset-2 hover:underline"
              }
            >
              {caseLabel}
            </Link>
            <Link
              href={complaintHref}
              className="mt-0.5 block truncate font-mono text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary underline-offset-2 hover:underline hover:text-ecmp-primary"
            >
              {complaintLabel}
            </Link>
          </div>
        );
      },
    },
    {
      key: "subject",
      header: t("subject"),
      cell: (row) =>
        row.caseItem?.subject?.trim() ||
        row.complaint.subject?.trim() ||
        "—",
    },
    {
      key: "status",
      header: t("status"),
      cell: (row) => (
        <Badge
          tone={
            row.complaint.status === "CLOSED"
              ? "success"
              : row.complaint.status === "IN_PROGRESS"
                ? "warning"
                : "info"
          }
        >
          {row.complaint.status === "CLOSED"
            ? t("statusClosed")
            : row.complaint.status === "IN_PROGRESS"
              ? t("statusInProgress")
              : t("statusOpen")}
        </Badge>
      ),
    },
    {
      // DEC-031 — 30 calendar-day resolution target. Server-computed; the
      // column is blank for complaints the server did not measure.
      key: "sla",
      header: t("slaColumn"),
      cell: (row) => (
        <ComplaintSlaBadge sla={row.complaint.sla} />
      ),
    },
    {
      key: "priority",
      header: t("priority"),
      cell: (row) => {
        const p = (row.caseItem?.priority || row.complaint.priority || "").toUpperCase();
        if (!p || row.complaint.status === "CLOSED") {
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
        const { name, id } = customerCellLabel(
          row.complaint,
          tCommon("emDash"),
        );
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
      cell: (row) =>
        formatDateTime24(row.complaint.createdAt, locale, tCommon("emDash")),
    },
    {
      key: "penanganan",
      header: t("penangananColumn"),
      cell: (row) => {
        const entry = casesByComplaint[row.complaint.complaintId];
        if (entry === undefined || entry === "loading") {
          return (
            <span className="text-ecmp-text-secondary">
              {tCommon("emDash")}
            </span>
          );
        }
        if (entry === "error") {
          return (
            <span className="text-ecmp-text-secondary">
              {t("penangananListUnavailable")}
            </span>
          );
        }
        if (row.caseItem?.escalatedToPusat) {
          return (
            <Badge tone="warning">{t("penangananListHqWaiting")}</Badge>
          );
        }
        const counts = penangananCountsFromCases(
          entry,
          row.complaint.intakeDisposition,
        );
        const kind = resolvePenangananContextKind({
          complaintStatus: row.complaint.status,
          intakeDisposition: row.complaint.intakeDisposition,
          counts,
        });
        if (kind === "closed") {
          return <Badge tone="success">{t("penangananListClosed")}</Badge>;
        }
        if (kind === "hq_waiting") {
          const phase = resolveHqPathPhase({
            intakeDisposition: row.complaint.intakeDisposition,
            hqAcceptedAt: row.complaint.hqAcceptedAt,
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
            {complaintNumberFirst ? (
              <Button
                type="button"
                variant="outline"
                onClick={() => router.push("/complaints/cm/cases")}
              >
                {tCases("inboxTitle")}
              </Button>
            ) : null}
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
              placeholder={t("aggregateSearchPlaceholder")}
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
                rows={listRows}
                getRowKey={(row) => row.key}
                density="compact"
                stickyHeader
                className="[--ecmp-font-table-size:0.9375rem]"
                getRowClassName={(row) =>
                  row.complaint.needsPusatHandling ? "font-semibold" : undefined
                }
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
