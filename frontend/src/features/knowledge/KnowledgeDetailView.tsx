"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  archiveKnowledge,
  deleteKnowledge,
  fetchKnowledge,
  publishKnowledge,
  unarchiveKnowledge,
  updateKnowledge,
} from "@/lib/api";
import type { Knowledge } from "@/lib/api/types";
import { formatDateTime } from "@/i18n/formatting";
import {
  Alert,
  Button,
  Card,
  CardBody,
  ErrorState,
  Modal,
  PageContainer,
  PageHeader,
  SectionHeader,
  Skeleton,
} from "@/shared/ui";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { useToast } from "@/shared/providers";
import { useOrgUnitCode } from "@/features/announcements/useOrgUnitCode";
import { knowledgeTypeKey, KnowledgeStatusBadge, KnowledgeTypeBadge } from "./KnowledgeBadges";
import { KnowledgeFileManager } from "./KnowledgeFileManager";
import { KnowledgeHistorySection } from "./KnowledgeHistorySection";
import { KnowledgeFormFields } from "./KnowledgeFormFields";
import {
  knowledgeFormFromExisting,
  toKnowledgeUpdateRequest,
  validateKnowledgeForm,
  type KnowledgeFieldErrors,
  type KnowledgeFormValues,
} from "./knowledgeForm";
import { mayManageKnowledge } from "./knowledgeManageGate";

function DetailField({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0 space-y-1">
      <dt className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
        {label}
      </dt>
      <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
        {value}
      </dd>
    </div>
  );
}

