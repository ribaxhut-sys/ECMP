"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  fetchCmBatch1ComplaintAttachments,
  voidCmBatch1Attachment,
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
  Button,
  Card,
  CardBody,
  CardDescription,
  CardHeader,
  CardTitle,
  Input,
  Skeleton,
} from "@/shared/ui";

/**
 * Bound attachments on Aggregate confirmation (API-509 list + optional API-512 void).
 * Dual SoT: uses complaint id from `/api/v1/cm` create/confirmation path.
 */
export function CmBatch1BoundAttachmentsCard({
  complaintId,
  allowVoid = true,
}: {
  complaintId: string;
  allowVoid?: boolean;
}) {
  const t = useTranslations("complaints");
  const { hasPermission } = useAuth();
  const canRead =
    hasPermission("attachment:read") || hasPermission("*");
  const canVoid =
    allowVoid &&
    (hasPermission("attachment:delete") || hasPermission("*"));

  const [items, setItems] = useState<CmBatch1AttachmentResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
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
    <Card data-testid="cm-batch1-bound-attachments">
      <CardHeader>
        <CardTitle>{t("boundAttachments")}</CardTitle>
        <CardDescription>
          {t("boundAttachmentsDescription")}
        </CardDescription>
      </CardHeader>
      <CardBody className="space-y-4">
        {loading ? <Skeleton rows={3} /> : null}

        {!loading && error ? (
          <Alert
            tone="danger"
            title={t("couldNotLoadAttachments")}
            description={error}
          />
        ) : null}

        {!loading && !error && voidTargetId ? (
          <div
            className="space-y-3 rounded-md border border-ecmp-border p-3"
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
              >{t("cancel")}              </Button>
              <Button
                type="button"
                onClick={() => void onConfirmVoid()}
                loading={voidingId !== null}
                disabled={voidingId !== null}
                aria-label={t("confirmVoid")}
              >{t("confirmVoid")}              </Button>
            </div>
          </div>
        ) : null}

        {!loading && !error && visible.length === 0 ? (
          <p className="text-sm text-ecmp-muted" data-testid="bound-empty">
            {t(cmBatch1AttachmentListLabel(0))}
          </p>
        ) : null}

        {!loading && !error && visible.length > 0 ? (
          <>
            <p className="text-sm text-ecmp-muted">
              {t(cmBatch1AttachmentListLabel(visible.length), { count: visible.length })}
            </p>
            <ul
              className="divide-y divide-ecmp-border rounded-md border border-ecmp-border"
              data-testid="bound-list"
              aria-label={t("boundAttachmentsAria")}
            >
              {visible.map((item) => (
                <li
                  key={item.attachmentId}
                  className="flex flex-col gap-2 px-3 py-2 text-sm sm:flex-row sm:items-center sm:justify-between"
                  data-testid={`bound-item-${item.attachmentId}`}
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
  );
}
