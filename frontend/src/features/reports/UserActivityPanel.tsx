"use client";

import { useMemo } from "react";
import { useLocale, useTranslations } from "next-intl";
import type { UserActivityCount } from "@/lib/api/types";
import { formatDateTime24 } from "@/shared/utils/datetime";
import {
  SectionHeader,
  Table,
  type TableColumn,
} from "@/shared/ui";

export function UserActivityPanel({
  rows,
  loading,
}: {
  rows: UserActivityCount[] | null;
  loading: boolean;
}) {
  const t = useTranslations("reports");
  const locale = useLocale();

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
        rows={rows ?? []}
        getRowKey={(row) => row.userId}
        loading={loading}
        caption={t("userActivity")}
        density="compact"
        emptyTitle={t("noUserActivity")}
        emptyMessage={t("noUserActivityDescription")}
      />
    </section>
  );
}