export function KnowledgeDetailView({ id }: { id: string }) {
  const router = useRouter();
  const t = useTranslations("knowledge");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const { hasPermission, roles } = useAuth();
  const orgUnitCode = useOrgUnitCode();
  const locale = useLocale();
  const { pushSuccess } = useToast();

  const canManage =
    orgUnitCode !== undefined &&
    mayManageKnowledge({ roles, hasPermission, orgUnitCode });

  const [knowledge, setKnowledge] = useState<Knowledge | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const [editing, setEditing] = useState(false);
  const [editValues, setEditValues] = useState<KnowledgeFormValues | null>(null);
  const [editErrors, setEditErrors] = useState<KnowledgeFieldErrors>({});
  const [savingEdit, setSavingEdit] = useState(false);

  const [showDelete, setShowDelete] = useState(false);
  const [deleteBusy, setDeleteBusy] = useState(false);
  const [showUnarchive, setShowUnarchive] = useState(false);
  const [unarchiveBusy, setUnarchiveBusy] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const res = await fetchKnowledge(id);
      setKnowledge(res.data);
    } catch (err) {
      setKnowledge(null);
      setLoadError(resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToLoad"));
    } finally {
      setLoading(false);
    }
  }, [id, t, tCommon, tErrors]);

  useEffect(() => {
    void load();
  }, [load]);

  function openEdit() {
    if (!knowledge) return;
    setActionError(null);
    setEditErrors({});
    setEditValues(knowledgeFormFromExisting(knowledge));
    setEditing(true);
  }

  async function submitEdit(event: FormEvent) {
    event.preventDefault();
    if (!knowledge || !editValues) return;
    const errors = validateKnowledgeForm(editValues);
    setEditErrors(errors);
    if (Object.keys(errors).length > 0) return;

    setSavingEdit(true);
    setActionError(null);
    try {
      const res = await updateKnowledge(knowledge.id, toKnowledgeUpdateRequest(editValues));
      setKnowledge(res.data);
      pushSuccess(tCommon("success"), t("updatedSuccess"));
      setEditing(false);
    } catch (err) {
      setActionError(resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToSave"));
    } finally {
      setSavingEdit(false);
    }
  }

  async function onPublish() {
    if (!knowledge) return;
    if (knowledge.files.length === 0) {
      setActionError(t("publishNeedsFile"));
      return;
    }
    setBusy(true);
    setActionError(null);
    try {
      const res = await publishKnowledge(knowledge.id);
      setKnowledge(res.data);
      pushSuccess(tCommon("success"), t("publishedSuccess"));
    } catch (err) {
      setActionError(
        err instanceof ApiError && err.message
          ? err.message
          : resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToPublish"),
      );
    } finally {
      setBusy(false);
    }
  }

  async function onArchive() {
    if (!knowledge) return;
    setBusy(true);
    setActionError(null);
    try {
      const res = await archiveKnowledge(knowledge.id);
      setKnowledge(res.data);
      pushSuccess(tCommon("success"), t("archivedSuccess"));
    } catch (err) {
      setActionError(resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToArchive"));
    } finally {
      setBusy(false);
    }
  }

  async function confirmUnarchive() {
    if (!knowledge) return;
    setUnarchiveBusy(true);
    setActionError(null);
    try {
      const res = await unarchiveKnowledge(knowledge.id);
      setKnowledge(res.data);
      setShowUnarchive(false);
      pushSuccess(tCommon("success"), t("unarchivedSuccess"));
    } catch (err) {
      setActionError(
        resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToUnarchive"),
      );
    } finally {
      setUnarchiveBusy(false);
    }
  }

  async function confirmDelete() {
    if (!knowledge) return;
    setDeleteBusy(true);
    setActionError(null);
    try {
      await deleteKnowledge(knowledge.id);
      pushSuccess(tCommon("success"), t("deletedSuccess"));
      router.push("/knowledge");
    } catch (err) {
      setActionError(resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToDelete"));
      setDeleteBusy(false);
    }
  }

  if (loading) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <Skeleton rows={8} />
      </PageContainer>
    );
  }

  if (loadError || !knowledge) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <ErrorState
          title={t("unableToLoad")}
          message={loadError ?? t("unableToLoad")}
          onRetry={() => void load()}
        />
      </PageContainer>
    );
  }

  const effectiveRange = [
    knowledge.effectiveFrom ? formatDateTime(knowledge.effectiveFrom, locale) : tCommon("emDash"),
    knowledge.effectiveTo ? formatDateTime(knowledge.effectiveTo, locale) : tCommon("emDash"),
  ].join(" – ");

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={knowledge.title}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title"), href: "/knowledge" },
          { label: knowledge.title },
        ]}
        meta={
          <div className="flex flex-wrap items-center gap-2">
            <KnowledgeStatusBadge status={knowledge.status} />
            <KnowledgeTypeBadge type={knowledge.knowledgeType} />
          </div>
        }
        actions={
          <button
            type="button"
            className="text-[length:var(--ecmp-font-body-small-size)] font-medium text-ecmp-primary underline-offset-2 hover:underline"
            onClick={() => router.push("/knowledge")}
          >
            {t("backToList")}
          </button>
        }
      />

      {actionError ? (
        <Alert tone="danger" title={t("actionFailed")} description={actionError} />
      ) : null}

      {canManage ? (
        <div className="flex flex-wrap gap-2">
          <Button type="button" size="sm" variant="secondary" onClick={openEdit}>
            {tCommon("edit")}
          </Button>
          {knowledge.status === "DRAFT" ? (
            <Button
              type="button"
              size="sm"
              disabled={busy || knowledge.files.length === 0}
              title={knowledge.files.length === 0 ? t("publishNeedsFile") : undefined}
              onClick={() => void onPublish()}
            >
              {t("publish")}
            </Button>
          ) : null}
          {knowledge.status === "ACTIVE" ? (
            <Button
              type="button"
              size="sm"
              variant="outline"
              disabled={busy}
              onClick={() => void onArchive()}
            >
              {t("archive")}
            </Button>
          ) : null}
          {knowledge.status === "ARCHIVED" ? (
            <Button
              type="button"
              size="sm"
              disabled={busy || unarchiveBusy}
              onClick={() => {
                setActionError(null);
                setShowUnarchive(true);
              }}
            >
              {t("unarchive")}
            </Button>
          ) : null}
          {knowledge.status === "DRAFT" ? (
            <Button
              type="button"
              size="sm"
              variant="danger"
              disabled={busy}
              onClick={() => setShowDelete(true)}
            >
              {tCommon("delete")}
            </Button>
          ) : null}
        </div>
      ) : null}

      <section className="space-y-[var(--ecmp-panel-gap)]">
        <SectionHeader title={t("documentsSectionTitle")} />
        <KnowledgeFileManager
          knowledge={knowledge}
          canManage={canManage}
          onChanged={(next) => setKnowledge(next)}
        />
      </section>

      <Card>
        <CardBody className="space-y-[var(--ecmp-panel-gap)]">
          <dl className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] sm:grid-cols-2 lg:grid-cols-3">
            <DetailField
              label={t("fieldTypeLabel")}
              value={t(knowledgeTypeKey(knowledge.knowledgeType))}
            />
            <DetailField
              label={t("fieldDocumentNumberLabel")}
              value={knowledge.documentNumber || tCommon("emDash")}
            />
            <DetailField
              label={t("fieldVersionLabel")}
              value={knowledge.versionLabel || tCommon("emDash")}
            />
            <DetailField
              label={t("ownerOrgUnit")}
              value={knowledge.ownerOrgUnitId || tCommon("emDash")}
            />
            <DetailField label={t("effectiveRange")} value={effectiveRange} />
            {knowledge.supersedesKnowledgeId ? (
              <div className="min-w-0 space-y-1">
                <dt className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                  {t("supersedes")}
                </dt>
                <dd>
                  <button
                    type="button"
                    className="text-[length:var(--ecmp-font-body-size)] text-ecmp-primary underline-offset-2 hover:underline"
                    onClick={() =>
                      router.push(`/knowledge/${knowledge.supersedesKnowledgeId}`)
                    }
                  >
                    {knowledge.supersedesTitle || tCommon("emDash")}
                  </button>
                </dd>
              </div>
            ) : null}
          </dl>
        </CardBody>
      </Card>

      <Card>
        <CardBody className="space-y-[var(--ecmp-panel-gap)]">
          <SectionHeader title={t("fieldSummaryLabel")} />
          <div className="whitespace-pre-wrap text-[length:var(--ecmp-font-body-size)] leading-relaxed text-ecmp-text-primary">
            {knowledge.summary || tCommon("emDash")}
          </div>
        </CardBody>
      </Card>

      <section className="space-y-[var(--ecmp-panel-gap)]">
        <SectionHeader title={t("historySectionTitle")} />
        <KnowledgeHistorySection knowledgeId={knowledge.id} />
      </section>

      <Modal
        open={editing}
        onClose={() => setEditing(false)}
        title={t("editTitle")}
        footer={
          <>
            <Button
              type="button"
              variant="secondary"
              onClick={() => setEditing(false)}
              disabled={savingEdit}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="submit"
              form="knowledge-edit-form"
              loading={savingEdit}
              disabled={savingEdit}
            >
              {savingEdit ? tCommon("saving") : tCommon("save")}
            </Button>
          </>
        }
      >
        {editValues ? (
          <form
            id="knowledge-edit-form"
            className="space-y-[var(--ecmp-form-gap)]"
            onSubmit={(e) => void submitEdit(e)}
            noValidate
          >
            <KnowledgeFormFields
              values={editValues}
              fieldErrors={editErrors}
              onChange={(key, value) =>
                setEditValues((prev) => (prev ? { ...prev, [key]: value } : prev))
              }
              identityLocked={knowledge.status !== "DRAFT"}
            />
            <div className="space-y-[var(--ecmp-panel-gap)] border-t border-ecmp-border pt-[var(--ecmp-panel-gap)]">
              <SectionHeader title={t("documentsSectionTitle")} />
              <KnowledgeFileManager
                knowledge={knowledge}
                canManage={canManage}
                showInlinePreview={false}
                onChanged={(next) => setKnowledge(next)}
              />
            </div>
          </form>
        ) : null}
      </Modal>

      <Modal
        open={showDelete}
        onClose={() => setShowDelete(false)}
        title={t("deleteConfirmTitle")}
        size="sm"
        footer={
          <>
            <Button
              type="button"
              variant="secondary"
              onClick={() => setShowDelete(false)}
              disabled={deleteBusy}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              variant="danger"
              loading={deleteBusy}
              disabled={deleteBusy}
              onClick={() => void confirmDelete()}
            >
              {deleteBusy ? tCommon("saving") : tCommon("delete")}
            </Button>
          </>
        }
      >
        <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
          {t("deleteConfirmDescription", { title: knowledge.title })}
        </p>
      </Modal>

      <Modal
        open={showUnarchive}
        onClose={() => setShowUnarchive(false)}
        title={t("unarchiveConfirmTitle")}
        size="sm"
        footer={
          <>
            <Button
              type="button"
              variant="secondary"
              onClick={() => setShowUnarchive(false)}
              disabled={unarchiveBusy}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              loading={unarchiveBusy}
              disabled={unarchiveBusy}
              onClick={() => void confirmUnarchive()}
            >
              {unarchiveBusy ? tCommon("saving") : t("confirmUnarchive")}
            </Button>
          </>
        }
      >
        <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
          {t("unarchiveConfirmDescription", { title: knowledge.title })}
        </p>
      </Modal>
    </PageContainer>
  );
}
