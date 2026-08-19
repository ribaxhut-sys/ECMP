"use client";

import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { createKnowledge, searchKnowledge, uploadKnowledgeFile } from "@/lib/api";
import type { Knowledge, KnowledgeStatus, KnowledgeType } from "@/lib/api/types";
import { formatDate } from "@/i18n/formatting";
import {
  Alert,
  Button,
  Empty,
  ErrorState,
  Input,
  Modal,
  PageContainer,
  PageHeader,
  Pagination,
  Select,
  Skeleton,
} from "@/shared/ui";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { useToast } from "@/shared/providers";
import { knowledgeTypeKey, KnowledgeTypeBadge } from "./KnowledgeBadges";
import { KnowledgeCreateFileStaging, type StagedKnowledgeFile } from "./KnowledgeCreateFileStaging";
import { KnowledgeFileTypeIcon } from "./KnowledgeFileTypeIcon";
import { KnowledgeFormFields } from "./KnowledgeFormFields";
import { mayManageKnowledge } from "./knowledgeManageGate";
import {
  buildKnowledgeListMeta,
  isKnowledgeListInactive,
  knowledgeStatusDotClass,
  knowledgeStatusLabelKey,
  pickKnowledgeDisplayFile,
  sortKnowledgeByUploadedAtDesc,
} from "./knowledgeListMeta";
import { useOrgUnitCode } from "@/features/announcements/useOrgUnitCode";
import {
  createEmptyKnowledgeForm,
  toKnowledgeCreateRequest,
  validateKnowledgeForm,
  type KnowledgeFieldErrors,
  type KnowledgeFormValues,
} from "./knowledgeForm";

const KNOWLEDGE_TYPE_VALUES: readonly KnowledgeType[] = [
  "SOP",
  "PERATURAN",
  "SURAT_EDARAN",
  "KEPUTUSAN",
  "PANDUAN",
];

/** Client-side paging over the fetched catalog — same pattern as the
 * announcement management list and the attachment catalog. */
const PAGE_SIZE_OPTIONS = [10, 25, 50] as const;
const DEFAULT_PAGE_SIZE = 10;

/**
 * Single shared list — search/filter for every knowledge:read holder;
 * "+ Tambah" and DRAFT status filter appear only for knowledge:manage
 * (Pusat-proven, mirrors announcement manage gate).
 */
