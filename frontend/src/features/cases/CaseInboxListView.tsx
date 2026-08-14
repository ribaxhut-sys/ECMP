"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
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

function customerLabelForId(
  customerId: string | null | undefined,
  labels: Record<string, string>,
  emDash: string,
): string {
  const id = (customerId || "").trim();
  if (!id) return emDash;
  if (labels[id]) return labels[id];
  if (looksLikeUuid(id)) return emDash;
  return id;
}

/**
 * DEC-024 / API-536 — visibility-scoped Case inbox for the signed-in principal.
 */
export function CaseInboxListView() {
  const t = useTranslations("cases");
  const tCommon = useTranslations("common");
  const tTable = useTranslations("table");
  const tStatus = useTranslations("status");
  const tPriority = useTranslations("priority");
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
  const [customerLabels, setCustomerLabels] = useState<Record<string, string>>(
    {},
  );

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
        err instanceof ApiError ? err.message : t("unableToLoadList"),
      );
    } finally {
      setLoading(false);
    }
  }, [canRead, page, statusFilter, t]);

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
      const next: Record<string, string> = {};
      for (const customer of customersRes?.data ?? []) {
        const name = customer.fullName?.trim();
        if (!name) continue;
        const number = customer.externalCustomerId?.trim();
        const label =
          number && number !== name ? `${name} (${number})` : name;
        next[customer.id] = label;
        if (number) next[number] = label;
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
        if (name) {
          next[id] =
            number && number !== name ? `${name} (${number})` : name;
        } else if (number) {
          next[id] = number;
        }
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
      cell: (row) => (
        <Link
          href={`/complaints/cm/cases/${encodeURIComponent(row.caseId)}`}
          className="font-medium text-ecmp-primary underline-offset-2 hover:underline"
        >
          {row.caseNumber}
        </Link>
      ),
    },
    {
      key: "subject",
      header: t("subject"),
      cell: (row) => row.subject?.trim() || "—",
    },
    {
      key: "status",
      header: tCommon("status"),
      headerClassName: "whitespace-nowrap",
      className: "whitespace-nowrap",
      cell: (row) => <CaseStatusBadge status={row.status} />,
    },
    {
      key: "priority",
      header: t("priority"),
      cell: (row) => {
        const key = (row.priority || "").toUpperCase();
        if (!key) return "—";
        return tPriority.has(key as "HIGH")
          ? tPriority(key as "HIGH")
          : row.priority;
      },
    },
    {
      key: "customer",
      header: t("customer"),
      hideOnMobile: true,
      cell: (row) =>
        customerLabelForId(row.customerId, customerLabels, tCommon("emDash")),
    },
    {
      key: "unit",
      header: t("unit"),
      hideOnMobile: true,
      cell: (row) => row.owningUnitId ?? row.ownerUnitId ?? "—",
    },
  ];

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={t("inboxTitle")}
        description={t("inboxDescription")}
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
            {tTable("itemsInView", { count: rows.length })}
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
