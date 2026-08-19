"use client";

import { useCallback, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import {
  ApiError,
  downloadAttachment,
  type Attachment,
} from "@/lib/api";
import {
  IconDownload,
  IconExternalLink,
  IconEye,
  IconFile,
  IconImage,
} from "@/shared/icons";
import { Alert, Badge, Button, Card, CardBody } from "@/shared/ui";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { AttachmentViewer } from "./AttachmentViewer";
import {
  fileTypeLabel,
  formatFileSize,
  formatUploadDate,
  getPreviewKind,
} from "./fileTypes";

function TypeIcon({
  mimeType,
  extension,
  filename,
}: {
  mimeType: string;
  extension: string | null;
  filename: string;
}) {
  const kind = getPreviewKind(mimeType, extension, filename);
  if (kind === "image") return <IconImage className="size-8 text-ecmp-primary" />;
  if (kind === "pdf") return <IconFile className="size-8 text-ecmp-danger" />;
  if (kind === "docx") return <IconFile className="size-8 text-ecmp-info" />;
  return <IconFile className="size-8 text-ecmp-text-secondary" />;
}

export interface AttachmentCardProps {
  attachment: Attachment;
}

export function AttachmentCard({ attachment }: AttachmentCardProps) {
  const t = useTranslations("attachments");
  const tErrors = useTranslations("errors");
  const tCommon = useTranslations("common");
  const locale = useLocale();
  const kind = getPreviewKind(
    attachment.mimeType,
    attachment.extension,
    attachment.originalName,
  );
  const [viewerOpen, setViewerOpen] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const mapError = useCallback((error: unknown): string => {
    if (error instanceof ApiError) {
      if (error.status === 404) return t("notFound404");
      if (error.status === 403) return t("permissionDenied403");
      if (error.status === 500) return t("serverError500");
      return resolveApiErrorMessage(error, tErrors, tCommon);
    }
    return t("actionFailed");
  }, [t, tErrors, tCommon]);

  const handleDownload = useCallback(async () => {
    setBusy(true);
    setActionError(null);
    try {
      const result = await downloadAttachment(attachment.id);
      const url = URL.createObjectURL(result.blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = result.filename || attachment.originalName;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setActionError(mapError(err));
    } finally {
      setBusy(false);
    }
  }, [attachment.originalName, attachment.id, mapError]);

  const handleOpenTab = useCallback(async () => {
    setBusy(true);
    setActionError(null);
    try {
      const result = await downloadAttachment(attachment.id);
      const url = URL.createObjectURL(result.blob);
      const opened = window.open(url, "_blank", "noopener,noreferrer");
      if (!opened) {
        URL.revokeObjectURL(url);
        setActionError(t("popupBlocked"));
        return;
      }
      window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch (err) {
      setActionError(mapError(err));
    } finally {
      setBusy(false);
    }
  }, [attachment.id, mapError, t]);

  return (
    <>
      <Card data-testid={`attachment-card-${attachment.id}`}>
        <CardBody className="space-y-[var(--ecmp-panel-gap)]">
          <div className="flex items-start gap-[var(--ecmp-form-gap)]">
            <div className="flex size-12 shrink-0 items-center justify-center rounded-[var(--ecmp-radius-md)] bg-ecmp-surface-sunken">
              <TypeIcon
                mimeType={attachment.mimeType}
                extension={attachment.extension}
                filename={attachment.originalName}
              />
            </div>
            <div className="min-w-0 flex-1 space-y-2">
              <p className="truncate text-[length:var(--ecmp-font-card-title-size)] font-[number:var(--ecmp-font-card-title-weight)] text-ecmp-text-primary">
                {attachment.originalName}
              </p>
              <div className="flex flex-wrap items-center gap-2">
                <Badge tone="neutral">
                  {fileTypeLabel(
                    attachment.mimeType,
                    attachment.extension,
                    attachment.originalName,
                  )}
                </Badge>
                {kind === "unsupported" ? (
                  <Badge tone="warning">{t("noPreview")}</Badge>
                ) : (
                  <Badge tone="info">{t("previewable")}</Badge>
                )}
              </div>
            </div>
          </div>

          <dl className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] sm:grid-cols-3">
            <div className="min-w-0 space-y-1">
              <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                {t("fileSize")}
              </dt>
              <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                {formatFileSize(attachment.sizeBytes)}
              </dd>
            </div>
            <div className="min-w-0 space-y-1">
              <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                {t("fileType")}
              </dt>
              <dd className="break-all text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-primary">
                {attachment.mimeType}
              </dd>
            </div>
            <div className="min-w-0 space-y-1">
              <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                {t("uploadDate")}
              </dt>
              <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                {formatUploadDate(attachment.uploadedAt, locale)}
              </dd>
            </div>
          </dl>

          {actionError ? (
            <Alert tone="danger" title={t("actionFailed")} description={actionError} />
          ) : null}

          <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center">
            {kind !== "unsupported" ? (
              <Button
                type="button"
                variant="primary"
                size="sm"
                leftIcon={<IconEye />}
                onClick={() => setViewerOpen(true)}
                disabled={busy}
              >{t("preview")}              </Button>
            ) : (
              <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                {t("previewNotSupportedDescription")}
              </p>
            )}
            <Button
              type="button"
              variant="outline"
              size="sm"
              leftIcon={<IconDownload />}
              loading={busy}
              onClick={() => void handleDownload()}
            >{t("download")}            </Button>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              leftIcon={<IconExternalLink />}
              disabled={busy}
              onClick={() => void handleOpenTab()}
            >{t("openInNewTab")}            </Button>
          </div>
        </CardBody>
      </Card>

      <AttachmentViewer
        attachment={attachment}
        open={viewerOpen}
        onClose={() => setViewerOpen(false)}
      />
    </>
  );
}
