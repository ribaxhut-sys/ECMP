"use client";

import { useCallback, useEffect, useRef, useState, type ChangeEvent } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  downloadAttachment,
  uploadCmBatch1Attachment,
  voidCmBatch1Attachment,
  type CmBatch1AttachmentClassification,
  type CmBatch1AttachmentResponse,
} from "@/lib/api";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import {
  CM_BATCH1_MAX_MULTI_UPLOAD,
  CM_BATCH1_VOID_REASON_UPLOADER_REMOVED,
  cmBatch1AttachmentClassificationLabelKey,
  cmBatch1VoidTargetId,
  formatCmBatch1AttachmentBytes,
  isCmBatch1AttachmentVoidable,
  isSameCmBatch1Attachment,
  normalizeCmBatch1Attachment,
  openBlankAttachmentTab,
  pickCmBatch1UploadFiles,
  showAttachmentInTab,
} from "./cmBatch1Attachments";
import {
  Alert,
  Badge,
  Button,
  Card,
  CardBody,
  SectionHeader,
  Select,
} from "@/shared/ui";

const CLASSIFICATION_OPTIONS = [
  { value: "customer_evidence", label: "classificationCustomerEvidence" },
  { value: "internal_evidence", label: "classificationInternalEvidence" },
  { value: "official_letter", label: "classificationOfficialLetter" },
  { value: "other", label: "classificationOther" },
] as const;

const ACCEPT_MIME =
  "application/pdf,image/jpeg,image/png,image/gif,image/webp,video/mp4,text/plain,application/zip,.pdf,.jpg,.jpeg,.png,.gif,.webp,.mp4,.txt,.zip";

export interface StagingAttachmentsPanelProps {
  stagingToken: string;
  customerId?: string | null;
  disabled?: boolean;
  onStagingTokenResolved?: (token: string) => void;
  /** True when at least one non-void staged file exists (informational). */
  onHasStagedChange?: (hasStaged: boolean) => void;
  /** True while a staging upload/void is in flight — parent should block submit. */
  onBusyChange?: (busy: boolean) => void;
}

/**
 * SCR-CM-004 — FR-004 staged upload + logical void for Aggregate create (API-507/512).
 */
