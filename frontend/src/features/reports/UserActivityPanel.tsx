"use client";

import { useEffect, useMemo, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import type { UserActivityCount } from "@/lib/api/types";
import { formatDateTime24 } from "@/shared/utils/datetime";
import {
  Pagination,
  SectionHeader,
  Select,
  Table,
  type TableColumn,
} from "@/shared/ui";

const PAGE_SIZE_OPTIONS = [10, 25, 50] as const;
const DEFAULT_PAGE_SIZE = 10;
const ALL_BRANCHES = "";
const NO_BRANCH = "__none__";

export function UserActivityPanel({
  rows,
  loading,
}: {
  rows: UserActivityCount[] | null;
  loading: boolean;
}) {
  const t = useTranslations("reports");
  const tCommon = useTranslations("common");
  const tTable = useTranslations("table");
  const locale = useLocale();

  const allRows = useMemo(() => rows ?? [], [rows]);

  const [branchFilter, setBranchFilter] = useState(ALL_BRANCHES);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState<number>(DEFAULT_PAGE_SIZE);

  // A reload (period/unit change on the page above) swaps `rows` for a new
  // array — any branch picked against the previous set may no longer exist,
  // so start over rather than silently show a stale, now-empty filter.
  useEffect(() => {
    setBranchFilter(ALL_BRANCHES);
    setPage(1);
  }, [allRows]);

  const branchOptions = useMemo(() => {
    const seen = new Map<string, string>();
    for (const row of allRows) {
      const key = row.branchId ?? NO_BRANCH;
      if (!seen.has(key)) seen.set(key, row.branchName || tCommon("emDash"));
    }
    return [
      { value: ALL_BRANCHES, label: t("userActivityAllBranches") },
      ...Array.from(seen, ([value, label]) => ({ value, label })).sort((a, b) =>
        a.label.localeCompare(b.label, locale),
      ),
    ];
  }, [allRows, locale, t, tCommon]);

  const filteredRows = useMemo(
    () =>
      branchFilter === ALL_BRANCHES
        ? allRows
        : allRows.filter((row) => (row.branchId ?? NO_BRANCH) === branchFilter),
    [allRows, branchFilter],
  );

  const totalItems = filteredRows.length;
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize) || 1);

  useEffect(() => {
    setPage((current) => Math.min(current, totalPages));
  }, [totalPages]);

  const pageRows = useMemo(
    () => filteredRows.slice((page - 1) * pageSize, (page - 1) * pageSize + pageSize),
    [filteredRows, page, pageSize],
  );

  const columns = useMemo<TableColumn<UserActivityCount>[]>(
    () => [
      {
        key: "user",
        header: t("userActivityUser"),
        cell: (row) => (
          <span className="flex min-w-0 flex-col">
            <span className="font-medium text-ecmp-text-primary">
              {row.displayName}
            </span>
            {row.username ? (
              <span className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                {row.username}
              </span>
            ) : null}
          </span>
        ),
      },
      {
        key: "unit",
        header: t("userActivityUnit"),
        cell: (row) => row.branchName || "—",
      },
      {
        key: "created",
        header: t("userActivityCreated"),
        cell: (row) => (
          <span className="tabular-nums">{row.createdCount}</span>
        ),
      },
      {
        key: "decided",
        header: t("userActivityDecided"),
        cell: (row) => (
          <span className="tabular-nums">{row.decidedCount}</span>
        ),
      },
      {
        key: "closed",
        header: t("userActivityClosed"),
        cell: (row) => (
          <span className="tabular-nums">{row.closedCount}</span>
        ),
      },
      {
        key: "activity",
        header: t("userActivityEvents"),
        cell: (row) => (
          <span className="tabular-nums">{row.activityCount}</span>
        ),
      },
      {
        key: "last",
        header: t("userActivityLast"),
        hideOnMobile: true,
        cell: (row) =>
          formatDateTime24(row.lastActivityAt, locale, "—"),
      },
    ],
    [locale, t],
  );

  const pageSizeOptions = useMemo(
    () =>
      PAGE_SIZE_OPTIONS.map((count) => ({
        value: String(count),
        label: tTable("perPage", { count }),
      })),
    [tTable],
  );

  return (
    <section
      className="space-y-[var(--ecmp-panel-gap)]"
      aria-label={t("userActivity")}
    >
      <SectionHeader
        title={t("userActivity")}
        description={t("userActivityDescription")}
      />
      <Table
        columns={columns}
        rows={pageRows}
        getRowKey={(row) => row.userId}
        loading={loading}
        caption={t("userActivity")}
        density="compact"
        emptyTitle={t("noUserActivity")}
        emptyMessage={t("noUserActivityDescription")}
        toolbar={
          branchOptions.length > 2 ? (
            <div className="w-[14rem]">
              <Select
                name="userActivityBranchFilter"
                label={t("userActivityFilterLabel")}
                options={branchOptions}
                value={branchFilter}
                disabled={loading}
                onChange={(e) => {
                  setBranchFilter(e.target.value);
                  setPage(1);
                }}
              />
            </div>
          ) : undefined
        }
      />
      {!loading && totalItems > 0 ? (
        <Pagination
          summary={tCommon("showingItems", {
            from: (page - 1) * pageSize + 1,
            to: Math.min(page * pageSize, totalItems),
            total: totalItems,
          })}
          pageSizeSlot={
            <div className="w-[9rem]">
              <Select
                name="userActivityPageSize"
                aria-label={t("userActivityPageSizeLabel")}
                options={pageSizeOptions}
                value={String(pageSize)}
                onChange={(e) => {
                  setPageSize(Number(e.target.value) || DEFAULT_PAGE_SIZE);
                  setPage(1);
                }}
              />
            </div>
          }
          previousLabel={tCommon("previous")}
          nextLabel={tCommon("next")}
          onPrevious={() => setPage((p) => Math.max(1, p - 1))}
          onNext={() => setPage((p) => Math.min(totalPages, p + 1))}
          previousDisabled={page <= 1}
          nextDisabled={page >= totalPages}
        />
      ) : null}
    </section>
  );
}
