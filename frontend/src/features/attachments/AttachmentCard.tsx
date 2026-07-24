"use client";

import { useCallback, useState } from "react";
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
  return <IconFile className="size-8 text-ecmp-text-secondary" />;
}

export interface AttachmentCardProps {
  attachment: Attachment;
}

export function AttachmentCard({ attachment }: AttachmentCardProps) {
  const kind = getPreviewKind(
    attachment.mimeType,
    attachment.extension,
    attachment.filename,
  );
  const [viewerOpen, setViewerOpen] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const mapError = (error: unknown): string => {
    if (error instanceof ApiError) {
      if (error.status === 404) return "Attachment not found (404).";
      if (error.status === 403) return "Permission denied (403).";
      if (error.status === 500) return "Server error (500).";
      return error.message;
    }
    return "Action failed.";
  };

  const handleDownload = useCallback(async () => {
    setBusy(true);
    setActionError(null);
    try {
      const result = await downloadAttachment(attachment.id);
      const url = URL.createObjectURL(result.blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = result.filename || attachment.filename;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setActionError(mapError(err));
    } finally {
      setBusy(false);
    }
  }, [attachment.filename, attachment.id]);

  const handleOpenTab = useCallback(async () => {
    setBusy(true);
    setActionError(null);
    try {
      const result = await downloadAttachment(attachment.id);
      const url = URL.createObjectURL(result.blob);
      const opened = window.open(url, "_blank", "noopener,noreferrer");
      if (!opened) {
        URL.revokeObjectURL(url);
        setActionError("Popup blocked. Allow popups to open in a new tab.");
        return;
      }
      window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch (err) {
      setActionError(mapError(err));
    } finally {
      setBusy(false);
    }
  }, [attachment.id]);

  return (
    <>
      <Card data-testid={`attachment-card-${attachment.id}`}>
        <CardBody className="space-y-4">
          <div className="flex items-start gap-3">
            <div className="flex size-12 shrink-0 items-center justify-center rounded-[var(--ecmp-radius-md)] bg-ecmp-secondary-muted">
              <TypeIcon
                mimeType={attachment.mimeType}
                extension={attachment.extension}
                filename={attachment.filename}
              />
            </div>
            <div className="min-w-0 flex-1 space-y-1">
              <p className="truncate text-[length:var(--ecmp-font-subtitle-size)] font-semibold text-ecmp-text-primary">
                {attachment.filename}
              </p>
              <div className="flex flex-wrap items-center gap-2">
                <Badge tone="neutral">
                  {fileTypeLabel(
                    attachment.mimeType,
                    attachment.extension,
                    attachment.filename,
                  )}
                </Badge>
                {kind === "unsupported" ? (
                  <Badge tone="warning">No preview</Badge>
                ) : (
                  <Badge tone="info">Previewable</Badge>
                )}
              </div>
            </div>
          </div>

          <dl className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div className="min-w-0 space-y-1">
              <dt className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary">
                File size
              </dt>
              <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                {formatFileSize(attachment.sizeBytes)}
              </dd>
            </div>
            <div className="min-w-0 space-y-1">
              <dt className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary">
                MIME type
              </dt>
              <dd className="break-all text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                {attachment.mimeType}
              </dd>
            </div>
            <div className="min-w-0 space-y-1">
              <dt className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary">
                Upload date
              </dt>
              <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                {formatUploadDate(attachment.createdAt)}
              </dd>
            </div>
          </dl>

          {actionError ? (
            <Alert tone="danger" title="Action failed" description={actionError} />
          ) : null}

          <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap">
            {kind !== "unsupported" ? (
              <Button
                type="button"
                variant="primary"
                size="sm"
                leftIcon={<IconEye />}
                onClick={() => setViewerOpen(true)}
                disabled={busy}
              >
                Preview
              </Button>
            ) : (
              <Button type="button" variant="outline" size="sm" disabled>
                Preview not supported
              </Button>
            )}
            <Button
              type="button"
              variant="outline"
              size="sm"
              leftIcon={<IconDownload />}
              loading={busy}
              onClick={() => void handleDownload()}
            >
              Download
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              leftIcon={<IconExternalLink />}
              disabled={busy}
              onClick={() => void handleOpenTab()}
            >
              Open in new tab
            </Button>
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
