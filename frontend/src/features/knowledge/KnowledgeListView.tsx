"use client";

import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { createKnowledge, searchKnowledge } from "@/lib/api";
import type { Knowledge, KnowledgeStatus, KnowledgeType } from "@/lib/api/types";
import {
  Alert,
  Button,
  Empty,
  ErrorState,
  Input,
  Modal,
  PageContainer,
  PageHeader,
  Select,
  Skeleton,
  Table,
  type TableColumn,
} from "@/shared/ui";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { knowledgeTypeKey, KnowledgeStatusBadge, KnowledgeTypeBadge } from "./KnowledgeBadges";
import { KnowledgeFormFields } from "./KnowledgeFormFields";
import { mayManageKnowledge } from "./knowledgeManageGate";
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

/**
 * Single shared list — search/filter for every knowledge:read holder;
 * "+ Tambah" and DRAFT status filter appear only for knowledge:manage
 * (Pusat-proven, mirrors announcement manage gate).
 */
export function KnowledgeListView() {
  const router = useRouter();
  const t = useTranslations("knowledge");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
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

  const [showCreate, setShowCreate] = useState(false);
  const [createValues, setCreateValues] = useState<KnowledgeFormValues>(
    createEmptyKnowledgeForm,
  );
  const [createErrors, setCreateErrors] = useState<KnowledgeFieldErrors>({});
  const [createError, setCreateError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const res = await searchKnowledge({
        q: search || undefined,
        type: typeFilter || undefined,
        status: statusFilter,
      });
      setRows(res.data);
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
      setShowCreate(false);
      resetCreateForm();
      router.push(`/knowledge/${res.data.id}`);
    } catch (err) {
      setCreateError(resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToSave"));
    } finally {
      setCreating(false);
    }
  }

  const columns: TableColumn<Knowledge>[] = [
    {
      key: "title",
      header: t("columnTitle"),
      cell: (row) => (
        <div className="min-w-0 max-w-[28rem]">
          <p className="truncate font-medium text-ecmp-text-primary">{row.title}</p>
          <p className="truncate text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
            {[row.documentNumber, row.versionLabel ? `v${row.versionLabel}` : null]
              .filter(Boolean)
              .join(" · ") || tCommon("emDash")}
          </p>
        </div>
      ),
    },
    {
      key: "type",
      header: t("columnType"),
      cell: (row) => <KnowledgeTypeBadge type={row.knowledgeType} />,
    },
    {
      key: "status",
      header: t("columnStatus"),
      slot: "status",
      cell: (row) => <KnowledgeStatusBadge status={row.status} />,
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
        <Table
          columns={columns}
          rows={rows}
          getRowKey={(row) => row.id}
          caption={t("tableCaption")}
          onRowClick={(row) => router.push(`/knowledge/${row.id}`)}
        />
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
        </form>
      </Modal>
    </PageContainer>
  );
}
