"use client";

import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
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
  Skeleton,
  Table,
  WorkspaceToolbar,
  type TableColumn,
} from "@/shared/ui";
import { formatDateTime24 } from "@/shared/utils/datetime";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { isPusatWorkAudience } from "./cmBatch1ComplaintListIdentity";
import { ComplaintSlaBadge } from "./ComplaintSlaBadge";
import {
  expandComplaintsToCaseRows,
  type CmBatch1ComplaintListCases,
  type CmBatch1ComplaintListRow,
} from "./cmBatch1ComplaintListRows";
import {
  closedArchiveIntakeDisposition,
  closedArchivePathLabelKey,
  keepClosedArchiveRow,
} from "./closedArchiveRows";

const NUMBER_LINK_BASE =
  "whitespace-nowrap tabular-nums text-ecmp-primary underline-offset-2 hover:underline";

function numberLinkClass(unread: boolean): string {
  return unread
    ? `${NUMBER_LINK_BASE} font-semibold`
    : `${NUMBER_LINK_BASE} font-medium`;
}

function customerCellLabel(
  row: CmBatch1ComplaintResponse,
  emDash: string,
): { name: string; id: string | null } {
  const displayName = row.customerDisplayName?.trim() || "";
  const businessId = row.customerNumber?.trim() || "";
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

function parsePositiveInt(raw: string | null, fallback: number): number {
  const value = Number(raw ?? fallback);
  return Number.isFinite(value) && value >= 1 ? Math.floor(value) : fallback;
}

/**
 * Ditutup archive at `/ditutup` — successful closes, not a work queue.
 * Cabang: BRANCH_CLOSED + HQ_CLOSED (API-514 COMPLETED). Pusat: HQ_CLOSED.
 */
export function ClosedArchiveListView() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const t = useTranslations("complaints");
  const tNav = useTranslations("nav");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const locale = useLocale();
  const { hasPermission } = useAuth();
  const canRead = hasPermission("complaints:read");
  const orgUnitCode = useOrgUnitCode();
  const pusatAudience = isPusatWorkAudience(orgUnitCode);

  const keyword = (searchParams.get("keyword") ?? "").slice(0, 200);
  const page = parsePositiveInt(searchParams.get("page"), 1);
  const pageSize = Math.min(parsePositiveInt(searchParams.get("pageSize"), 10), 100);

  const [draftKeyword, setDraftKeyword] = useState(keyword);
  useEffect(() => {
    setDraftKeyword(keyword);
  }, [keyword]);

  const [rows, setRows] = useState<CmBatch1ComplaintResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!canRead) {
      setLoading(false);
      return;
    }
    if (pusatAudience === null) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetchCmBatch1Complaints({
        page,
        pageSize,
        keyword,
        status: "CLOSED",
        intakeDisposition: closedArchiveIntakeDisposition(pusatAudience),
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
  }, [canRead, pusatAudience, page, pageSize, keyword, t, tErrors, tCommon]);

  useEffect(() => {
    void load();
  }, [load]);

  const casesByComplaint = useMemo(() => {
    const next: Record<string, CmBatch1ComplaintListCases> = {};
    for (const item of rows) {
      next[item.complaintId] = Array.isArray(item.cases) ? item.cases : [];
    }
    return next;
  }, [rows]);

  const listRows = useMemo(
    () =>
      expandComplaintsToCaseRows(rows, casesByComplaint).filter(
        keepClosedArchiveRow,
      ),
    [rows, casesByComplaint],
  );

  function applyQuery(next: {
    keyword?: string;
    page?: number;
  }): void {
    const params = new URLSearchParams();
    const nextKeyword = (next.keyword ?? keyword).trim();
    if (nextKeyword) params.set("keyword", nextKeyword);
    const nextPage = next.page ?? page;
    if (nextPage > 1) params.set("page", String(nextPage));
    if (pageSize !== 10) params.set("pageSize", String(pageSize));
    const qs = params.toString();
    router.replace(qs ? `/ditutup?${qs}` : "/ditutup");
  }

  function onSubmitFilters(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    applyQuery({ keyword: draftKeyword, page: 1 });
  }

  if (!canRead) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <PageHeader
          title={tNav("closed")}
          breadcrumbs={[
            { label: tCommon("home"), href: "/dashboard" },
            { label: tNav("closed") },
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
      header: t("listCaseColumn"),
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
                  ? tCommon("emDash")
                  : t("noCaseYet");
        const complaintLabel = row.complaint.complaintNumber;
        const secondaryClass =
          "mt-0.5 block truncate font-mono text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary underline-offset-2 hover:underline hover:text-ecmp-primary";
        return (
          <div className="min-w-0">
            <Link href={caseHref} className={numberLinkClass(false)}>
              {caseLabel}
            </Link>
            <Link href={complaintHref} className={secondaryClass}>
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
        row.caseItem?.subject?.trim() || row.complaint.subject?.trim() || "—",
    },
    {
      key: "status",
      header: t("status"),
      cell: (row) => (
        <Badge
          tone={
            closedArchivePathLabelKey(row.complaint.intakeDisposition) ===
            "tagHqCompleted"
              ? "info"
              : "success"
          }
        >
          {t(closedArchivePathLabelKey(row.complaint.intakeDisposition))}
        </Badge>
      ),
    },
    {
      key: "sla",
      header: t("slaColumn"),
      cell: (row) => <ComplaintSlaBadge sla={row.complaint.sla} />,
    },
    {
      key: "customer",
      header: t("customer"),
      cell: (row) => {
        const { name, id } = customerCellLabel(row.complaint, tCommon("emDash"));
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
  ];

  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const rangeFrom = total === 0 ? 0 : (page - 1) * pageSize + 1;
  const rangeTo = Math.min(page * pageSize, total);
  const hasKeyword = Boolean(keyword.trim());

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        overline={t("overline")}
        title={t("aggregateListTitleClosed")}
        description={
          pusatAudience === true
            ? t("aggregateListDescriptionClosedPusat")
            : t("aggregateListDescriptionClosed")
        }
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: tNav("closed") },
        ]}
      />

      <form onSubmit={onSubmitFilters} aria-label={t("filtersAriaLabel")}>
        <FilterBar
          inline
          search={
            <Input
              name="keyword"
              label={tCommon("search")}
              placeholder={t("aggregateSearchPlaceholder")}
              value={draftKeyword}
              onChange={(e) => setDraftKeyword(e.target.value)}
              maxLength={200}
            />
          }
          actions={<Button type="submit">{t("applyFilters")}</Button>}
        />
      </form>

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
              title={t("aggregateListEmptyClosed")}
              description={
                hasKeyword
                  ? t("aggregateListEmptyFiltered")
                  : t("aggregateListEmptyDescriptionClosed")
              }
              primaryAction={
                hasKeyword
                  ? {
                      label: t("clearFilters"),
                      onClick: () => applyQuery({ keyword: "", page: 1 }),
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
              />
              <Pagination
                summary={tCommon("pageOf", {
                  page,
                  totalPages,
                })}
                previousLabel={tCommon("previous")}
                nextLabel={tCommon("next")}
                previousDisabled={page <= 1 || loading}
                nextDisabled={page >= totalPages || loading}
                onPrevious={() => applyQuery({ page: Math.max(1, page - 1) })}
                onNext={() =>
                  applyQuery({ page: Math.min(totalPages, page + 1) })
                }
              />
            </>
          )}
        </CardBody>
      </Card>
    </PageContainer>
  );
}
