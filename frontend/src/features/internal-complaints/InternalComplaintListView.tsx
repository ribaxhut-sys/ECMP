"use client";

import { useMemo, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import {
  Alert,
  Button,
  Card,
  CardBody,
  Empty,
  FilterBar,
  Input,
  PageContainer,
  PageHeader,
  Select,
  Table,
  WorkspaceToolbar,
  type SelectOption,
  type TableColumn,
} from "@/shared/ui";
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
} from "./components/InternalBadges";

function formatDate(value: string | null): string {
  if (!value) return "—";
  try {
    return new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(
      new Date(value),
    );
  } catch {
    return value;
  }
}

export function InternalComplaintListView() {
  const router = useRouter();
  const t = useTranslations("internalComplaints");
  const tCommon = useTranslations("common");
  const tPriority = useTranslations("priority");
  const { rows: allRows, loading, error } = useInternalComplaints();

  const [filters, setFilters] = useState<InternalListFilters>(
    defaultInternalListFilters(),
  );
  const [draft, setDraft] = useState<InternalListFilters>(filters);

  const rows = useMemo(
    () => sortByMostRecent(filterInternalComplaints(allRows, filters)),
    [allRows, filters],
  );

  function onSubmitFilters(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    setFilters(draft);
  }

  function onResetFilters(): void {
    const next = defaultInternalListFilters();
    setDraft(next);
    setFilters(next);
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
          className="text-left font-medium text-ecmp-primary underline-offset-2 hover:underline"
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
      cell: (row) => <InternalStatusBadge status={row.status} />,
    },
    {
      key: "priority",
      header: t("priority"),
      cell: (row) => <InternalPriorityBadge priority={row.priority} />,
    },
    {
      key: "created",
      header: t("createdAt"),
      cell: (row) => formatDate(row.createdAt),
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
            search={
              <Input
                label={t("search")}
                value={draft.q}
                onChange={(e) => setDraft((d) => ({ ...d, q: e.target.value }))}
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

          <WorkspaceToolbar
            summary={
              hasActiveInternalFilters(filters)
                ? t("filteredCount", { count: rows.length })
                : t("totalCount", { count: rows.length })
            }
          />

          {loading ? (
            <Empty title={tCommon("loading")} description="" />
          ) : rows.length === 0 ? (
            <Empty
              title={t("listEmpty")}
              description={t("listEmptyDescription")}
            />
          ) : (
            <Table
              columns={columns}
              rows={rows}
              getRowKey={(row) => row.id}
            />
          )}
        </CardBody>
      </Card>
    </PageContainer>
  );
}
