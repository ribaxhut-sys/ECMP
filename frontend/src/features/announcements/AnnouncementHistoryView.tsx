"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { fetchAnnouncementHistory } from "@/lib/api";
import type { Announcement } from "@/lib/api/types";
import { sortAnnouncements } from "@/features/landing/announcements";
import { summarize } from "@/features/landing/announcementSummary";
import { formatDateTime } from "@/i18n/formatting";
import { useLocaleContext } from "@/shared/i18n";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { cn } from "@/shared/utils";
import {
  Card,
  CardBody,
  Checkbox,
  Empty,
  ErrorState,
  Pagination,
  SectionHeader,
  Select,
  Skeleton,
  Table,
  type TableColumn,
} from "@/shared/ui";

function isUnread(row: Announcement): boolean {
  return row.isRead !== true;
}

const HISTORY_PAGE_SIZE_OPTIONS = [10, 25, 50] as const;
const DEFAULT_HISTORY_PAGE_SIZE = 10;
const HISTORY_BODY_PREVIEW_MAX = 120;

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
  const [unreadOnly, setUnreadOnly] = useState(false);

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

  const visibleRows = useMemo(
    () => (unreadOnly ? rows.filter(isUnread) : rows),
    [rows, unreadOnly],
  );
  const totalItems = visibleRows.length;
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize) || 1);

  useEffect(() => {
    setPage((current) => Math.min(current, totalPages));
  }, [totalPages]);

  const pageRows = useMemo(() => {
    const start = (page - 1) * pageSize;
    return visibleRows.slice(start, start + pageSize);
  }, [page, pageSize, visibleRows]);

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
          <Link
            href={`/announcements/${encodeURIComponent(row.id)}`}
            className={cn(
              "tabular-nums underline-offset-2 hover:underline",
              isUnread(row)
                ? "font-semibold text-ecmp-primary"
                : "font-normal text-ecmp-primary",
            )}
          >
            {row.referenceNumber}
          </Link>
        ),
      },
      {
        key: "title",
        header: t("columnTitle"),
        cell: (row) => (
          <span
            className={cn(
              isUnread(row)
                ? "font-semibold text-ecmp-text-primary"
                : "font-normal text-ecmp-text-secondary",
            )}
          >
            {row.title}
          </span>
        ),
      },
      {
        key: "body",
        header: t("columnBody"),
        cell: (row) => {
          const preview = summarize(row.body, HISTORY_BODY_PREVIEW_MAX);
          if (!preview) return tCommon("emDash");
          return (
            <span
              className="line-clamp-2 text-[length:var(--ecmp-font-body-small-size)] font-normal text-ecmp-text-secondary"
              title={row.body.trim()}
            >
              {preview}
            </span>
          );
        },
      },
      {
        key: "publishedAt",
        header: t("columnPublishedAt"),
        cell: (row) =>
          row.publishedAt
            ? formatDateTime(row.publishedAt, locale, {
                day: "numeric",
                month: "long",
                year: "numeric",
              })
            : tCommon("emDash"),
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
              <Checkbox
                name="historyUnreadOnly"
                label={t("historyUnreadOnly")}
                checked={unreadOnly}
                onChange={(e) => {
                  setUnreadOnly(e.target.checked);
                  setPage(1);
                }}
              />
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
            {unreadOnly && totalItems === 0 ? (
              <Empty
                title={t("historyUnreadEmpty")}
                description={t("historyUnreadEmptyDescription")}
              />
            ) : (
              <>
                <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                  {rangeLabel}
                </p>
                <Table
                  columns={columns}
                  rows={pageRows}
                  getRowKey={(row) => row.id}
                  getRowClassName={(row) =>
                    isUnread(row) ? "bg-ecmp-primary-muted/40" : undefined
                  }
                  caption={t("historyTableCaption")}
                  emptyMessage={t("historyEmpty")}
                  density="compact"
                />
              </>
            )}
            {totalItems > 0 ? (
              <Pagination
                summary={tCommon("pageOf", { page, totalPages })}
                previousLabel={tCommon("previous")}
                nextLabel={tCommon("next")}
                onPrevious={() => setPage((p) => Math.max(1, p - 1))}
                onNext={() => setPage((p) => Math.min(totalPages, p + 1))}
                previousDisabled={page <= 1}
                nextDisabled={page >= totalPages}
              />
            ) : null}
          </CardBody>
        </Card>
      )}
    </section>
  );
}
