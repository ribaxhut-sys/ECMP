"use client";

import { useCallback, useEffect, useRef, useState, type ChangeEvent } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  downloadAttachment,
  fetchCmBatch1ComplaintAttachments,
  uploadCmBatch1Attachment,
  voidCmBatch1Attachment,
  type CmBatch1AttachmentClassification,
  type CmBatch1AttachmentResponse,
} from "@/lib/api";
import {
  CM_BATCH1_MAX_MULTI_UPLOAD,
  CM_BATCH1_VOID_REASON_UPLOADER_REMOVED,
  cmBatch1AttachmentClassificationLabelKey,
  cmBatch1AttachmentListLabel,
  cmBatch1VoidTargetId,
  formatCmBatch1AttachmentBytes,
  formatCmBatch1AttachmentSummaryLine,
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
  Skeleton,
} from "@/shared/ui";

const CLASSIFICATION_OPTIONS = [
  { value: "customer_evidence", label: "classificationCustomerEvidence" },
  { value: "internal_evidence", label: "classificationInternalEvidence" },
  { value: "official_letter", label: "classificationOfficialLetter" },
] as const;

const ACCEPT_MIME =
  "application/pdf,image/jpeg,image/png,image/webp,video/mp4,text/plain,.pdf,.jpg,.jpeg,.png,.webp,.mp4,.txt";

/**
 * Bound attachments on Aggregate confirmation (API-509 list + API-507 upload + API-512 void).
 * Attachments are optional — upload here recovers attachment_bind_failed later-review.
 */
