"use client";

import { useEffect, useMemo, useState, type FormEvent } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import {
  Alert,
  Button,
  Card,
  CardBody,
  Empty,
  ErrorState,
  FilterBar,
  Input,
  PageContainer,
  PageHeader,
  Pagination,
  Select,
  Skeleton,
  Table,
  WorkspaceToolbar,
  type SelectOption,
  type TableColumn,
} from "@/shared/ui";
import { formatDate } from "@/i18n/formatting";
import { useOrgUnitCode } from "@/features/announcements/useOrgUnitCode";
import { useInternalComplaints } from "./mock/useInternalComplaints";
import {
  defaultInternalListFilters,
  filterInternalComplaints,
  hasActiveInternalFilters,
  sortByMostRecent,
  type InternalListFilters,
} from "./internalComplaintsFilters";
import {
  CATEGORY_LABEL_KEY,
  INTERNAL_CATEGORIES,
  INTERNAL_PRIORITIES,
  INTERNAL_STATUSES,
  STATUS_LABEL_KEY,
  type InternalComplaint,
} from "./types";
import {
  InternalPriorityBadge,
  InternalStatusBadge,
  InternalTransferRequestBadge,
  InternalWithdrawRequestBadge,
} from "./components/InternalBadges";

/** Client-side page window over the filtered rows. */
const LIST_PAGE_SIZE = 20;

