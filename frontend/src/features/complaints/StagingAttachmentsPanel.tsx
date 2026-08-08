"use client";

import { useCallback, useEffect, useRef, useState, type ChangeEvent } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  uploadCmBatch1Attachment,
  voidCmBatch1Attachment,
  type CmBatch1AttachmentClassification,
  type CmBatch1AttachmentResponse,
} from "@/lib/api";
import {
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
} from "@/shared/ui";

const CLASSIFICATION_OPTIONS = [
  { value: "customer_evidence", label: "classificationCustomerEvidence" },
  { value: "internal_evidence", label: "classificationInternalEvidence" },
  { value: "official_letter", label: "classificationOfficialLetter" },
] as const;

const ACCEPT_MIME =
  "application/pdf,image/jpeg,image/png,image/webp,video/mp4,text/plain,.pdf,.jpg,.jpeg,.png,.webp,.mp4,.txt";

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
  const { hasPermission } = useAuth();
  const canUpload =
    hasPermission("attachment:create") || hasPermission("*");
  const canVoid =
    hasPermission("attachment:delete") || hasPermission("*");
  const inputRef = useRef<HTMLInputElement>(null);

  const [classification, setClassification] =
    useState<CmBatch1AttachmentClassification>("customer_evidence");
  const [items, setItems] = useState<CmBatch1AttachmentResponse[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [voidingId, setVoidingId] = useState<string | null>(null);
  const [voidReason, setVoidReason] = useState("");
  const [voidTargetId, setVoidTargetId] = useState<string | null>(null);

  const customerLocked = Boolean(customerId?.trim());
  const uploadBlocked = disabled || !customerLocked;

  useEffect(() => {
    onBusyChange?.(uploading || Boolean(voidingId));
  }, [onBusyChange, uploading, voidingId]);

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
      const file = event.target.files?.[0];
      event.target.value = "";
      if (!file || !canUpload || uploadBlocked) return;
      const lockedCustomerId = customerId?.trim();
      if (!lockedCustomerId) {
        setError(t("attachAfterCustomerConfirm"));
        return;
      }

      setUploading(true);
      setError(null);
      try {
        const res = await uploadCmBatch1Attachment({
          file,
          classification,
          stagingToken,
          customerId: lockedCustomerId,
        });
        const data = res.data;
        setItems((prev) => {
          const next = [data, ...prev];
          notifyStaged(next);
          return next;
        });
        const resolved = data.stagingToken?.trim() || stagingToken;
        if (resolved && resolved !== stagingToken) {
          onStagingTokenResolved?.(resolved);
        }
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
    [
      canUpload,
      classification,
      customerId,
      notifyStaged,
      onStagingTokenResolved,
      stagingToken,
      t,
      uploadBlocked,
    ],
  );

  const onConfirmVoid = useCallback(async () => {
    if (!voidTargetId || !canVoid || disabled) return;
    const reason = normalizeCmBatch1VoidReason(voidReason);
    if (!reason) {
      setError(t("voidReasonRequired"));
      return;
    }
    setVoidingId(voidTargetId);
    setError(null);
    try {
      const res = await voidCmBatch1Attachment(voidTargetId, reason);
      setItems((prev) => {
        const next = prev.map((item) =>
          item.attachmentId === voidTargetId ? res.data : item,
        );
        notifyStaged(next);
        return next;
      });
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
  }, [canVoid, disabled, notifyStaged, voidReason, voidTargetId, t]);

  const visible = items.filter((item) => item.status !== "VOID");

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
    <section className="space-y-[var(--ecmp-panel-gap)]">
      <SectionHeader
        title={t("stagedAttachments")}
        description={t("stagedAttachmentsDescription")}
      />
      <Card>
        <CardBody className="space-y-[var(--ecmp-panel-gap)]">
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

          <div className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] md:grid-cols-2 md:items-end">
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
            <div className="flex flex-col gap-2">
              <input
                ref={inputRef}
                type="file"
                className="sr-only"
                accept={ACCEPT_MIME}
                disabled={uploadBlocked || uploading}
                onChange={(event) => void onFileChange(event)}
                aria-label={t("chooseFile")}
              />
              <Button
                type="button"
                variant="outline"
                onClick={onPick}
                loading={uploading}
                disabled={uploadBlocked || uploading}
                aria-label={t("uploadStagedAttachment")}
              >
                {uploading ? t("uploading") : t("uploadFile")}
              </Button>
              <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                {t("filePolicy")}
              </p>
            </div>
          </div>

          {voidTargetId ? (
            <div
              className="space-y-[var(--ecmp-form-gap)] rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface-sunken p-3"
              data-testid="staging-void-form"
            >
              <Input
                id="stagingVoidReason"
                name="stagingVoidReason"
                label={t("voidReason")}
                value={voidReason}
                onChange={(event) => setVoidReason(event.target.value)}
                disabled={disabled || voidingId !== null}
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
                  disabled={disabled || voidingId !== null}
                  aria-label={t("confirmVoid")}
                >
                  {t("confirmVoid")}
                </Button>
              </div>
            </div>
          ) : null}

          {visible.length === 0 ? (
            <div data-testid="staging-empty">
              <Empty
                title={t("noStagedAttachments")}
                description={t("stagedAttachmentsDescription")}
                primaryAction={{
                  label: t("uploadFile"),
                  onClick: onPick,
                  disabled: disabled || uploading || !canUpload,
                }}
              />
            </div>
          ) : (
            <ul
              className="divide-y divide-ecmp-border rounded-[var(--ecmp-radius-md)] border border-ecmp-border"
              data-testid="staging-list"
              aria-label={t("stagedAttachmentsAria")}
            >
              {visible.map((item) => (
                <li
                  key={item.attachmentId}
                  className="flex flex-col gap-2 px-3 py-3 text-[length:var(--ecmp-font-body-size)] sm:flex-row sm:items-center sm:justify-between"
                  data-testid={`staging-item-${item.attachmentId}`}
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
                      disabled={disabled || voidingId !== null}
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
          )}
        </CardBody>
      </Card>
    </section>
  );
}
