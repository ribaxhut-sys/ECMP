"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { useOrgUnitCode } from "@/features/announcements/useOrgUnitCode";
import { ApiError, fetchCmBatch1Complaints, fetchCmCases } from "@/lib/api";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { formatHqArrivalSlot } from "@/shared/utils/datetime";
import {
  Badge,
  Button,
  Card,
  CardBody,
  Empty,
  ErrorState,
  Input,
  PageContainer,
  PageHeader,
  Skeleton,
  Table,
  WorkspaceToolbar,
  type BadgeTone,
  type TableColumn,
} from "@/shared/ui";
import { isPusatWorkAudience } from "./cmBatch1ComplaintListIdentity";
import {
  buildFollowUpRows,
  filterFollowUpRows,
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
    case "hqAwaitingAccept":
      return "info";
    case "hqAcceptedUnscheduled":
      return "info";
    case "hqScheduled":
      return "info";
    case "returnedToBranch":
      return "warning";
    case "caseWorking":
      return "primary";
    case "caseNew":
      return "neutral";
    default:
      return "neutral";
  }
}

/**
 * Tindak lanjut — Case-only work list. Presentation composition over
 * API-514 / API-536; no new API surface. See followUpRows.ts.
 */
export function FollowUpListView() {
  const router = useRouter();
  const t = useTranslations("followUp");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const tComplaints = useTranslations("complaints");
  const locale = useLocale();
  const { hasPermission } = useAuth();
  const canRead = hasPermission("complaints:read");
  const orgUnitCode = useOrgUnitCode();
  const pusatAudience = isPusatWorkAudience(orgUnitCode);

  const [rows, setRows] = useState<FollowUpRow[]>([]);
  const [query, setQuery] = useState("");
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
      const [complaintsRes, casesRes] = await Promise.all([
        fetchCmBatch1Complaints({ page: 1, pageSize: FOLLOW_UP_FETCH_PAGE_SIZE }),
        fetchCmCases({ page: 1, pageSize: FOLLOW_UP_FETCH_PAGE_SIZE }),
      ]);
      setRows(
        buildFollowUpRows({
          complaints: complaintsRes.data ?? [],
          allCases: casesRes.data ?? [],
          audience: pusatAudience ? "pusat" : "cabang",
        }),
      );
    } catch (err) {
      setRows([]);
      setError(
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : t("unableToLoad"),
      );
    } finally {
      setLoading(false);
    }
  }, [canRead, pusatAudience, t, tErrors, tCommon]);

  useEffect(() => {
    void load();
  }, [load]);

  const statusLabel = useCallback(
    (row: FollowUpRow): string => {
      switch (row.statusKey) {
        case "awaitingApproval":
          return t("statusAwaitingApproval");
        case "hqAwaitingAccept":
          return t("statusHqAwaitingAccept");
        case "hqAcceptedUnscheduled":
          return t("statusHqAcceptedUnscheduled");
        case "hqScheduled":
          return t("statusHqScheduled");
        case "returnedToBranch":
          return t("statusReturnedToBranch");
        case "caseWorking":
          return t("statusCaseWorking");
        case "caseNew":
          return t("statusCaseNew");
        default:
          return row.statusKey;
      }
    },
    [t],
  );

  const visibleRows = useMemo(
    () => filterFollowUpRows(rows, query, statusLabel),
    [rows, query, statusLabel],
  );

  function scheduleLabel(row: FollowUpRow): string {
    if (!row.hqArrivalDate?.trim() || !row.hqArrivalTime?.trim()) {
      return tCommon("emDash");
    }
    const parts = formatHqArrivalSlot(row.hqArrivalDate, row.hqArrivalTime, locale);
    return parts ? tComplaints("hqArrivalSlotLabel", parts) : tCommon("emDash");
  }

  function openRow(row: FollowUpRow): void {
    router.push(followUpRowHref(row));
  }

  function followUpNumberClass(unread: boolean): string {
    return unread
      ? "cursor-pointer font-semibold text-ecmp-primary underline-offset-2 hover:underline"
      : "cursor-pointer font-medium text-ecmp-primary underline-offset-2 hover:underline";
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
      headerClassName: "whitespace-nowrap",
      className: "whitespace-nowrap",
      cell: (row) => (
        <Link
          href={followUpRowHref(row)}
          className={followUpNumberClass(row.isUnread)}
        >
          {row.number}
        </Link>
      ),
    },
    {
      key: "subject",
      header: t("columnSubject"),
      className: "max-w-[16rem]",
      cell: (row) => (
        <span className="block truncate">
          {row.subject?.trim() || tCommon("emDash")}
        </span>
      ),
    },
    {
      key: "status",
      header: t("columnStatus"),
      headerClassName: "whitespace-nowrap",
      className: "whitespace-nowrap",
      cell: (row) => <Badge tone={statusTone(row.statusKey)}>{statusLabel(row)}</Badge>,
    },
    {
      key: "schedule",
      header: t("columnSchedule"),
      headerClassName: "whitespace-nowrap",
      cell: (row) => (
        <span className={row.statusKey === "hqScheduled" ? "text-ecmp-text-primary" : "text-ecmp-text-secondary"}>
          {scheduleLabel(row)}
        </span>
      ),
    },
    {
      key: "handler",
      header: t("columnHandler"),
      cell: (row) => row.handlerName || tCommon("emDash"),
    },
    {
      key: "actions",
      header: tCommon("actions"),
      headerClassName: "whitespace-nowrap",
      className: "whitespace-nowrap",
      cell: (row) => (
        <Button
          type="button"
          size="sm"
          variant="outline"
          className="!h-7 !min-h-7 px-2.5 text-[length:var(--ecmp-font-caption-size)]"
          onClick={() => openRow(row)}
        >
          {t("open")}
        </Button>
      ),
    },
  ];

  const hasQuery = query.trim().length > 0;

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={t("title")}
        description={pusatAudience === true ? t("descriptionPusat") : t("description")}
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
            <Empty
              title={t("emptyTitle")}
              description={
                pusatAudience === true
                  ? t("emptyDescriptionPusat")
                  : t("emptyDescription")
              }
            />
          ) : (
            <>
              <WorkspaceToolbar
                search={
                  <Input
                    name="followUpSearch"
                    type="search"
                    value={query}
                    onChange={(event) => setQuery(event.target.value)}
                    placeholder={t("searchPlaceholder")}
                    aria-label={t("searchAriaLabel")}
                  />
                }
                summary={tCommon("showingItems", {
                  from: visibleRows.length === 0 ? 0 : 1,
                  to: visibleRows.length,
                  total: rows.length,
                })}
                actions={
                  <>
                    {hasQuery ? (
                      <Button
                        type="button"
                        size="sm"
                        variant="ghost"
                        onClick={() => setQuery("")}
                      >
                        {tCommon("reset")}
                      </Button>
                    ) : null}
                    <Button type="button" size="sm" variant="outline" onClick={() => void load()}>
                      {tCommon("refresh")}
                    </Button>
                  </>
                }
              />
              {visibleRows.length === 0 ? (
                <Empty
                  title={t("emptyFilterTitle")}
                  description={t("emptyFilterDescription")}
                  primaryAction={{
                    label: tCommon("reset"),
                    onClick: () => setQuery(""),
                  }}
                />
              ) : (
                <Table
                  columns={columns}
                  rows={visibleRows}
                  getRowKey={(row) => row.key}
                  density="compact"
                  stickyHeader
                  className="leading-tight [--ecmp-font-table-size:0.9375rem] [--ecmp-density-compact-cell-y:4px]"
                  getRowClassName={(row) =>
                    row.isUnread ? "font-semibold" : undefined
                  }
                />
              )}
            </>
          )}
        </CardBody>
      </Card>
    </PageContainer>
  );
}
