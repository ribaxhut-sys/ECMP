"use client";

import { useCallback, useRef, useState, type ChangeEvent } from "react";
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
  Button,
  Card,
  CardBody,
  CardDescription,
  CardHeader,
  CardTitle,
  Input,
  Select,
} from "@/shared/ui";

const CLASSIFICATION_OPTIONS = [
  { value: "customer_evidence", label: "Customer evidence" },
  { value: "internal_evidence", label: "Internal evidence" },
  { value: "official_letter", label: "Official letter" },
] as const;

const ACCEPT_MIME =
  "application/pdf,image/jpeg,image/png,image/webp,video/mp4,text/plain,.pdf,.jpg,.jpeg,.png,.webp,.mp4,.txt";

export interface StagingAttachmentsPanelProps {
  stagingToken: string;
  disabled?: boolean;
  onStagingTokenResolved?: (token: string) => void;
}

/**
 * SCR-CM-004 — FR-004 staged upload + logical void for Aggregate create (API-507/512).
 */
export function StagingAttachmentsPanel({
  stagingToken,
  disabled = false,
  onStagingTokenResolved,
}: StagingAttachmentsPanelProps) {
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

  const onPick = useCallback(() => {
    inputRef.current?.click();
  }, []);

  const onFileChange = useCallback(
    async (event: ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      event.target.value = "";
      if (!file || !canUpload || disabled) return;

      setUploading(true);
      setError(null);
      try {
        const res = await uploadCmBatch1Attachment({
          file,
          classification,
          stagingToken,
        });
        const data = res.data;
        setItems((prev) => [data, ...prev]);
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
              : "Unable to upload attachment.",
        );
      } finally {
        setUploading(false);
      }
    },
    [
      canUpload,
      classification,
      disabled,
      onStagingTokenResolved,
      stagingToken,
    ],
  );

  const onConfirmVoid = useCallback(async () => {
    if (!voidTargetId || !canVoid || disabled) return;
    const reason = normalizeCmBatch1VoidReason(voidReason);
    if (!reason) {
      setError("Void reason is required (logical void, not delete).");
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
            : "Unable to void attachment.",
      );
    } finally {
      setVoidingId(null);
    }
  }, [canVoid, disabled, voidReason, voidTargetId]);

  const visible = items.filter((item) => item.status !== "VOID");

  if (!canUpload) {
    return (
      <Alert
        tone="info"
        title="Attachments unavailable"
        description="You need attachment:create to stage evidence on this create path."
      />
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Attachments (staged)</CardTitle>
        <CardDescription>
          SCR-CM-004 / FR-004 — upload evidence before commit. Void is logical
          (API-512 / BR-012), not physical delete. Dual SoT Aggregate path only.
        </CardDescription>
      </CardHeader>
      <CardBody className="space-y-4">
        {error ? (
          <Alert tone="danger" title="Attachment error" description={error} />
        ) : null}

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 md:items-end">
          <Select
            name="attachmentClassification"
            id="attachmentClassification"
            label="Classification"
            options={[...CLASSIFICATION_OPTIONS]}
            value={classification}
            onChange={(event) =>
              setClassification(
                event.target.value as CmBatch1AttachmentClassification,
              )
            }
            disabled={disabled || uploading}
          />
          <div className="flex flex-col gap-2">
            <input
              ref={inputRef}
              type="file"
              className="sr-only"
              accept={ACCEPT_MIME}
              disabled={disabled || uploading}
              onChange={(event) => void onFileChange(event)}
              aria-label="Choose file to stage"
            />
            <Button
              type="button"
              variant="outline"
              onClick={onPick}
              loading={uploading}
              disabled={disabled || uploading}
              aria-label="Upload staged attachment"
            >
              {uploading ? "Uploading…" : "Upload file"}
            </Button>
            <p className="text-xs text-ecmp-muted">
              PDF, JPEG, PNG, WebP, MP4, or plain text — max 10 MB (Batch-1
              policy).
            </p>
          </div>
        </div>

        {voidTargetId ? (
          <div
            className="space-y-3 rounded-md border border-ecmp-border p-3"
            data-testid="staging-void-form"
          >
            <Input
              id="stagingVoidReason"
              name="stagingVoidReason"
              label="Void reason"
              value={voidReason}
              onChange={(event) => setVoidReason(event.target.value)}
              disabled={disabled || voidingId !== null}
              hint="Required — BR-012 void-with-reason"
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
                Cancel
              </Button>
              <Button
                type="button"
                onClick={() => void onConfirmVoid()}
                loading={voidingId !== null}
                disabled={disabled || voidingId !== null}
                aria-label="Confirm void staged attachment"
              >
                Confirm void
              </Button>
            </div>
          </div>
        ) : null}

        {visible.length === 0 ? (
          <p className="text-sm text-ecmp-muted" data-testid="staging-empty">
            No staged attachments yet. Optional before create.
          </p>
        ) : (
          <ul
            className="divide-y divide-ecmp-border rounded-md border border-ecmp-border"
            data-testid="staging-list"
            aria-label="Staged attachments"
          >
            {visible.map((item) => (
              <li
                key={item.attachmentId}
                className="flex flex-col gap-2 px-3 py-2 text-sm sm:flex-row sm:items-center sm:justify-between"
                data-testid={`staging-item-${item.attachmentId}`}
              >
                <div className="min-w-0">
                  <span className="font-medium text-ecmp-fg truncate block">
                    {item.originalName}
                  </span>
                  <span className="text-xs text-ecmp-muted">
                    {item.status} · {item.classification} ·{" "}
                    {formatCmBatch1AttachmentBytes(item.sizeBytes)}
                  </span>
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
                    aria-label={`Void ${item.originalName}`}
                  >
                    Void
                  </Button>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </CardBody>
    </Card>
  );
}
