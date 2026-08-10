"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import {
  deleteAnnouncementAttachmentFromCatalog,
  downloadAttachment,
  fetchAnnouncementAttachmentLibrary,
  updateAnnouncementAttachmentAccess,
  uploadAnnouncementAttachmentToCatalog,
} from "@/lib/api";
import type { AnnouncementAttachmentLibraryItem, Attachment } from "@/lib/api/types";
import { fileTypeLabel, formatFileSize } from "@/features/attachments/fileTypes";
import { AttachmentViewer } from "@/features/attachments/AttachmentViewer";
import {
  Alert,
  Button,
  Empty,
  ErrorState,
  Input,
  PageContainer,
  PageHeader,
  Pagination,
  Select,
  Skeleton,
  Table,
  type TableColumn,
} from "@/shared/ui";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { IconClose, IconDownload, IconEye } from "@/shared/icons";
import { useToast } from "@/shared/providers";

/** Keep accept simple — complex MIME lists break the picker on some OS/browsers. */
const CATALOG_ACCEPT = ".pdf,.png,.jpg,.jpeg,.gif,.webp,.txt,.doc,.docx,.xls,.xlsx";
const PAGE_SIZE_OPTIONS = [10, 25, 50] as const;
const DEFAULT_PAGE_SIZE = 10;
type CatalogOrgScope = "all" | "pusat" | "cabang";
const ORG_SCOPE_OPTIONS: readonly CatalogOrgScope[] = ["all", "pusat", "cabang"];

function toViewerAttachment(item: AnnouncementAttachmentLibraryItem): Attachment {
  const ext = item.fileName.includes(".")
    ? item.fileName.slice(item.fileName.lastIndexOf(".") + 1)
    : null;
  return {
    id: item.id,
    aggregateType: "Announcement",
    aggregateId: item.id,
    fileName: item.fileName,
    originalName: item.fileName,
    mimeType: item.mimeType,
    extension: ext,
    sizeBytes: item.sizeBytes,
    checksumSha256: "",
    storageProvider: "local",
    uploadedBy: item.uploadedBy,
    uploadedAt: item.createdAt,
    status: "AVAILABLE",
  };
}

/**
 * Sidebar Lampiran — katalog file domain Pengumuman (PUBLIC/PRIVATE).
 * Compact table + client-side pagination (same pattern as announcement history).
 */
