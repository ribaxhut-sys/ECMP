"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  fetchCmBatch1Customer360,
  fetchCmCases,
  fetchCustomers,
  type CmCaseStatus,
  type CmCaseSummary,
} from "@/lib/api";
import {
  Badge,
  Button,
  Empty,
  ErrorState,
  PageContainer,
  PageHeader,
  Select,
  Skeleton,
  Table,
  type TableColumn,
} from "@/shared/ui";
import { CaseStatusBadge } from "./CaseStatusBadge";

const PAGE_SIZE = 20;

const CASE_STATUS_FILTERS: CmCaseStatus[] = [
  "CREATED",
  "ASSIGNED",
  "IN_PROGRESS",
  "RESOLVED",
  "CLOSED",
  "CANCELLED",
];

function looksLikeUuid(value: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(
    value.trim(),
  );
}

function profileText(
  profile: Record<string, unknown> | null | undefined,
  ...keys: string[]
): string | null {
  if (!profile) return null;
  for (const key of keys) {
    const value = profile[key];
    if (typeof value === "string" && value.trim()) return value.trim();
  }
  return null;
}

type CustomerListLabel = { name: string; number: string | null };

function customerListLabel(
  name: string | null | undefined,
  number: string | null | undefined,
): CustomerListLabel | null {
  const displayName = (name || "").trim();
  const displayNumber = (number || "").trim();
  if (!displayName && !displayNumber) return null;
  if (displayName && displayNumber && displayName !== displayNumber) {
    return { name: displayName, number: displayNumber };
  }
  return { name: displayName || displayNumber, number: null };
}

function putCustomerLabel(
  map: Record<string, CustomerListLabel>,
  keys: Array<string | null | undefined>,
  label: CustomerListLabel | null,
) {
  if (!label) return;
  for (const key of keys) {
    const id = (key || "").trim();
    if (id) map[id] = label;
  }
}

function customerLabelForId(
  customerId: string | null | undefined,
  labels: Record<string, CustomerListLabel>,
  emDash: string,
): CustomerListLabel {
  const id = (customerId || "").trim();
  if (!id) return { name: emDash, number: null };
  if (labels[id]) return labels[id];
  if (looksLikeUuid(id)) return { name: emDash, number: null };
  return { name: id, number: null };
}

/**
 * DEC-024 / API-536 — visibility-scoped Case inbox for the signed-in principal.
 */
