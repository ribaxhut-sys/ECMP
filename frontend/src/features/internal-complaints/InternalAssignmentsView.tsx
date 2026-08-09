"use client";

import { useMemo } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import {
  Alert,
  Empty,
  PageContainer,
  PageHeader,
  Table,
  type TableColumn,
} from "@/shared/ui";
import { useInternalComplaints } from "./mock/useInternalComplaints";
import type { InternalComplaint } from "./types";
import { InternalStatusBadge } from "./components/InternalBadges";

function FilteredList({
  title,
  description,
  statuses,
}: {
  title: string;
  description: string;
  statuses: readonly string[];
}) {
  const router = useRouter();
  const t = useTranslations("internalComplaints");
  const tCommon = useTranslations("common");
  const { rows, loading, error } = useInternalComplaints();
  const filtered = useMemo(
    () => rows.filter((r) => statuses.includes(String(r.status))),
    [rows, statuses],
  );

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
    { key: "handling", header: t("handlingUnit"), cell: (row) => row.handlingUnitId },
    {
      key: "status",
      header: t("status"),
      cell: (row) => <InternalStatusBadge status={row.status} />,
    },
  ];

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={title}
        description={description}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title"), href: "/internal" },
          { label: title },
        ]}
      />
      {error ? <Alert tone="danger" title={error} /> : null}
      {loading ? (
        <Empty title={tCommon("loading")} description="" />
      ) : filtered.length === 0 ? (
        <Empty title={t("listEmpty")} description={t("listEmptyDescription")} />
      ) : (
        <Table columns={columns} rows={filtered} getRowKey={(row) => row.id} />
      )}
    </PageContainer>
  );
}

export function InternalAssignmentsView() {
  const t = useTranslations("internalComplaints");
  return (
    <FilteredList
      title={t("assignmentsTitle")}
      description={t("assignmentsDescription")}
      statuses={["ASSIGNED", "CREATED"]}
    />
  );
}

export function InternalFollowUpListView() {
  const t = useTranslations("internalComplaints");
  return (
    <FilteredList
      title={t("followUpTitle")}
      description={t("followUpDescription")}
      statuses={["IN_PROGRESS"]}
    />
  );
}

export function InternalVerificationListView() {
  const t = useTranslations("internalComplaints");
  return (
    <FilteredList
      title={t("verificationTitle")}
      description={t("verificationDescription")}
      statuses={["RESOLVED"]}
    />
  );
}

export function InternalReportsView() {
  const t = useTranslations("internalComplaints");
  return (
    <FilteredList
      title={t("reportsTitle")}
      description={t("reportsDescription")}
      statuses={["CLOSED", "RESOLVED", "IN_PROGRESS", "ASSIGNED", "CREATED"]}
    />
  );
}
