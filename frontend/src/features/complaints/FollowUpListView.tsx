"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { ApiError, fetchCmBatch1Complaints, fetchCmCases } from "@/lib/api";
import {
  Badge,
  Button,
  Card,
  CardBody,
  Empty,
  ErrorState,
  PageContainer,
  PageHeader,
  Skeleton,
  Table,
  WorkspaceToolbar,
  type BadgeTone,
  type TableColumn,
} from "@/shared/ui";
import {
  buildFollowUpRows,
  followUpRowHref,
  type FollowUpRow,
  type FollowUpStatusKey,
} from "./followUpRows";

/** Fetch page size for the coexistence read. Larger lists are not paginated
 * here — see the visibility limitation note in the DoD deliverable. */
const FOLLOW_UP_FETCH_PAGE_SIZE = 100;

function statusTone(statusKey: FollowUpStatusKey): BadgeTone {
  switch (statusKey) {
    case "awaitingApproval":
      return "warning";
    case "hqPath":
      return "info";
    case "returnedToBranch":
      return "warning";
    case "caseWorking":
      return "primary";
    case "caseNew":
      return "neutral";
    case "noHandling":
      return "neutral";
    default:
      return "neutral";
  }
}

/**
 * Tindak lanjut — union work list of Case (Penanganan) and Complaint
 * (Pengaduan) rows. Presentation-only composition over API-514 / API-536;
 * no new API surface. See followUpRows.ts for the merge/filter/sort rules.
 */
export function FollowUpListView() {
  const router = useRouter();
  const t = useTranslations("followUp");
  const tCommon = useTranslations("common");
  const tTable = useTranslations("table");
  const { hasPermission } = useAuth();
  const canRead = hasPermission("complaints:read");

  const [rows, setRows] = useState<FollowUpRow[]>([]);
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
      const [complaintsRes, casesRes] = await Promise.all([
        fetchCmBatch1Complaints({ page: 1, pageSize: FOLLOW_UP_FETCH_PAGE_SIZE }),
        fetchCmCases({ page: 1, pageSize: FOLLOW_UP_FETCH_PAGE_SIZE }),
      ]);
      setRows(
        buildFollowUpRows({
          complaints: complaintsRes.data ?? [],
          allCases: casesRes.data ?? [],
        }),
      );
    } catch (err) {
      setRows([]);
      setError(err instanceof ApiError ? err.message : t("unableToLoad"));
    } finally {
      setLoading(false);
    }
  }, [canRead, t]);

  useEffect(() => {
    void load();
  }, [load]);

  function statusLabel(row: FollowUpRow): string {
    switch (row.statusKey) {
      case "awaitingApproval":
        return t("statusAwaitingApproval");
      case "hqPath":
        return row.kind === "case"
          ? t("statusCaseHqPath")
          : t("statusHqPath");
      case "returnedToBranch":
        return t("statusReturnedToBranch");
      case "caseWorking":
        return t("statusCaseWorking");
      case "caseNew":
        return t("statusCaseNew");
      case "noHandling":
        return t("statusNoHandling");
      default:
        return row.statusKey;
    }
  }

  function openRow(row: FollowUpRow): void {
    router.push(followUpRowHref(row));
  }

  if (!canRead) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <PageHeader
          title={t("title")}
          breadcrumbs={[
            { label: tCommon("home"), href: "/dashboard" },
            { label: t("title") },
          ]}
        />
        <Empty
          title={tCommon("accessRestricted")}
          description={t("accessDescription")}
          primaryAction={{
            label: tCommon("goHome"),
            onClick: () => router.push("/dashboard"),
          }}
        />
      </PageContainer>
    );
  }

  const columns: TableColumn<FollowUpRow>[] = [
    {
      key: "number",
      header: t("columnNumber"),
      cell: (row) => (
        <Link
          href={followUpRowHref(row)}
          className="cursor-pointer font-medium text-ecmp-primary underline-offset-2 hover:underline"
        >
          {row.number}
        </Link>
      ),
    },
    {
      key: "parent",
      header: t("columnParent"),
      cell: (row) =>
        row.parentComplaintId ? (
          <Link
            href={`/complaints/cm/${encodeURIComponent(row.parentComplaintId)}`}
            className="cursor-pointer font-medium text-ecmp-primary underline-offset-2 hover:underline"
          >
            {row.parentComplaintNumber ?? row.parentComplaintId}
          </Link>
        ) : (
          <span className="text-ecmp-text-secondary">{tCommon("emDash")}</span>
        ),
    },
    {
      key: "kind",
      header: t("columnKind"),
      cell: (row) => (
        <Badge tone={row.kind === "case" ? "primary" : "neutral"}>
          {row.kind === "case" ? t("kindCase") : t("kindComplaint")}
        </Badge>
      ),
    },
    {
      key: "status",
      header: t("columnStatus"),
      cell: (row) => <Badge tone={statusTone(row.statusKey)}>{statusLabel(row)}</Badge>,
    },
    {
      key: "actions",
      header: tCommon("actions"),
      cell: (row) => (
        <Button type="button" size="sm" variant="outline" onClick={() => openRow(row)}>
          {t("open")}
        </Button>
      ),
    },
  ];

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={t("title")}
        description={t("description")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title") },
        ]}
      />

      {error ? (
        <ErrorState title={t("unableToLoad")} message={error} onRetry={() => void load()} />
      ) : null}

      <Card padding={false} className="overflow-hidden">
        <CardBody className="space-y-[var(--ecmp-panel-gap)] p-4 md:p-6">
          {loading && rows.length === 0 ? (
            <Skeleton rows={6} />
          ) : !error && rows.length === 0 ? (
            <Empty title={t("emptyTitle")} description={t("emptyDescription")} />
          ) : (
            <>
              <WorkspaceToolbar
                summary={tTable("itemsInView", { count: rows.length })}
                actions={
                  <Button type="button" size="sm" variant="outline" onClick={() => void load()}>
                    {tCommon("refresh")}
                  </Button>
                }
              />
              <Table columns={columns} rows={rows} getRowKey={(row) => row.key} stickyHeader />
            </>
          )}
        </CardBody>
      </Card>
    </PageContainer>
  );
}