export function InternalComplaintListView() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const t = useTranslations("internalComplaints");
  const tCommon = useTranslations("common");
  const tPriority = useTranslations("priority");
  const locale = useLocale();
  const orgUnitCode = useOrgUnitCode();
  const needsReceiveFromUrl = searchParams.get("needsReceive") === "1";
  const {
    rows: allRows,
    total,
    truncated,
    loading,
    error,
    reload,
  } = useInternalComplaints();

  const [filters, setFilters] = useState<InternalListFilters>(() => ({
    ...defaultInternalListFilters(),
    needsReceive: needsReceiveFromUrl,
  }));
  const [draft, setDraft] = useState<InternalListFilters>(filters);
  const [page, setPage] = useState(1);

  useEffect(() => {
    setFilters((current) =>
      current.needsReceive === needsReceiveFromUrl
        ? current
        : { ...current, needsReceive: needsReceiveFromUrl },
    );
    setDraft((current) =>
      current.needsReceive === needsReceiveFromUrl
        ? current
        : { ...current, needsReceive: needsReceiveFromUrl },
    );
  }, [needsReceiveFromUrl]);

  const rows = useMemo(
    () =>
      sortByMostRecent(
        filterInternalComplaints(allRows, filters, orgUnitCode),
      ),
    [allRows, filters, orgUnitCode],
  );
  // Filters are client-side (the API filters status only), so the page window
  // is applied after filtering — same shape as the attachment catalog.
  const totalPages = Math.max(1, Math.ceil(rows.length / LIST_PAGE_SIZE));
  const currentPage = Math.min(page, totalPages);
  const pageRows = useMemo(
    () =>
      rows.slice((currentPage - 1) * LIST_PAGE_SIZE, currentPage * LIST_PAGE_SIZE),
    [rows, currentPage],
  );

  function onSubmitFilters(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    setFilters(draft);
    setPage(1);
  }

  function onResetFilters(): void {
    const next = defaultInternalListFilters();
    setDraft(next);
    setFilters(next);
    setPage(1);
    if (needsReceiveFromUrl) {
      router.replace("/internal/complaints");
    }
  }

  const statusOptions: SelectOption[] = [
    { value: "", label: tCommon("all") },
    ...INTERNAL_STATUSES.map((s) => ({
      value: s,
      label: t(STATUS_LABEL_KEY[s]),
    })),
  ];
  const categoryOptions: SelectOption[] = [
    { value: "", label: tCommon("all") },
    ...INTERNAL_CATEGORIES.map((c) => ({
      value: c,
      label: t(CATEGORY_LABEL_KEY[c]),
    })),
  ];
  const priorityOptions: SelectOption[] = [
    { value: "", label: tCommon("all") },
    ...INTERNAL_PRIORITIES.map((p) => ({
      value: p,
      label: tPriority(p),
    })),
  ];

  const columns: TableColumn<InternalComplaint>[] = [
    {
      key: "number",
      header: t("number"),
      cell: (row) => (
        <button
          type="button"
          className="cursor-pointer text-left font-medium text-ecmp-primary underline-offset-2 hover:underline"
          onClick={() =>
            router.push(`/internal/complaints/${encodeURIComponent(row.id)}`)
          }
        >
          {row.number}
        </button>
      ),
    },
    {
      key: "title",
      header: t("titleField"),
      cell: (row) => row.title,
    },
    {
      key: "owner",
      header: t("ownerUnit"),
      cell: (row) => row.ownerUnitId,
    },
    {
      key: "handling",
      header: t("handlingUnit"),
      cell: (row) => row.handlingUnitId,
    },
    {
      key: "status",
      header: t("status"),
      cell: (row) => (
        <div className="flex flex-wrap gap-1">
          <InternalStatusBadge status={row.status} />
          <InternalTransferRequestBadge status={row.transferRequestStatus} />
          <InternalWithdrawRequestBadge status={row.withdrawRequestStatus} />
        </div>
      ),
    },
    {
      key: "priority",
      header: t("priority"),
      cell: (row) => <InternalPriorityBadge priority={row.priority} />,
    },
    {
      key: "created",
      header: t("createdAt"),
      cell: (row) => formatDate(row.createdAt, locale) || tCommon("emDash"),
    },
  ];

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={t("listTitle")}
        description={t("listDescription")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title"), href: "/internal" },
          { label: t("listTitle") },
        ]}
        actions={
          <Button
            type="button"
            onClick={() => router.push("/internal/complaints/new")}
          >
            {t("create")}
          </Button>
        }
      />

      {error ? <Alert tone="danger" title={error} /> : null}

      <Card>
        <CardBody className="space-y-4">
          <FilterBar
            searchPlacement="bottom"
            search={
              <Input
                label={t("search")}
                value={draft.q}
                onChange={(e) => setDraft((d) => ({ ...d, q: e.target.value }))}
                placeholder={t("searchPlaceholder")}
              />
            }
            filters={
              <>
                <Select
                  label={t("status")}
                  options={statusOptions}
                  value={draft.status}
                  onChange={(e) =>
                    setDraft((d) => ({ ...d, status: e.target.value }))
                  }
                />
                <Select
                  label={t("category")}
                  options={categoryOptions}
                  value={draft.category}
                  onChange={(e) =>
                    setDraft((d) => ({ ...d, category: e.target.value }))
                  }
                />
                <Select
                  label={t("priority")}
                  options={priorityOptions}
                  value={draft.priority}
                  onChange={(e) =>
                    setDraft((d) => ({ ...d, priority: e.target.value }))
                  }
                />
              </>
            }
            actions={
              <Button type="submit" form="internal-filters">
                {tCommon("apply")}
              </Button>
            }
            reset={
              <Button type="button" variant="ghost" onClick={onResetFilters}>
                {tCommon("reset")}
              </Button>
            }
          />
          <form id="internal-filters" onSubmit={onSubmitFilters} className="hidden" />

          {truncated ? (
            <Alert
              tone="warning"
              title={t("partialDataWarning", { loaded: allRows.length, total })}
            />
          ) : null}

          {filters.needsReceive ? (
            <Alert tone="info" title={t("inboxFilterNotice")} />
          ) : null}

          <WorkspaceToolbar
            summary={
              hasActiveInternalFilters(filters)
                ? t("filteredCount", { count: rows.length })
                : t("totalCount", { count: rows.length })
            }
          />

          {loading ? (
            <Skeleton rows={6} />
          ) : error ? (
            <ErrorState message={error} onRetry={reload} />
          ) : rows.length === 0 ? (
            <Empty
              title={t("listEmpty")}
              description={t("listEmptyDescription")}
            />
          ) : (
            <>
              <Table
                columns={columns}
                rows={pageRows}
                getRowKey={(row) => row.id}
              />
              <Pagination
                summary={tCommon("pageOf", { page: currentPage, totalPages })}
                previousLabel={tCommon("previous")}
                nextLabel={tCommon("next")}
                onPrevious={() => setPage((p) => Math.max(1, p - 1))}
                onNext={() => setPage((p) => Math.min(totalPages, p + 1))}
                previousDisabled={currentPage <= 1}
                nextDisabled={currentPage >= totalPages}
              />
            </>
          )}
        </CardBody>
      </Card>
    </PageContainer>
  );
}
