"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import type { Complaint } from "@/lib/api/types";
import { formatDateTime } from "@/i18n/formatting";
import {
  Badge,
  Card,
  CardBody,
  CardHeader,
  PanelHeader,
  Empty,
  Skeleton,
  Table,
  type BadgeTone,
  type TableColumn,
} from "@/shared/ui";

function priorityTone(priority: string): BadgeTone {
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

export function LatestComplaints({
  rows,
  loading,
  onRefresh,
}: {
  rows: Complaint[] | null;
  loading: boolean;
  onRefresh?: () => void;
}) {
  const router = useRouter();
  const t = useTranslations("dashboard");
  const tComplaints = useTranslations("complaints");
  const tStatus = useTranslations("status");
  const tPriority = useTranslations("priority");
  const tCommon = useTranslations("common");
  const locale = useLocale();

  const columns: TableColumn<Complaint>[] = [
    {
      key: "number",
      header: t("number"),
      cell: (row) => (
        <Link
          href={`/complaints/${row.id}`}
          className="font-mono text-[length:var(--ecmp-font-caption-size)] text-ecmp-primary hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-focus"
        >
          {row.complaintNumber}
        </Link>
      ),
    },
    {
      key: "subject",
      header: tComplaints("subject"),
      cell: (row) => <span className="line-clamp-2">{row.subject}</span>,
    },
    {
      key: "status",
      header: tComplaints("status"),
      cell: (row) => (
        <Badge tone="neutral">{tStatus(row.status)}</Badge>
      ),
    },
    {
      key: "priority",
      header: tComplaints("priority"),
      cell: (row) => (
        <Badge tone={priorityTone(row.priority)}>{tPriority(row.priority)}</Badge>
      ),
    },
    {
      key: "created",
      header: tComplaints("createdAt"),
      cell: (row) => (
        <span className="text-ecmp-text-secondary">
          {formatDateTime(row.createdAt, locale)}
        </span>
      ),
    },
  ];

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <PanelHeader title={t("recentComplaints")} className="mb-0 border-0 pb-0" />
        </CardHeader>
        <CardBody>
          <Skeleton rows={5} />
        </CardBody>
      </Card>
    );
  }

  if (!rows || rows.length === 0) {
    return (
      <Card>
        <CardHeader>
          <PanelHeader title={t("recentComplaints")} className="mb-0 border-0 pb-0" />
        </CardHeader>
        <CardBody>
          <Empty
            title={t("noComplaints")}
            description={t("noComplaintsDescription")}
            primaryAction={{
              label: t("refreshDashboard"),
              onClick: onRefresh,
            }}
            secondaryAction={{
              label: tCommon("goToComplaints"),
              onClick: () => router.push("/complaints"),
            }}
          />
        </CardBody>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <PanelHeader title={t("recentComplaints")} className="mb-0 border-0 pb-0" />
      </CardHeader>
      <CardBody>
        <Table
          columns={columns}
          rows={rows}
          getRowKey={(row) => row.id}
          caption={t("recentComplaints")}
          emptyMessage={t("noComplaintsDescription")}
        />
      </CardBody>
    </Card>
  );
}