export function KnowledgeListView() {
  const router = useRouter();
  const locale = useLocale();
  const t = useTranslations("knowledge");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const tTable = useTranslations("table");
  const tAttachments = useTranslations("attachments");
  const { push: pushToast } = useToast();
  const { hasPermission, roles } = useAuth();
  const orgUnitCode = useOrgUnitCode();
  const canManage =
    orgUnitCode !== undefined &&
    mayManageKnowledge({ roles, hasPermission, orgUnitCode });

  const [q, setQ] = useState("");
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState<KnowledgeType | "">("");
  const [statusFilter, setStatusFilter] = useState<KnowledgeStatus>("ACTIVE");
  const [rows, setRows] = useState<Knowledge[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState<number>(DEFAULT_PAGE_SIZE);

  const [showCreate, setShowCreate] = useState(false);
  const [createValues, setCreateValues] = useState<KnowledgeFormValues>(
    createEmptyKnowledgeForm,
  );
  const [createErrors, setCreateErrors] = useState<KnowledgeFieldErrors>({});
  const [createError, setCreateError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [stagedFiles, setStagedFiles] = useState<StagedKnowledgeFile[]>([]);

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const res = await searchKnowledge({
        q: search || undefined,
        type: typeFilter || undefined,
        status: statusFilter,
      });
      setRows(sortKnowledgeByUploadedAtDesc(res.data));
      // A new result set always starts at page 1 — otherwise a narrower
      // filter can leave the view stranded on a page that no longer exists.
      setPage(1);
    } catch (err) {
      setRows([]);
      setLoadError(resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToLoad"));
    } finally {
      setLoading(false);
    }
  }, [search, typeFilter, statusFilter, t, tCommon, tErrors]);

  useEffect(() => {
    void load();
  }, [load]);

  const totalItems = rows.length;
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize) || 1);

  useEffect(() => {
    setPage((current) => Math.min(current, totalPages));
  }, [totalPages]);

  const pageRows = useMemo(
    () => rows.slice((page - 1) * pageSize, (page - 1) * pageSize + pageSize),
    [rows, page, pageSize],
  );

  const pageSizeOptions = useMemo(
    () =>
      PAGE_SIZE_OPTIONS.map((count) => ({
        value: String(count),
        label: tTable("perPage", { count }),
      })),
    [tTable],
  );

  const statusOptions = useMemo(() => {
    const base: { value: KnowledgeStatus; label: string }[] = [
      { value: "ACTIVE", label: t("statusActive") },
      { value: "ARCHIVED", label: t("statusArchived") },
    ];
    if (canManage) {
      base.push({ value: "DRAFT", label: t("statusDraft") });
    }
    return base;
  }, [canManage, t]);

  const typeOptions = useMemo(
    () => [
      { value: "", label: t("filterTypeAll") },
      ...KNOWLEDGE_TYPE_VALUES.map((value) => ({ value, label: t(knowledgeTypeKey(value)) })),
    ],
    [t],
  );

  function resetCreateForm() {
    setCreateValues(createEmptyKnowledgeForm());
    setCreateErrors({});
    setCreateError(null);
    setStagedFiles([]);
  }

  async function submitCreate(event: FormEvent) {
    event.preventDefault();
    const errors = validateKnowledgeForm(createValues);
    setCreateErrors(errors);
    if (Object.keys(errors).length > 0) return;

    setCreating(true);
    setCreateError(null);
    try {
      const res = await createKnowledge(toKnowledgeCreateRequest(createValues));
      const created = res.data;

      // Knowledge has no staging endpoint (unlike complaint attachments) —
      // files are picked before create exists, then uploaded one by one
      // right after, DRAFT-only, via the same endpoint the detail page uses.
      const failedFileNames: string[] = [];
      for (let i = 0; i < stagedFiles.length; i++) {
        const staged = stagedFiles[i];
        try {
          await uploadKnowledgeFile(
            created.id,
            staged.file,
            i === 0 ? "PRIMARY" : "SUPPORTING",
          );
        } catch {
          failedFileNames.push(staged.file.name);
        }
      }

      setShowCreate(false);
      resetCreateForm();
      if (failedFileNames.length > 0) {
        pushToast({
          title: tAttachments("partialUploadFailed", { detail: failedFileNames.join(", ") }),
          tone: "warning",
        });
      }
      router.push(`/knowledge/${created.id}`);
    } catch (err) {
      setCreateError(resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToSave"));
    } finally {
      setCreating(false);
    }
  }

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={t("title")}
        description={t("description")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title") },
        ]}
        actions={
          canManage ? (
            <Button type="button" onClick={() => setShowCreate(true)}>
              {t("addKnowledge")}
            </Button>
          ) : undefined
        }
      />

      <form
        className="flex flex-wrap items-end gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          setSearch(q);
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
        <div className="w-full max-w-[14rem] sm:w-auto">
          <Select
            name="knowledgeTypeFilter"
            label={t("filterTypeLabel")}
            options={typeOptions}
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value as KnowledgeType | "")}
          />
        </div>
        <div className="w-full max-w-[12rem] sm:w-auto">
          <Select
            name="knowledgeStatusFilter"
            label={t("filterStatusLabel")}
            options={statusOptions}
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as KnowledgeStatus)}
          />
        </div>
        <Button type="submit" variant="secondary">
          {tCommon("search")}
        </Button>
      </form>

      {loading ? (
        <Skeleton rows={6} />
      ) : loadError ? (
        <ErrorState title={t("unableToLoad")} message={loadError} onRetry={() => void load()} />
      ) : rows.length === 0 ? (
        <Empty title={t("listEmpty")} description={t("listEmptyDescription")} />
      ) : (
        <div className="space-y-[var(--ecmp-panel-gap)]">
          <ul
            className="divide-y divide-ecmp-border overflow-hidden rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface"
            aria-label={t("tableCaption")}
            data-testid="knowledge-list"
          >
            {pageRows.map((row) => {
              const meta = buildKnowledgeListMeta(
                row,
                {
                  status: t(knowledgeStatusLabelKey(row.status)),
                  effective: (date) => t("listMetaEffective", { date }),
                  uploaded: (date) => t("listMetaUploaded", { date }),
                  inactive: (date) => t("listMetaInactive", { date }),
                  files: (count) => t("listMetaFiles", { count }),
                  emDash: tCommon("emDash"),
                },
                (value) => formatDate(value, locale),
              );
              const muted = isKnowledgeListInactive(row);
              const displayFile = pickKnowledgeDisplayFile(row.files);
              return (
                <li key={row.id}>
                  <button
                    type="button"
                    className={[
                      "flex w-full items-center gap-2 px-3 py-2 text-left",
                      "hover:bg-ecmp-hover focus-visible:bg-ecmp-hover",
                      muted ? "opacity-60" : "",
                    ]
                      .filter(Boolean)
                      .join(" ")}
                    onClick={() => router.push(`/knowledge/${row.id}`)}
                  >
                    <span
                      className={[
                        "h-2 w-2 shrink-0 rounded-full",
                        knowledgeStatusDotClass(row.status),
                      ].join(" ")}
                      aria-hidden
                    />
                    <KnowledgeFileTypeIcon file={displayFile} size="sm" />
                    <KnowledgeTypeBadge type={row.knowledgeType} />
                    <span className="min-w-0 flex-1 truncate text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary">
                      {row.title}
                    </span>
                    <span
                      className="hidden min-w-0 max-w-[55%] shrink-0 truncate text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary sm:inline"
                      title={meta}
                    >
                      {meta || tCommon("emDash")}
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
          <Pagination
            summary={tCommon("showingItems", {
              from: (page - 1) * pageSize + 1,
              to: Math.min(page * pageSize, totalItems),
              total: totalItems,
            })}
            pageSizeSlot={
              <div className="w-[9rem]">
                <Select
                  name="knowledgePageSize"
                  aria-label={t("pageSizeLabel")}
                  options={pageSizeOptions}
                  value={String(pageSize)}
                  onChange={(e) => {
                    setPageSize(Number(e.target.value) || DEFAULT_PAGE_SIZE);
                    setPage(1);
                  }}
                />
              </div>
            }
            previousLabel={tCommon("previous")}
            nextLabel={tCommon("next")}
            onPrevious={() => setPage((p) => Math.max(1, p - 1))}
            onNext={() => setPage((p) => Math.min(totalPages, p + 1))}
            previousDisabled={page <= 1}
            nextDisabled={page >= totalPages}
          />
        </div>
      )}

      <Modal
        open={showCreate}
        onClose={() => {
          setShowCreate(false);
          resetCreateForm();
        }}
        title={t("createTitle")}
        footer={
          <>
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                setShowCreate(false);
                resetCreateForm();
              }}
              disabled={creating}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="submit"
              form="knowledge-create-form"
              loading={creating}
              disabled={creating}
            >
              {creating ? tCommon("saving") : tCommon("save")}
            </Button>
          </>
        }
      >
        <form
          id="knowledge-create-form"
          className="space-y-[var(--ecmp-form-gap)]"
          onSubmit={(e) => void submitCreate(e)}
          noValidate
        >
          {createError ? (
            <Alert tone="danger" title={t("actionFailed")} description={createError} />
          ) : null}
          <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
            {t("createHint")}
          </p>
          <KnowledgeFormFields
            values={createValues}
            fieldErrors={createErrors}
            onChange={(key, value) =>
              setCreateValues((prev) => ({ ...prev, [key]: value }))
            }
          />
          <KnowledgeCreateFileStaging
            files={stagedFiles}
            onChange={setStagedFiles}
            disabled={creating}
          />
        </form>
      </Modal>
    </PageContainer>
  );
}