export function AttachmentsWorkspace() {
  const t = useTranslations("attachments");
  const tCommon = useTranslations("common");
  const tTable = useTranslations("table");
  const tErrors = useTranslations("errors");
  const { pushSuccess } = useToast();

  const [q, setQ] = useState("");
  const [search, setSearch] = useState("");
  const [orgScope, setOrgScope] = useState<CatalogOrgScope>("all");
  const [items, setItems] = useState<AnnouncementAttachmentLibraryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE);
  const [preview, setPreview] = useState<AnnouncementAttachmentLibraryItem | null>(
    null,
  );

  const load = useCallback(
    async (query?: string, scope?: CatalogOrgScope) => {
      const effective = query !== undefined ? query : search;
      const effectiveScope = scope ?? orgScope;
      setLoading(true);
      setError(null);
      try {
        const res = await fetchAnnouncementAttachmentLibrary({
          q: effective.trim() || undefined,
          orgScope: effectiveScope,
        });
        setItems(res.data);
        setPage(1);
      } catch (err) {
        setItems([]);
        setError(
          resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToLoad"),
        );
      } finally {
        setLoading(false);
      }
    },
    [orgScope, search, t, tCommon, tErrors],
  );

  useEffect(() => {
    void load();
  }, [load]);

  const totalItems = items.length;
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize) || 1);

  useEffect(() => {
    setPage((current) => Math.min(current, totalPages));
  }, [totalPages]);

  const pageRows = useMemo(() => {
    const start = (page - 1) * pageSize;
    return items.slice(start, start + pageSize);
  }, [items, page, pageSize]);

  const pageSizeOptions = useMemo(
    () =>
      PAGE_SIZE_OPTIONS.map((count) => ({
        value: String(count),
        label: tTable("perPage", { count }),
      })),
    [tTable],
  );

  const orgScopeOptions = useMemo(
    () =>
      ORG_SCOPE_OPTIONS.map((value) => ({
        value,
        label:
          value === "all"
            ? t("filterOrgAll")
            : value === "pusat"
              ? t("filterOrgPusat")
              : t("filterOrgCabang"),
      })),
    [t],
  );

  async function uploadFiles(files: File[]) {
    if (files.length === 0) return;

    setUploading(true);
    setActionError(null);
    setUploadProgress(t("uploadProgress", { current: 0, total: files.length }));
    const failures: string[] = [];
    let uploaded = 0;

    try {
      for (let i = 0; i < files.length; i += 1) {
        const file = files[i];
        setUploadProgress(
          t("uploadProgress", { current: i + 1, total: files.length }),
        );
        try {
          await uploadAnnouncementAttachmentToCatalog(file, "PRIVATE");
          uploaded += 1;
        } catch (err) {
          failures.push(
            `${file.name}: ${
              resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToUpload")
            }`,
          );
        }
      }
      if (uploaded > 0) {
        pushSuccess(tCommon("success"), t("uploadedToCatalog", { count: uploaded }));
        setQ("");
        setSearch("");
        await load("");
      }
      if (failures.length > 0) {
        setActionError(
          failures.length === files.length
            ? failures.join(" ")
            : t("partialUploadFailed", { detail: failures.join(" ") }),
        );
      }
    } finally {
      setUploading(false);
      setUploadProgress(null);
    }
  }

  function onFileInputChange(event: React.ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files ?? []);
    event.target.value = "";
    if (files.length === 0) return;
    void uploadFiles(files);
  }

  function onDrop(event: React.DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setDragOver(false);
    if (uploading) return;
    const files = Array.from(event.dataTransfer.files || []);
    void uploadFiles(files);
  }

  async function setAccess(
    item: AnnouncementAttachmentLibraryItem,
    accessLevel: "PUBLIC" | "PRIVATE",
  ) {
    setBusyId(item.id);
    setActionError(null);
    try {
      await updateAnnouncementAttachmentAccess(item.id, { accessLevel });
      pushSuccess(tCommon("success"), t("accessUpdated"));
      await load();
    } catch (err) {
      setActionError(
        resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToUpdateAccess"),
      );
    } finally {
      setBusyId(null);
    }
  }

  async function onDelete(item: AnnouncementAttachmentLibraryItem) {
    setBusyId(item.id);
    setActionError(null);
    try {
      await deleteAnnouncementAttachmentFromCatalog(item.id);
      pushSuccess(tCommon("success"), t("deletedFromCatalog"));
      await load();
    } catch (err) {
      setActionError(
        resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToDelete"),
      );
    } finally {
      setBusyId(null);
    }
  }

  async function onDownload(item: AnnouncementAttachmentLibraryItem) {
    setBusyId(item.id);
    setActionError(null);
    try {
      const result = await downloadAttachment(item.id);
      const url = URL.createObjectURL(result.blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = result.filename || item.fileName;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setActionError(
        resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToDownload"),
      );
    } finally {
      setBusyId(null);
    }
  }

  const columns: TableColumn<AnnouncementAttachmentLibraryItem>[] = [
    {
      key: "fileName",
      header: t("fileName"),
      cell: (row) => (
        <div className="min-w-0 max-w-[22rem]">
          <p className="truncate font-medium text-ecmp-text-primary">{row.fileName}</p>
          <p className="truncate text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
            {t("catalogUnitUser", {
              unit: row.uploadedOrgUnitId || tCommon("emDash"),
              user: row.uploadedByName || tCommon("emDash"),
            })}
            {row.usageCount > 0 ? ` · ${t("linkedShort", { count: row.usageCount })}` : ""}
          </p>
        </div>
      ),
    },
    {
      key: "type",
      header: t("fileType"),
      hideOnMobile: true,
      cell: (row) => (
        <span className="whitespace-nowrap">
          {fileTypeLabel(row.mimeType, null, row.fileName)}
        </span>
      ),
    },
    {
      key: "size",
      header: t("fileSize"),
      hideOnMobile: true,
      cell: (row) => (
        <span className="whitespace-nowrap tabular-nums">
          {formatFileSize(row.sizeBytes)}
        </span>
      ),
    },
    {
      key: "access",
      header: t("columnAccess"),
      cell: (row) => {
        const busy = busyId === row.id;
        const isPublic = row.accessLevel === "PUBLIC";
        return (
          <Button
            type="button"
            size="sm"
            variant="ghost"
            disabled={busy || uploading}
            aria-label={isPublic ? t("setPrivate") : t("setPublic")}
            title={isPublic ? t("setPrivate") : t("setPublic")}
            className="!min-h-7 !px-2 whitespace-nowrap"
            onClick={() => void setAccess(row, isPublic ? "PRIVATE" : "PUBLIC")}
          >
            {isPublic ? t("accessPublic") : t("accessPrivate")}
          </Button>
        );
      },
    },
    {
      key: "actions",
      header: tCommon("actions"),
      slot: "action",
      cell: (row) => {
        const busy = busyId === row.id;
        return (
          <div className="flex flex-nowrap items-center justify-end gap-0.5">
            <Button
              type="button"
              size="sm"
              variant="ghost"
              disabled={busy || uploading}
              aria-label={t("preview")}
              title={t("preview")}
              className="!min-h-8 !min-w-8 !px-0"
              onClick={() => setPreview(row)}
            >
              <IconEye className="size-4" />
            </Button>
            <Button
              type="button"
              size="sm"
              variant="ghost"
              disabled={busy || uploading}
              loading={busy}
              aria-label={t("download")}
              title={t("download")}
              className="!min-h-8 !min-w-8 !px-0"
              onClick={() => void onDownload(row)}
            >
              <IconDownload className="size-4" />
            </Button>
            <Button
              type="button"
              size="sm"
              variant="ghost"
              disabled={busy || uploading || row.usageCount > 0}
              aria-label={tCommon("delete")}
              title={
                row.usageCount > 0
                  ? t("deleteBlockedWhileLinked")
                  : tCommon("delete")
              }
              className="!min-h-8 !min-w-8 !px-0 text-ecmp-danger"
              onClick={() => void onDelete(row)}
            >
              <IconClose className="size-4" />
            </Button>
          </div>
        );
      },
    },
  ];

  const rangeLabel =
    totalItems === 0
      ? t("noItems")
      : tCommon("showingItems", {
          from: (page - 1) * pageSize + 1,
          to: Math.min(page * pageSize, totalItems),
          total: totalItems,
        });

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={t("title")}
        breadcrumbs={[
          { label: t("home"), href: "/dashboard" },
          { label: t("title") },
        ]}
        description={t("catalogDescription")}
        meta={
          <span className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
            {t("catalogCount", { count: items.length })}
          </span>
        }
      />

      <div
        className={
          dragOver
            ? "rounded-[var(--ecmp-radius-md)] border-2 border-dashed border-ecmp-primary bg-ecmp-hover p-3"
            : "rounded-[var(--ecmp-radius-md)] border border-dashed border-ecmp-border bg-ecmp-surface p-3"
        }
        onDragEnter={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={(e) => {
          e.preventDefault();
          setDragOver(false);
        }}
        onDrop={onDrop}
      >
        <label className="flex flex-col gap-1.5">
          <span className="text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary">
            {t("upload")}
          </span>
          <input
            type="file"
            multiple
            accept={CATALOG_ACCEPT}
            disabled={uploading}
            aria-label={t("uploadAriaLabel")}
            className="block w-full cursor-pointer text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-primary file:mr-3 file:cursor-pointer file:rounded-[var(--ecmp-radius-md)] file:border-0 file:bg-ecmp-primary file:px-3 file:py-2 file:text-ecmp-primary-foreground"
            onChange={onFileInputChange}
          />
          <span className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
            {t("uploadHint")}
          </span>
        </label>
      </div>

      <form
        className="flex flex-wrap gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          setSearch(q);
          setPage(1);
        }}
      >
        <div className="min-w-[16rem] flex-1">
          <Input
            label={t("searchLabel")}
            placeholder={t("searchPlaceholder")}
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>
        <div className="w-full max-w-[12rem] sm:w-auto">
          <Select
            name="catalogOrgScope"
            label={t("filterOrgLabel")}
            options={orgScopeOptions}
            value={orgScope}
            onChange={(e) => {
              const next = e.target.value as CatalogOrgScope;
              setOrgScope(
                ORG_SCOPE_OPTIONS.includes(next) ? next : "all",
              );
            }}
          />
        </div>
        <div className="flex items-end gap-2">
          <Button type="submit">{tCommon("search")}</Button>
          <Button
            type="button"
            variant="secondary"
            disabled={loading || uploading}
            onClick={() => void load()}
          >
            {tCommon("refresh")}
          </Button>
        </div>
      </form>

      {uploadProgress ? (
        <Alert tone="info" title={t("uploading")} description={uploadProgress} />
      ) : null}

      {actionError ? (
        <Alert tone="danger" title={t("actionFailed")} description={actionError} />
      ) : null}

      {loading ? (
        <Skeleton rows={6} />
      ) : error ? (
        <ErrorState
          title={t("unableToLoad")}
          message={error}
          onRetry={() => void load()}
        />
      ) : items.length === 0 ? (
        <Empty title={t("noItems")} description={t("catalogEmptyDescription")} />
      ) : (
        <div className="space-y-[var(--ecmp-panel-gap)]">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
              {rangeLabel}
            </p>
            <div className="w-full max-w-[14rem] sm:w-auto">
              <Select
                name="catalogPageSize"
                label={t("pageSizeLabel")}
                options={pageSizeOptions}
                value={String(pageSize)}
                onChange={(e) => {
                  setPageSize(Number(e.target.value) || DEFAULT_PAGE_SIZE);
                  setPage(1);
                }}
              />
            </div>
          </div>
          <Table
            columns={columns}
            rows={pageRows}
            getRowKey={(row) => row.id}
            caption={t("catalogTableCaption")}
            emptyMessage={t("noItems")}
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
        </div>
      )}

      {preview ? (
        <AttachmentViewer
          open
          onClose={() => setPreview(null)}
          attachment={toViewerAttachment(preview)}
        />
      ) : null}
    </PageContainer>
  );
}
