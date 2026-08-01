"use client";

import Link from "next/link";
import { useLocale, useTranslations } from "next-intl";
import type { DashboardRecentActivityItem } from "@/lib/api/types";
import { formatDateTime } from "@/i18n/formatting";
import {
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  Empty,
  Skeleton,
  Table,
  type TableColumn,
} from "@/shared/ui";

export function RecentActivity({
  rows,
  loading,
}: {
  rows: DashboardRecentActivityItem[] | null;
  loading: boolean;
}) {
  const t = useTranslations("dashboard");
  const locale = useLocale();

  const columns: TableColumn<DashboardRecentActivityItem>[] = [
    {
      key: "eventType",
      header: t("eventType"),
      cell: (row) => (
        <span className="font-mono text-[length:var(--ecmp-font-caption-size)]">
          {row.eventType}
        </span>
      ),
    },
    {
      key: "complaintNumber",
      header: t("complaintNumberColumn"),
      cell: (row) => (
        <Link
          href={`/complaints?keyword=${encodeURIComponent(row.complaintNumber)}`}
          className="font-mono text-[length:var(--ecmp-font-caption-size)] text-ecmp-primary hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-focus"
        >
          {row.complaintNumber}
        </Link>
      ),
    },
    {
      key: "timestamp",
      header: t("timestamp"),
      cell: (row) => (
        <span className="text-ecmp-text-secondary">
          {formatDateTime(row.timestamp, locale)}
        </span>
      ),
    },
    {
      key: "actor",
      header: t("actor"),
      cell: (row) => <span>{row.actor}</span>,
    },
  ];

  if (loading) {
    return (
      <Card data-testid="dashboard-recent-activity">
        <CardHeader>
          <CardTitle>{t("recentActivity")}</CardTitle>
        </CardHeader>
        <CardBody>
          <Skeleton rows={5} />
        </CardBody>
      </Card>
    );
  }

  if (!rows || rows.length === 0) {
    return (
      <Card data-testid="dashboard-recent-activity">
        <CardHeader>
          <CardTitle>{t("recentActivity")}</CardTitle>
        </CardHeader>
        <CardBody>
          <Empty
            title={t("noActivity")}
            description={t("noActivityDescription")}
          />
        </CardBody>
      </Card>
    );
  }

  return (
    <Card data-testid="dashboard-recent-activity">
      <CardHeader>
        <CardTitle>{t("recentActivity")}</CardTitle>
      </CardHeader>
      <CardBody>
        <Table
          columns={columns}
          rows={rows}
          getRowKey={(row, index) =>
            `${row.complaintNumber}-${row.eventType}-${row.timestamp}-${index}`
          }
          caption={t("recentActivity")}
          emptyMessage={t("noActivityDescription")}
        />
      </CardBody>
    </Card>
  );
}