export function CmBatch1BoundAttachmentsCard({
  complaintId,
  customerId = null,
  allowVoid = true,
  allowUpload = true,
}: {
  complaintId: string;
  customerId?: string | null;
  allowVoid?: boolean;
  allowUpload?: boolean;
}) {
  const t = useTranslations("complaints");
  const { hasPermission } = useAuth();
  const canRead =
    hasPermission("attachment:read") || hasPermission("*");
  const canUpload =
    allowUpload &&
    (hasPermission("attachment:create") || hasPermission("*"));
  const canVoid =
    allowVoid &&
    (hasPermission("attachment:delete") || hasPermission("*"));
  /** Closed / locked complaint: read + open only (no upload/void chrome). */
  const readOnlyList = !allowUpload && !allowVoid;
  const inputRef = useRef<HTMLInputElement>(null);

  const [items, setItems] = useState<CmBatch1AttachmentResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [classification, setClassification] =
    useState<CmBatch1AttachmentClassification>("customer_evidence");
  const [voidingId, setVoidingId] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const previewTabsRef = useRef<Map<string, Window>>(new Map());

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

  const load = useCallback(async () => {
    if (!canRead || !complaintId.trim()) {
      setItems([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetchCmBatch1ComplaintAttachments(complaintId.trim());
      setItems(
        (res.data ?? []).map(
          (row) =>
            normalizeCmBatch1Attachment(
              row as unknown as Record<string, unknown>,
            ) as CmBatch1AttachmentResponse,
        ),
      );
    } catch (err) {
      setItems([]);
      setError(
        err instanceof ApiError
          ? err.message
          : t("unableToLoadAggregateAttachments"),
      );
    } finally {
      setLoading(false);
    }
  }, [canRead, complaintId, t]);

  useEffect(() => {
    void load();
  }, [load]);

  const onFileChange = useCallback(
    async (event: ChangeEvent<HTMLInputElement>) => {
      const { files, truncated } = pickCmBatch1UploadFiles(event.target.files);
      event.target.value = "";
      if (files.length === 0 || !canUpload || uploading) return;

      setUploading(true);
      setError(null);
      setInfo(null);
      const uploaded: CmBatch1AttachmentResponse[] = [];
      const failures: string[] = [];
      try {
        for (const file of files) {
          try {
            const res = await uploadCmBatch1Attachment({
              file,
              classification,
              complaintId: complaintId.trim(),
              customerId: customerId?.trim() || null,
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
          } catch (err) {
            const detail =
              err instanceof ApiError
                ? err.message
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
          setItems((prev) => [...uploaded, ...prev]);
          setInfo(
            uploaded.length === 1
              ? t("attachmentAddedOptional")
              : t("attachmentMultiUploadSuccess", { count: uploaded.length }),
          );
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
    [canUpload, classification, complaintId, customerId, t, uploading],
  );

  const onVoid = useCallback(
    async (item: CmBatch1AttachmentResponse) => {
      if (!canVoid || voidingId) return;
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
        return prev.filter((row) => !isSameCmBatch1Attachment(row, targetId));
      });
      closePreviewTab(targetId);
      try {
        await voidCmBatch1Attachment(
          targetId,
          CM_BATCH1_VOID_REASON_UPLOADER_REMOVED,
        );
      } catch (err) {
        setItems(snapshot);
        setError(
          err instanceof ApiError
            ? err.message
            : err instanceof Error
              ? err.message
              : t("unableToVoidAttachment"),
        );
      } finally {
        setVoidingId(null);
      }
    },
    [canVoid, closePreviewTab, t, voidingId],
  );

  const onOpen = useCallback(
    async (item: CmBatch1AttachmentResponse) => {
      if (!canRead || busyId) return;
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
        // Revoke later so the new tab can still read the blob.
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
              : err.message
            : t("unableToOpenAttachment"),
        );
      } finally {
        setBusyId(null);
      }
    },
    [busyId, canRead, t],
  );

  if (!canRead) {
    return (
      <Alert
        tone="info"
        title={t("boundAttachments")}
        description={t("noAttachmentReadPermission")}
      />
    );
  }

  const visible = items.filter(
    (item) => item.status !== "VOID" && item.status !== "SUPERSEDED",
  );

  return (
    <section
      className="space-y-[var(--ecmp-form-gap)]"
      data-testid="cm-batch1-bound-attachments"
    >
      <SectionHeader
        title={t("boundAttachments")}
        description={
          readOnlyList
            ? t("boundAttachmentsClosedDescription")
            : t("boundAttachmentsOptionalDescription")
        }
      />
      <Card>
        <CardBody className="space-y-3">
          {loading ? <Skeleton rows={3} /> : null}

          {!loading && error ? (
            <Alert
              tone="danger"
              title={t("attachmentError")}
              description={error}
            />
          ) : null}

          {!loading && info ? (
            <Alert tone="info" title={t("notice")} description={info} />
          ) : null}

          {canUpload ? (
            <>
              <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:gap-3">
                <div className="min-w-0 sm:max-w-xs sm:flex-1">
                  <Select
                    name="boundAttachmentClassification"
                    id="boundAttachmentClassification"
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
                    disabled={uploading || loading}
                  />
                </div>
                <input
                  ref={inputRef}
                  type="file"
                  className="sr-only"
                  accept={ACCEPT_MIME}
                  multiple
                  disabled={uploading || loading}
                  onChange={(event) => void onFileChange(event)}
                  aria-label={t("chooseFile")}
                />
                <Button
                  type="button"
                  className="shrink-0 sm:self-end"
                  onClick={() => inputRef.current?.click()}
                  loading={uploading}
                  disabled={uploading || loading}
                  aria-label={t("uploadBoundAttachment")}
                >
                  {uploading ? t("uploading") : t("uploadFile")}
                </Button>
              </div>
              <p className="text-[length:var(--ecmp-font-helper-size)] leading-snug text-ecmp-text-secondary">
                {t("filePolicy")}
              </p>
            </>
          ) : null}

          {!loading && !error && visible.length === 0 ? (
            <div
              data-testid="bound-empty"
              className="rounded-[var(--ecmp-radius-md)] border border-dashed border-ecmp-border/80 bg-ecmp-surface-sunken/50 px-3 py-4 text-center"
            >
              <p className="text-[length:var(--ecmp-font-body-small-size)] font-medium text-ecmp-text-primary">
                {t(cmBatch1AttachmentListLabel(0))}
              </p>
              <p className="mt-1 text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                {readOnlyList
                  ? t("boundAttachmentsClosedDescription")
                  : canUpload
                    ? t("noStagedAttachmentsHint")
                    : t("boundAttachmentsOptionalDescription")}
              </p>
            </div>
          ) : null}

          {!loading && !error && visible.length > 0 ? (
            <ul
              className="divide-y divide-ecmp-border rounded-[var(--ecmp-radius-md)] border border-ecmp-border"
              data-testid="bound-list"
              aria-label={t("boundAttachmentsAria")}
            >
              {visible.map((item) => {
                const rowId = cmBatch1VoidTargetId(item) ?? item.originalName;
                const classificationKey =
                  cmBatch1AttachmentClassificationLabelKey(
                    item.classification,
                  );
                const classificationLabel =
                  classificationKey === item.classification
                    ? item.classification
                    : t(classificationKey);
                return (
                  <li
                    key={rowId}
                    className="flex flex-col gap-2 px-3 py-2 text-[length:var(--ecmp-font-body-size)] sm:flex-row sm:items-center sm:justify-between"
                    data-testid={`bound-item-${rowId}`}
                  >
                    {readOnlyList ? (
                      <p className="min-w-0 truncate text-ecmp-text-primary">
                        {formatCmBatch1AttachmentSummaryLine(
                          item.originalName,
                          item.sizeBytes,
                          classificationLabel,
                        )}
                      </p>
                    ) : (
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
                    )}
                    <div className="flex flex-shrink-0 flex-wrap gap-2">
                      {canRead ? (
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          disabled={busyId !== null || voidingId !== null}
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
                          disabled={busyId !== null || voidingId !== null}
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
          ) : null}
        </CardBody>
      </Card>
    </section>
  );
}
