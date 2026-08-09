"use client";

import { useMemo } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import {
  Alert,
  Button,
  Card,
  CardBody,
  Empty,
  PageContainer,
  PageHeader,
  Table,
  type TableColumn,
} from "@/shared/ui";
import { useInternalComplaints } from "./mock/useInternalComplaints";
import { sortByMostRecent } from "./internalComplaintsFilters";
import type { InternalComplaint } from "./types";
import {
  InternalPriorityBadge,
  InternalStatusBadge,
} from "./components/InternalBadges";

export function InternalDashboardView() {
  const router = useRouter();
  const t = useTranslations("internalComplaints");
  const tCommon = useTranslations("common");
  const { rows, loading, error } = useInternalComplaints();
  const recent = useMemo(() => sortByMostRecent(rows).slice(0, 8), [rows]);

  const openCount = rows.filter((r) => r.status !== "CLOSED").length;
  const resolvedCount = rows.filter((r) => r.status === "RESOLVED").length;
  const closedCount = rows.filter((r) => r.status === "CLOSED").length;

  const columns: TableColumn<InternalComplaint>[] = [
    {
      key: "number",
      header: t("number"),
      cell: (row) => (
        <button
          type="button"
          className="font-medium text-ecmp-primary underline-offset-2 hover:underline"
          onClick={() =>
            router.push(`/internal/complaints/${encodeURIComponent(row.id)}`)
          }
        >
          {row.number}
        </button>
      ),
    },
    { key: "title", header: t("titleField"), cell: (row) => row.title },
    {
      key: "status",
      header: t("status"),
      cell: (row) => <InternalStatusBadge status={row.status} />,
    },
    {
      key: "priority",
      header: t("priority"),
      cell: (row) => <InternalPriorityBadge priority={row.priority} />,
    },
  ];

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={t("title")}
        description={t("dashboardDescription")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title") },
        ]}
        actions={
          <Button type="button" onClick={() => router.push("/internal/complaints/new")}>
            {t("create")}
          </Button>
        }
      />
      {error ? <Alert tone="danger" title={error} /> : null}
      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardBody>
            <div className="text-sm text-ecmp-text-secondary">{t("kpiOpen")}</div>
            <div className="text-2xl font-semibold">{openCount}</div>
          </CardBody>
        </Card>
        <Card>
          <CardBody>
            <div className="text-sm text-ecmp-text-secondary">{t("kpiResolved")}</div>
            <div className="text-2xl font-semibold">{resolvedCount}</div>
          </CardBody>
        </Card>
        <Card>
          <CardBody>
            <div className="text-sm text-ecmp-text-secondary">{t("kpiClosed")}</div>
            <div className="text-2xl font-semibold">{closedCount}</div>
          </CardBody>
        </Card>
      </div>
      <Card>
        <CardBody>
          {loading ? (
            <Empty title={tCommon("loading")} description="" />
          ) : recent.length === 0 ? (
            <Empty title={t("listEmpty")} description={t("listEmptyDescription")} />
          ) : (
            <Table columns={columns} rows={recent} getRowKey={(row) => row.id} />
          )}
        </CardBody>
      </Card>
    </PageContainer>
  );
}
