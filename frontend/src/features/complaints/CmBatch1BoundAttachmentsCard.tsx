"use client";

import { useCallback, useEffect, useRef, useState, type ChangeEvent } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  fetchCmBatch1ComplaintAttachments,
  uploadCmBatch1Attachment,
  voidCmBatch1Attachment,
  type CmBatch1AttachmentClassification,
  type CmBatch1AttachmentResponse,
} from "@/lib/api";
import {
  cmBatch1AttachmentListLabel,
  formatCmBatch1AttachmentBytes,
  isCmBatch1AttachmentVoidable,
  normalizeCmBatch1VoidReason,
} from "./cmBatch1Attachments";
import {
  Alert,
  Badge,
  Button,
  Card,
  CardBody,
  Empty,
  Input,
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
  const inputRef = useRef<HTMLInputElement>(null);

  const [items, setItems] = useState<CmBatch1AttachmentResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [classification, setClassification] =
    useState<CmBatch1AttachmentClassification>("customer_evidence");
  const [voidTargetId, setVoidTargetId] = useState<string | null>(null);
  const [voidReason, setVoidReason] = useState("");
  const [voidingId, setVoidingId] = useState<string | null>(null);

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
      setItems(res.data ?? []);
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
      const file = event.target.files?.[0];
      event.target.value = "";
      if (!file || !canUpload || uploading) return;

      setUploading(true);
      setError(null);
      setInfo(null);
      try {
        const res = await uploadCmBatch1Attachment({
          file,
          classification,
          complaintId: complaintId.trim(),
          customerId: customerId?.trim() || null,
        });
        setItems((prev) => [res.data, ...prev]);
        setInfo(t("attachmentAddedOptional"));
      } catch (err) {
        setError(
          err instanceof ApiError
            ? err.message
            : err instanceof Error
              ? err.message
              : t("unableToUploadAttachment"),
        );
      } finally {
        setUploading(false);
      }
    },
    [canUpload, classification, complaintId, customerId, t, uploading],
  );

  const onConfirmVoid = useCallback(async () => {
    if (!voidTargetId || !canVoid) return;
    const reason = normalizeCmBatch1VoidReason(voidReason);
    if (!reason) {
      setError(t("voidReasonRequired"));
      return;
    }
    setVoidingId(voidTargetId);
    setError(null);
    try {
      const res = await voidCmBatch1Attachment(voidTargetId, reason);
      setItems((prev) =>
        prev.map((item) =>
          item.attachmentId === voidTargetId ? res.data : item,
        ),
      );
      setVoidTargetId(null);
      setVoidReason("");
    } catch (err) {
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
  }, [canVoid, voidReason, voidTargetId, t]);

  if (!canRead) {
    return (
      <Alert
        tone="info"
        title={t("boundAttachments")}
        description={t("noAttachmentReadPermission")}
      />
    );
  }

  const visible = items.filter((item) => item.status !== "VOID");

  return (
    <section
      className="space-y-[var(--ecmp-panel-gap)]"
      data-testid="cm-batch1-bound-attachments"
    >
      <SectionHeader
        title={t("boundAttachments")}
        description={t("boundAttachmentsOptionalDescription")}
      />
      <Card>
        <CardBody className="space-y-[var(--ecmp-panel-gap)]">
          {loading ? <Skeleton rows={3} /> : null}

          {!loading && error ? (
            <Alert
              tone="danger"
              title={t("couldNotLoadAttachments")}
              description={error}
            />
          ) : null}

          {!loading && info ? (
            <Alert tone="info" title={t("notice")} description={info} />
          ) : null}

          {canUpload ? (
            <div className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] md:grid-cols-2 md:items-end">
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
              <div className="flex flex-col gap-2">
                <input
                  ref={inputRef}
                  type="file"
                  className="sr-only"
                  accept={ACCEPT_MIME}
                  disabled={uploading || loading}
                  onChange={(event) => void onFileChange(event)}
                  aria-label={t("chooseFile")}
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => inputRef.current?.click()}
                  loading={uploading}
                  disabled={uploading || loading}
                  aria-label={t("uploadBoundAttachment")}
                >
                  {uploading ? t("uploading") : t("addAttachment")}
                </Button>
                <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                  {t("filePolicy")}
                </p>
              </div>
            </div>
          ) : null}

          {!loading && !error && voidTargetId ? (
            <div
              className="space-y-3 rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface-sunken p-3"
              data-testid="bound-void-form"
            >
              <Input
                id="boundVoidReason"
                name="boundVoidReason"
                label={t("voidReason")}
                value={voidReason}
                onChange={(event) => setVoidReason(event.target.value)}
                disabled={voidingId !== null}
                hint={t("voidReasonHint")}
              />
              <div className="flex flex-wrap gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setVoidTargetId(null);
                    setVoidReason("");
                  }}
                  disabled={voidingId !== null}
                >
                  {t("cancel")}
                </Button>
                <Button
                  type="button"
                  onClick={() => void onConfirmVoid()}
                  loading={voidingId !== null}
                  disabled={voidingId !== null}
                  aria-label={t("confirmVoid")}
                >
                  {t("confirmVoid")}
                </Button>
              </div>
            </div>
          ) : null}

          {!loading && !error && visible.length === 0 ? (
            <div data-testid="bound-empty">
              <Empty
                title={t(cmBatch1AttachmentListLabel(0))}
                description={t("boundAttachmentsOptionalDescription")}
                primaryAction={
                  canUpload
                    ? {
                        label: t("addAttachment"),
                        onClick: () => inputRef.current?.click(),
                      }
                    : {
                        label: t("refreshList"),
                        onClick: () => void load(),
                      }
                }
              />
            </div>
          ) : null}

          {!loading && !error && visible.length > 0 ? (
            <>
              <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                {t(cmBatch1AttachmentListLabel(visible.length), {
                  count: visible.length,
                })}
              </p>
              <ul
                className="divide-y divide-ecmp-border rounded-[var(--ecmp-radius-md)] border border-ecmp-border"
                data-testid="bound-list"
                aria-label={t("boundAttachmentsAria")}
              >
                {visible.map((item) => (
                  <li
                    key={item.attachmentId}
                    className="flex flex-col gap-2 px-3 py-3 text-[length:var(--ecmp-font-body-size)] sm:flex-row sm:items-center sm:justify-between"
                    data-testid={`bound-item-${item.attachmentId}`}
                  >
                    <div className="min-w-0 space-y-1">
                      <span className="block truncate font-medium text-ecmp-text-primary">
                        {item.originalName}
                      </span>
                      <div className="flex flex-wrap items-center gap-2">
                        <Badge tone="neutral">{item.status}</Badge>
                        <Badge tone="info">{item.classification}</Badge>
                        <span className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                          {formatCmBatch1AttachmentBytes(item.sizeBytes)}
                        </span>
                      </div>
                    </div>
                    {canVoid && isCmBatch1AttachmentVoidable(item.status) ? (
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        disabled={voidingId !== null}
                        onClick={() => {
                          setVoidTargetId(item.attachmentId);
                          setVoidReason("");
                          setError(null);
                        }}
                        aria-label={t("voidNamed", { name: item.originalName })}
                      >
                        {t("void")}
                      </Button>
                    ) : null}
                  </li>
                ))}
              </ul>
            </>
          ) : null}
        </CardBody>
      </Card>
    </section>
  );
}
