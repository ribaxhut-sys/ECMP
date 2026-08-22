"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  archiveKnowledge,
  createKnowledge,
  deleteKnowledge,
  fetchKnowledge,
  publishKnowledge,
  unarchiveKnowledge,
  updateKnowledge,
  uploadKnowledgeFile,
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
import { KnowledgeCreateFileStaging, type StagedKnowledgeFile } from "./KnowledgeCreateFileStaging";
import { KnowledgeFileManager } from "./KnowledgeFileManager";
import { KnowledgeHistorySection } from "./KnowledgeHistorySection";
import { KnowledgeFormFields } from "./KnowledgeFormFields";
import {
  knowledgeFormFromExisting,
  toKnowledgeCreateRequest,
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
  const tAttachments = useTranslations("attachments");
  const { hasPermission, roles } = useAuth();
  const orgUnitCode = useOrgUnitCode();
  const locale = useLocale();
  const { push: pushToast, pushSuccess } = useToast();

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

  const [replacing, setReplacing] = useState(false);
  const [replaceValues, setReplaceValues] = useState<KnowledgeFormValues | null>(null);
  const [replaceErrors, setReplaceErrors] = useState<KnowledgeFieldErrors>({});
  const [replaceError, setReplaceError] = useState<string | null>(null);
  const [savingReplace, setSavingReplace] = useState(false);
  const [stagedFiles, setStagedFiles] = useState<StagedKnowledgeFile[]>([]);

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

  function closeReplace() {
    setReplacing(false);
    setReplaceValues(null);
    setReplaceErrors({});
    setReplaceError(null);
    setStagedFiles([]);
  }

  function openReplace() {
    if (!knowledge) return;
    setEditing(false);
    setActionError(null);
    setReplaceErrors({});
    setReplaceError(null);
    setReplaceValues(knowledgeFormFromExisting(knowledge));
    setStagedFiles([]);
    setReplacing(true);
  }

  async function submitReplace(event: FormEvent) {
    event.preventDefault();
    if (!knowledge || !replaceValues) return;
    const errors = validateKnowledgeForm(replaceValues);
    setReplaceErrors(errors);
    if (Object.keys(errors).length > 0) return;

    setSavingReplace(true);
    setReplaceError(null);
    try {
      const res = await createKnowledge(
        toKnowledgeCreateRequest(replaceValues, {
          supersedesKnowledgeId: knowledge.id,
        }),
      );
      const created = res.data;

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

      closeReplace();
      if (failedFileNames.length > 0) {
        pushToast({
          title: tAttachments("partialUploadFailed", { detail: failedFileNames.join(", ") }),
          tone: "warning",
        });
      } else {
        pushSuccess(tCommon("success"), t("createReplacementSuccess"));
      }
      router.push(`/knowledge/${created.id}`);
    } catch (err) {
      setReplaceError(resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToSave"));
    } finally {
      setSavingReplace(false);
    }
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
      pushSuccess(
        tCommon("success"),
        knowledge.supersedesKnowledgeId
          ? t("publishedReplacementSuccess")
          : t("publishedSuccess"),
      );
    } catch (err) {
      setActionError(
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : t("unableToPublish"),
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

      {knowledge.status === "DRAFT" && knowledge.supersedesTitle ? (
        <Alert
          tone="info"
          title={t("replacementDraftBannerTitle")}
          description={t("replacementDraftBanner", { title: knowledge.supersedesTitle })}
        />
      ) : null}

      {canManage ? (
        <div className="flex flex-wrap gap-2">
          <Button type="button" size="sm" variant="secondary" onClick={openEdit}>
            {tCommon("edit")}
          </Button>
          {knowledge.status !== "DRAFT" ? (
            <Button type="button" size="sm" variant="outline" onClick={openReplace}>
              {t("createReplacement")}
            </Button>
          ) : null}
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
              identityLockedAction={
                knowledge.status !== "DRAFT" ? (
                  <Button type="button" size="sm" variant="outline" onClick={openReplace}>
                    {t("createReplacement")}
                  </Button>
                ) : null
              }
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
        open={replacing}
        onClose={() => {
          if (!savingReplace) closeReplace();
        }}
        title={t("createReplacementTitle")}
        footer={
          <>
            <Button
              type="button"
              variant="secondary"
              onClick={closeReplace}
              disabled={savingReplace}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="submit"
              form="knowledge-replace-form"
              loading={savingReplace}
              disabled={savingReplace}
            >
              {savingReplace ? tCommon("saving") : tCommon("save")}
            </Button>
          </>
        }
      >
        {replaceValues ? (
          <form
            id="knowledge-replace-form"
            className="space-y-[var(--ecmp-form-gap)]"
            onSubmit={(e) => void submitReplace(e)}
            noValidate
          >
            {replaceError ? (
              <Alert tone="danger" title={t("actionFailed")} description={replaceError} />
            ) : null}
            <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
              {t("createReplacementHint", { title: knowledge.title })}
            </p>
            <KnowledgeFormFields
              values={replaceValues}
              fieldErrors={replaceErrors}
              onChange={(key, value) =>
                setReplaceValues((prev) => (prev ? { ...prev, [key]: value } : prev))
              }
            />
            <KnowledgeCreateFileStaging
              files={stagedFiles}
              onChange={setStagedFiles}
              disabled={savingReplace}
            />
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