export function StagingAttachmentsPanel({
  stagingToken,
  customerId = null,
  disabled = false,
  onStagingTokenResolved,
  onHasStagedChange,
  onBusyChange,
}: StagingAttachmentsPanelProps) {
  const t = useTranslations("complaints");
  const tErrors = useTranslations("errors");
  const tCommon = useTranslations("common");
  const { hasPermission } = useAuth();
  const canUpload =
    hasPermission("attachment:create") || hasPermission("*");
  const canOpen =
    hasPermission("attachment:read") ||
    hasPermission("attachment:create") ||
    hasPermission("*");
  const canVoid =
    hasPermission("attachment:delete") || hasPermission("*");
  const inputRef = useRef<HTMLInputElement>(null);

  const [classification, setClassification] =
    useState<CmBatch1AttachmentClassification>("customer_evidence");
  const [items, setItems] = useState<CmBatch1AttachmentResponse[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [voidingId, setVoidingId] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const previewTabsRef = useRef<Map<string, Window>>(new Map());

  const customerLocked = Boolean(customerId?.trim());
  const uploadBlocked = disabled || !customerLocked;

  const closePreviewTab = useCallback((attachmentId: string) => {
    const tab = previewTabsRef.current.get(attachmentId);
    if (tab && !tab.closed) {
      try {
        tab.close();
      } catch {
        /* ignore */
      }
    }
    previewTabsRef.current.delete(attachmentId);
  }, []);

  useEffect(() => {
    onBusyChange?.(uploading || Boolean(voidingId) || Boolean(busyId));
  }, [busyId, onBusyChange, uploading, voidingId]);

  const onOpen = useCallback(
    async (item: CmBatch1AttachmentResponse) => {
      if (!canOpen || busyId || disabled) return;
      const rowId = cmBatch1VoidTargetId(item);
      const platformId = item.platformAttachmentId?.trim() || rowId;
      if (!rowId || !platformId) {
        setError(t("unableToOpenAttachment"));
        return;
      }
      const preview = openBlankAttachmentTab();
      if (!preview) {
        setError(t("attachmentPopupBlocked"));
        return;
      }
      setBusyId(rowId);
      setError(null);
      try {
        const result = await downloadAttachment(platformId);
        const url = URL.createObjectURL(result.blob);
        showAttachmentInTab(preview, url);
        previewTabsRef.current.set(rowId, preview);
        window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
      } catch (err) {
        try {
          preview.close();
        } catch {
          /* ignore */
        }
        setError(
          err instanceof ApiError
            ? err.status === 404
              ? t("attachmentBlobMissing")
              : resolveApiErrorMessage(err, tErrors, tCommon)
            : t("unableToOpenAttachment"),
        );
      } finally {
        setBusyId(null);
      }
    },
    [busyId, canOpen, disabled, t, tErrors, tCommon],
  );

  const notifyStaged = useCallback(
    (next: CmBatch1AttachmentResponse[]) => {
      const hasStaged = next.some((item) => item.status !== "VOID");
      onHasStagedChange?.(hasStaged);
    },
    [onHasStagedChange],
  );

  const onPick = useCallback(() => {
    inputRef.current?.click();
  }, []);

  const onFileChange = useCallback(
    async (event: ChangeEvent<HTMLInputElement>) => {
      const { files, truncated } = pickCmBatch1UploadFiles(event.target.files);
      event.target.value = "";
      if (files.length === 0 || !canUpload || uploadBlocked) return;
      const lockedCustomerId = customerId?.trim();
      if (!lockedCustomerId) {
        setError(t("attachAfterCustomerConfirm"));
        return;
      }

      setUploading(true);
      setError(null);
      let token = stagingToken;
      const uploaded: CmBatch1AttachmentResponse[] = [];
      const failures: string[] = [];
      try {
        for (const file of files) {
          try {
            const res = await uploadCmBatch1Attachment({
              file,
              classification,
              stagingToken: token,
              customerId: lockedCustomerId,
            });
            const data = normalizeCmBatch1Attachment(
              res.data as unknown as Record<string, unknown>,
            ) as CmBatch1AttachmentResponse;
            if (!data.attachmentId && !data.platformAttachmentId) {
              failures.push(
                t("attachmentUploadNamedFailed", {
                  name: file.name,
                  detail: t("unableToUploadAttachment"),
                }),
              );
              continue;
            }
            uploaded.push(data);
            const resolved = data.stagingToken?.trim() || token;
            if (resolved && resolved !== token) {
              token = resolved;
              onStagingTokenResolved?.(resolved);
            }
          } catch (err) {
            const detail =
              err instanceof ApiError
                ? resolveApiErrorMessage(err, tErrors, tCommon)
                : err instanceof Error
                  ? err.message
                  : t("unableToUploadAttachment");
            failures.push(
              t("attachmentUploadNamedFailed", {
                name: file.name,
                detail,
              }),
            );
          }
        }
        if (uploaded.length > 0) {
          setItems((prev) => {
            const next = [...uploaded, ...prev];
            notifyStaged(next);
            return next;
          });
        }
        const notes: string[] = [];
        if (truncated) {
          notes.push(
            t("attachmentMultiUploadTruncated", {
              max: CM_BATCH1_MAX_MULTI_UPLOAD,
            }),
          );
        }
        if (failures.length > 0) {
          notes.push(
            t("attachmentMultiUploadPartial", {
              ok: uploaded.length,
              fail: failures.length,
              details: failures.join("; "),
            }),
          );
        }
        if (notes.length > 0) {
          setError(notes.join(" "));
        }
      } finally {
        setUploading(false);
      }
    },
    [
      canUpload,
      classification,
      customerId,
      notifyStaged,
      onStagingTokenResolved,
      stagingToken,
      t,
      tErrors,
      tCommon,
      uploadBlocked,
    ],
  );

  const onVoid = useCallback(
    async (item: CmBatch1AttachmentResponse) => {
      if (!canVoid || disabled || voidingId) return;
      const targetId = cmBatch1VoidTargetId(item);
      if (!targetId) {
        setError(t("unableToVoidAttachment"));
        return;
      }
      setVoidingId(targetId);
      setError(null);
      let snapshot: CmBatch1AttachmentResponse[] = [];
      setItems((prev) => {
        snapshot = prev;
        const next = prev.filter(
          (row) => !isSameCmBatch1Attachment(row, targetId),
        );
        notifyStaged(next);
        return next;
      });
      closePreviewTab(targetId);
      try {
        await voidCmBatch1Attachment(
          targetId,
          CM_BATCH1_VOID_REASON_UPLOADER_REMOVED,
        );
      } catch (err) {
        setItems(() => {
          notifyStaged(snapshot);
          return snapshot;
        });
        setError(
          err instanceof ApiError
            ? resolveApiErrorMessage(err, tErrors, tCommon)
            : err instanceof Error
              ? err.message
              : t("unableToVoidAttachment"),
        );
      } finally {
        setVoidingId(null);
      }
    },
    [canVoid, closePreviewTab, disabled, notifyStaged, t, tErrors, tCommon, voidingId],
  );

  const visible = items.filter(
    (item) => item.status !== "VOID" && item.status !== "SUPERSEDED",
  );

  if (!canUpload) {
    return (
      <Alert
        tone="info"
        title={t("attachmentsUnavailable")}
        description={t("stageEvidencePermission")}
      />
    );
  }

  return (
    <section className="space-y-[var(--ecmp-form-gap)]">
      <SectionHeader
        title={t("stagedAttachments")}
        description={t("stagedAttachmentsDescription")}
      />
      <Card>
        <CardBody className="space-y-3">
          {error ? (
            <Alert tone="danger" title={t("attachmentError")} description={error} />
          ) : null}

          {!customerLocked ? (
            <Alert
              tone="info"
              title={t("attachNeedsCustomerTitle")}
              description={t("attachAfterCustomerConfirm")}
            />
          ) : null}

          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:gap-3">
            <div className="min-w-0 sm:max-w-xs sm:flex-1">
              <Select
                name="attachmentClassification"
                id="attachmentClassification"
                label={t("classification")}
                options={CLASSIFICATION_OPTIONS.map((option) => ({
                  ...option,
                  label: t(option.label),
                }))}
                value={classification}
                onChange={(event) =>
                  setClassification(
                    event.target.value as CmBatch1AttachmentClassification,
                  )
                }
                disabled={uploadBlocked || uploading}
              />
            </div>
            <input
              ref={inputRef}
              type="file"
              className="sr-only"
              accept={ACCEPT_MIME}
              multiple
              disabled={uploadBlocked || uploading}
              onChange={(event) => void onFileChange(event)}
              aria-label={t("chooseFile")}
            />
            <Button
              type="button"
              className="shrink-0 sm:self-end"
              onClick={onPick}
              loading={uploading}
              disabled={uploadBlocked || uploading}
              aria-label={t("uploadStagedAttachment")}
            >
              {uploading ? t("uploading") : t("uploadFile")}
            </Button>
          </div>
          <p className="text-[length:var(--ecmp-font-helper-size)] leading-snug text-ecmp-text-secondary">
            {t("filePolicy")}
          </p>

          {visible.length === 0 ? (
            <div
              data-testid="staging-empty"
              className="rounded-[var(--ecmp-radius-md)] border border-dashed border-ecmp-border/80 bg-ecmp-surface-sunken/50 px-3 py-4 text-center"
            >
              <p className="text-[length:var(--ecmp-font-body-small-size)] font-medium text-ecmp-text-primary">
                {t("noStagedAttachments")}
              </p>
              <p className="mt-1 text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                {t("noStagedAttachmentsHint")}
              </p>
            </div>
          ) : (
            <ul
              className="divide-y divide-ecmp-border rounded-[var(--ecmp-radius-md)] border border-ecmp-border"
              data-testid="staging-list"
              aria-label={t("stagedAttachmentsAria")}
            >
              {visible.map((item) => {
                const rowId = cmBatch1VoidTargetId(item) ?? item.originalName;
                const classificationKey =
                  cmBatch1AttachmentClassificationLabelKey(item.classification);
                const classificationLabel =
                  classificationKey === item.classification
                    ? item.classification
                    : t(classificationKey);
                return (
                  <li
                    key={rowId}
                    className="flex flex-col gap-2 px-3 py-2 text-[length:var(--ecmp-font-body-size)] sm:flex-row sm:items-center sm:justify-between"
                    data-testid={`staging-item-${rowId}`}
                  >
                    <div className="min-w-0 space-y-0.5">
                      <span className="block truncate font-medium text-ecmp-text-primary">
                        {item.originalName}
                      </span>
                      <div className="flex flex-wrap items-center gap-2">
                        <Badge tone="neutral">{item.status}</Badge>
                        <Badge tone="info">{classificationLabel}</Badge>
                        <span className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                          {formatCmBatch1AttachmentBytes(item.sizeBytes)}
                        </span>
                      </div>
                    </div>
                    <div className="flex flex-shrink-0 flex-wrap gap-2">
                      {canOpen ? (
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          disabled={
                            disabled || busyId !== null || voidingId !== null
                          }
                          loading={busyId === rowId}
                          onClick={() => void onOpen(item)}
                          aria-label={t("openAttachmentNamed", {
                            name: item.originalName,
                          })}
                        >
                          {t("openAttachment")}
                        </Button>
                      ) : null}
                      {canVoid && isCmBatch1AttachmentVoidable(item.status) ? (
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          disabled={
                            disabled || busyId !== null || voidingId !== null
                          }
                          loading={voidingId === rowId}
                          onClick={() => void onVoid(item)}
                          aria-label={t("voidNamed", {
                            name: item.originalName,
                          })}
                        >
                          {t("void")}
                        </Button>
                      ) : null}
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
        </CardBody>
      </Card>
    </section>
  );
}