export function CaseInboxListView() {
  const t = useTranslations("cases");
  const tCommon = useTranslations("common");
  const tStatus = useTranslations("status");
  const tPriority = useTranslations("priority");
  const tErrors = useTranslations("errors");
  const router = useRouter();
  const { hasPermission } = useAuth();
  const canRead = hasPermission("complaints:read");

  const [rows, setRows] = useState<CmCaseSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState("");
  const [draftStatus, setDraftStatus] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [customerLabels, setCustomerLabels] = useState<
    Record<string, CustomerListLabel>
  >({});

  const load = useCallback(async () => {
    if (!canRead) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetchCmCases({
        page,
        pageSize: PAGE_SIZE,
        status: statusFilter || undefined,
      });
      setRows(res.data ?? []);
      setTotal(res.meta?.totalItems ?? res.data?.length ?? 0);
    } catch (err) {
      setRows([]);
      setTotal(0);
      setError(
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : t("unableToLoadList"),
      );
    } finally {
      setLoading(false);
    }
  }, [canRead, page, statusFilter, t, tErrors, tCommon]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    const ids = [
      ...new Set(
        rows
          .map((row) => row.customerId?.trim())
          .filter((id): id is string => Boolean(id)),
      ),
    ];
    if (ids.length === 0) {
      setCustomerLabels({});
      return;
    }
    let cancelled = false;
    void (async () => {
      const [customersRes, ...profiles] = await Promise.all([
        fetchCustomers(200).catch(() => null),
        ...ids.map(async (id) => {
          const res = await fetchCmBatch1Customer360(id).catch(() => null);
          return [id, res] as const;
        }),
      ]);
      const next: Record<string, CustomerListLabel> = {};
      for (const customer of customersRes?.data ?? []) {
        const name = customer.fullName?.trim();
        const number = customer.externalCustomerId?.trim();
        putCustomerLabel(
          next,
          [customer.id, number],
          customerListLabel(name, number),
        );
      }
      for (const [id, res] of profiles) {
        if (next[id]) continue;
        const profile = res?.data?.profile as
          | Record<string, unknown>
          | undefined;
        const name = profileText(profile, "displayName", "fullName", "name");
        const number = profileText(
          profile,
          "customerNumber",
          "customer_number",
          "externalId",
        );
        putCustomerLabel(next, [id, number], customerListLabel(name, number));
      }
      if (!cancelled) setCustomerLabels(next);
    })();
    return () => {
      cancelled = true;
    };
  }, [rows]);

  const statusOptions = useMemo(
    () => [
      { value: "", label: t("allStatuses") },
      ...CASE_STATUS_FILTERS.map((status) => ({
        value: status,
        label: tStatus.has(status as "IN_PROGRESS")
          ? tStatus(status as "IN_PROGRESS")
          : status,
      })),
    ],
    [t, tStatus],
  );

  if (!canRead) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <PageHeader title={t("inboxTitle")} />
        <Empty
          title={t("accessDenied")}
          description={t("readPermission")}
          primaryAction={{
            label: tCommon("goHome"),
            onClick: () => router.push("/dashboard"),
          }}
        />
      </PageContainer>
    );
  }

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const from = total === 0 ? 0 : (page - 1) * PAGE_SIZE + 1;
  const to = Math.min(page * PAGE_SIZE, total);

  const columns: TableColumn<CmCaseSummary>[] = [
    {
      key: "caseNumber",
      header: t("caseNumber"),
      headerClassName: "whitespace-nowrap",
      className: "whitespace-nowrap",
      cell: (row) => (
        <div className="flex min-w-0 max-w-[16rem] items-center gap-1.5">
          <Link
            href={`/complaints/cm/cases/${encodeURIComponent(row.caseId)}`}
            className={
              row.isRead === false
                ? "min-w-0 truncate font-semibold text-ecmp-primary underline-offset-2 hover:underline"
                : "min-w-0 truncate font-medium text-ecmp-primary underline-offset-2 hover:underline"
            }
          >
            {row.caseNumber}
          </Link>
          {row.isRead === false && row.unreadReason ? (
            <Badge tone="warning" className="shrink-0">
              {row.unreadReason === "HQ_SCHEDULED"
                ? t("unreadHqScheduled")
                : t("unreadReturned")}
            </Badge>
          ) : null}
        </div>
      ),
    },
    {
      key: "subject",
      header: t("subject"),
      className: "max-w-[14rem]",
      cell: (row) => (
        <span className="block truncate">
          {row.subject?.trim() || tCommon("emDash")}
        </span>
      ),
    },
    {
      key: "priority",
      header: t("priority"),
      headerClassName: "whitespace-nowrap",
      className: "whitespace-nowrap",
      cell: (row) => {
        const key = (row.priority || "").toUpperCase();
        if (!key) return tCommon("emDash");
        return tPriority.has(key as "HIGH")
          ? tPriority(key as "HIGH")
          : row.priority;
      },
    },
    {
      key: "customer",
      header: t("customer"),
      mobileLabel: t("customer"),
      className: "max-w-[12rem]",
      cell: (row) => {
        const label = customerLabelForId(
          row.customerId,
          customerLabels,
          tCommon("emDash"),
        );
        return (
          <span className="block truncate font-medium text-ecmp-text-primary">
            {label.name}
          </span>
        );
      },
    },
    {
      key: "customerNumber",
      header: t("customerNumber"),
      mobileLabel: t("customerNumber"),
      headerClassName: "whitespace-nowrap",
      className: "whitespace-nowrap font-mono",
      cell: (row) => {
        const label = customerLabelForId(
          row.customerId,
          customerLabels,
          tCommon("emDash"),
        );
        return (
          <span className="block truncate font-mono text-ecmp-text-secondary">
            {label.number || tCommon("emDash")}
          </span>
        );
      },
    },
    {
      key: "status",
      header: tCommon("status"),
      headerClassName: "whitespace-nowrap",
      className: "whitespace-nowrap",
      cell: (row) => <CaseStatusBadge status={row.status} />,
    },
  ];

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={t("inboxTitle")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("inboxTitle") },
        ]}
        actions={
          <Button
            type="button"
            variant="outline"
            onClick={() => router.push("/complaints")}
          >
            {t("goToComplaints")}
          </Button>
        }
      />

      <form
        aria-label={t("filtersAriaLabel")}
        className="sticky top-0 z-[calc(var(--ecmp-z-sticky-header)-1)] flex flex-col gap-2 rounded-[var(--ecmp-radius-search)] border border-ecmp-border/80 bg-ecmp-surface/95 px-3 py-2.5 shadow-ecmp-raised backdrop-blur-sm sm:flex-row sm:items-center sm:justify-between sm:gap-3"
        onSubmit={(event) => {
          event.preventDefault();
          setPage(1);
          setStatusFilter(draftStatus);
        }}
      >
        <div className="flex min-w-0 flex-wrap items-center gap-2">
          <span className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
            {tCommon("showingItems", { from, to, total })}
          </span>
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={() => void load()}
          >
            {tCommon("refresh")}
          </Button>
        </div>
        <div className="flex min-w-0 flex-wrap items-center justify-end gap-2">
          <div className="w-[13rem] shrink-0">
            <Select
              name="status"
              aria-label={tCommon("status")}
              options={statusOptions}
              value={draftStatus}
              onChange={(event) => setDraftStatus(event.target.value)}
            />
          </div>
          {statusFilter || draftStatus ? (
            <Button
              type="button"
              size="sm"
              variant="ghost"
              onClick={() => {
                setDraftStatus("");
                setStatusFilter("");
                setPage(1);
              }}
            >
              {tCommon("reset")}
            </Button>
          ) : null}
          <Button type="submit" size="sm">
            {t("applyFilters")}
          </Button>
        </div>
      </form>

      {error ? (
        <ErrorState
          title={t("unableToLoadList")}
          message={error}
          onRetry={() => void load()}
        />
      ) : null}

      {loading && rows.length === 0 ? <Skeleton rows={6} /> : null}

      {!loading && !error && rows.length === 0 ? (
        <Empty
          title={t("inboxEmpty")}
          description={
            statusFilter
              ? t("inboxEmptyFilterDescription")
              : t("inboxEmptyDescription")
          }
          primaryAction={{
            label: t("goToComplaints"),
            onClick: () => router.push("/complaints"),
          }}
        />
      ) : null}

      {rows.length > 0 ? (
        <>
          <Table
            columns={columns}
            rows={rows}
            getRowKey={(row) => row.caseId}
            density="compact"
            stickyHeader
            className="[--ecmp-font-table-size:0.9375rem] [--ecmp-density-compact-cell-y:6px]"
            getRowClassName={(row) =>
              row.isRead === false ? "font-semibold" : undefined
            }
          />
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <span className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
              {tCommon("showingItems", { from, to, total })}
              {totalPages > 1 ? (
                <>
                  <span className="mx-2 text-ecmp-border">·</span>
                  {tCommon("pageOf", { page, totalPages })}
                </>
              ) : null}
            </span>
            {totalPages > 1 ? (
              <div className="flex items-center gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={page <= 1 || loading}
                  onClick={() => setPage((current) => Math.max(1, current - 1))}
                >
                  {tCommon("previous")}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={page >= totalPages || loading}
                  onClick={() =>
                    setPage((current) => Math.min(totalPages, current + 1))
                  }
                >
                  {tCommon("next")}
                </Button>
              </div>
            ) : null}
          </div>
        </>
      ) : null}
    </PageContainer>
  );
}
