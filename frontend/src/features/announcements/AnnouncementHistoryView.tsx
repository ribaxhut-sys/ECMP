"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { fetchAnnouncementHistory } from "@/lib/api";
import type { Announcement } from "@/lib/api/types";
import { sortAnnouncements } from "@/features/landing/announcements";
import { formatDate } from "@/i18n/formatting";
import { useLocaleContext } from "@/shared/i18n";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import {
  Card,
  CardBody,
  Empty,
  ErrorState,
  Pagination,
  SectionHeader,
  Select,
  Skeleton,
  Table,
  type TableColumn,
} from "@/shared/ui";

const HISTORY_PAGE_SIZE_OPTIONS = [10, 25, 50] as const;
const DEFAULT_HISTORY_PAGE_SIZE = 10;

/**
 * Riwayat Pengumuman — read-only archive list for announcement:read holders
 * who do not also hold announcement:manage (managers see AnnouncementManagement
 * at the same /announcements route). Client-side page size defaults to 10;
 * the user can choose 10 / 25 / 50. No audience/target filtering (LOCKED).
 */
export function AnnouncementHistoryView() {
  const t = useTranslations("announcements");
  const tCommon = useTranslations("common");
  const tTable = useTranslations("table");
  const tErrors = useTranslations("errors");
  const { locale } = useLocaleContext();

  const [rows, setRows] = useState<Announcement[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(DEFAULT_HISTORY_PAGE_SIZE);

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const res = await fetchAnnouncementHistory();
      setRows(sortAnnouncements(res.data));
      setPage(1);
    } catch (err) {
      setRows([]);
      setLoadError(
        resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToLoad"),
      );
    } finally {
      setLoading(false);
    }
  }, [t, tCommon, tErrors]);

  useEffect(() => {
    void load();
  }, [load]);

  const totalItems = rows.length;
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize) || 1);

  useEffect(() => {
    setPage((current) => Math.min(current, totalPages));
  }, [totalPages]);

  const pageRows = useMemo(() => {
    const start = (page - 1) * pageSize;
    return rows.slice(start, start + pageSize);
  }, [page, pageSize, rows]);

  const pageSizeOptions = useMemo(
    () =>
      HISTORY_PAGE_SIZE_OPTIONS.map((count) => ({
        value: String(count),
        label: tTable("perPage", { count }),
      })),
    [tTable],
  );

  const columns: TableColumn<Announcement>[] = useMemo(
    () => [
      {
        key: "referenceNumber",
        header: t("columnReferenceNumber"),
        cell: (row) => (
          <span className="font-medium tabular-nums text-ecmp-text-primary">
            {row.referenceNumber}
          </span>
        ),
      },
      {
        key: "title",
        header: t("columnTitle"),
        cell: (row) => (
          <span className="font-medium text-ecmp-text-primary">{row.title}</span>
        ),
      },
      {
        key: "publishedAt",
        header: t("columnPublishedAt"),
        cell: (row) =>
          row.publishedAt
            ? formatDate(row.publishedAt, locale, {
                day: "numeric",
                month: "short",
                year: "numeric",
              })
            : tCommon("emDash"),
      },
      {
        key: "attachmentCount",
        header: t("columnAttachmentCount"),
        cell: (row) =>
          row.attachmentCount > 0 ? String(row.attachmentCount) : tCommon("emDash"),
      },
      {
        key: "actions",
        header: tCommon("actions"),
        cell: (row) => (
          <Link
            href={`/announcements/${encodeURIComponent(row.id)}`}
            className="text-[length:var(--ecmp-font-body-small-size)] font-medium text-ecmp-primary underline-offset-2 hover:underline"
          >
            {t("viewDetail")}
          </Link>
        ),
      },
    ],
    [locale, t, tCommon],
  );

  const rangeLabel =
    totalItems === 0
      ? t("historyEmpty")
      : tCommon("showingItems", {
          from: (page - 1) * pageSize + 1,
          to: Math.min(page * pageSize, totalItems),
          total: totalItems,
        });

  return (
    <section className="space-y-[var(--ecmp-panel-gap)]">
      <SectionHeader
        title={t("historyTitle")}
        description={t("historyDescription")}
      />

      {loading ? (
        <Card>
          <CardBody>
            <Skeleton rows={6} />
          </CardBody>
        </Card>
      ) : loadError ? (
        <ErrorState
          title={t("unableToLoad")}
          message={loadError}
          onRetry={() => void load()}
        />
      ) : rows.length === 0 ? (
        <Card>
          <CardBody>
            <Empty
              title={t("historyEmpty")}
              description={t("historyEmptyDescription")}
            />
          </CardBody>
        </Card>
      ) : (
        <Card>
          <CardBody className="space-y-[var(--ecmp-panel-gap)]">
            <div className="flex flex-wrap items-end justify-between gap-3">
              <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                {rangeLabel}
              </p>
              <div className="w-full max-w-[14rem] sm:w-auto">
                <Select
                  name="historyPageSize"
                  label={t("historyPageSize")}
                  options={pageSizeOptions}
                  value={String(pageSize)}
                  onChange={(e) => {
                    setPageSize(
                      Number(e.target.value) || DEFAULT_HISTORY_PAGE_SIZE,
                    );
                    setPage(1);
                  }}
                />
              </div>
            </div>
            <Table
              columns={columns}
              rows={pageRows}
              getRowKey={(row) => row.id}
              caption={t("historyTableCaption")}
              emptyMessage={t("historyEmpty")}
              density="compact"
            />
            <Pagination
              summary={tCommon("pageOf", { page, totalPages })}
              previousLabel={tCommon("previous")}
              nextLabel={tCommon("next")}
              onPrevious={() => setPage((p) => Math.max(1, p - 1))}
              onNext={() => setPage((p) => Math.min(totalPages, p + 1))}
              previousDisabled={page <= 1}
              nextDisabled={page >= totalPages}
            />
          </CardBody>
        </Card>
      )}
    </section>
  );
}
