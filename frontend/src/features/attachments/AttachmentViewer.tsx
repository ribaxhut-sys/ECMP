"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import type { Attachment } from "@/lib/api";
import {
  IconClose,
  IconDownload,
  IconExternalLink,
  IconZoomIn,
  IconZoomOut,
} from "@/shared/icons";
import { Button } from "@/shared/ui";
import { AttachmentPreviewBody } from "./AttachmentPreviewBody";
import { attachmentPreviewPath } from "./previewRoutes";
import { useAttachmentPreview } from "./useAttachmentPreview";

export interface AttachmentViewerProps {
  attachment: Attachment;
  open: boolean;
  onClose: () => void;
}

/**
 * Lazy preview modal: downloads bytes only after open.
 * Images and DOCX: zoom. PDF: browser iframe viewer (has its own zoom).
 * Unsupported: message + download.
 */
export function AttachmentViewer({
  attachment,
  open,
  onClose,
}: AttachmentViewerProps) {
  const t = useTranslations("attachments");
  const state = useAttachmentPreview(attachment, open);
  const { kind, download } = state;
  const [zoom, setZoom] = useState(1);

  useEffect(() => {
    if (!open) setZoom(1);
  }, [open]);

  useEffect(() => {
    if (!open) return;
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    document.addEventListener("keydown", onKeyDown);
    const previous = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = previous;
    };
  }, [open, onClose]);

  // Opens the in-app preview route, not a blob: URL — synchronous, so popup
  // blockers see a direct user gesture, and the tab can be refreshed/shared.
  const handleOpenTab = useCallback(() => {
    window.open(
      attachmentPreviewPath(attachment.id),
      "_blank",
      "noopener,noreferrer",
    );
  }, [attachment.id]);

  if (!open || typeof document === "undefined") return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center p-0 sm:items-center sm:p-[var(--ecmp-panel-gap)]"
      role="dialog"
      aria-modal="true"
      aria-label={t("previewAriaLabel", { name: attachment.originalName })}
      data-testid="attachment-viewer"
    >
      <button
        type="button"
        aria-label={t("closePreviewOverlay")}
        className="absolute inset-0 bg-ecmp-overlay"
        onClick={onClose}
      />
      <div className="relative z-10 flex h-[100dvh] w-full max-w-5xl flex-col overflow-hidden rounded-none border border-ecmp-border bg-ecmp-surface shadow-ecmp-lg sm:h-auto sm:max-h-[92vh] sm:rounded-[var(--ecmp-radius-xl)]">
        <header className="flex items-center justify-between gap-[var(--ecmp-form-gap)] border-b border-ecmp-border px-3 py-3 sm:px-5">
          <div className="min-w-0">
            <h2 className="truncate text-[length:var(--ecmp-font-title-size)] font-[number:var(--ecmp-font-section-title-weight)] text-ecmp-text-primary">
              {attachment.originalName}
            </h2>
            <p className="truncate text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
              {attachment.mimeType}
            </p>
          </div>
          <div className="flex shrink-0 flex-wrap items-center justify-end gap-1">
            {kind === "image" || kind === "docx" ? (
              <>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  aria-label={t("zoomOut")}
                  onClick={() => setZoom((z) => Math.max(0.5, Number((z - 0.25).toFixed(2))))}
                  className="!min-h-[44px] !min-w-[44px] px-0"
                >
                  <IconZoomOut />
                </Button>
                <span className="min-w-[3.5rem] text-center text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
                  {Math.round(zoom * 100)}%
                </span>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  aria-label={t("zoomIn")}
                  onClick={() => setZoom((z) => Math.min(3, Number((z + 0.25).toFixed(2))))}
                  className="!min-h-[44px] !min-w-[44px] px-0"
                >
                  <IconZoomIn />
                </Button>
              </>
            ) : null}
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={handleOpenTab}
              leftIcon={<IconExternalLink />}
            >
              <span className="hidden sm:inline">{t("newTab")}</span>
            </Button>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => void download()}
              leftIcon={<IconDownload />}
            >
              <span className="hidden sm:inline">{t("download")}</span>
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              aria-label={t("closePreview")}
              onClick={onClose}
              className="!min-h-[44px] !min-w-[44px] px-0"
            >
              <IconClose />
            </Button>
          </div>
        </header>

        <AttachmentPreviewBody
          attachment={attachment}
          state={state}
          zoom={zoom}
          className="flex min-h-0 flex-1 flex-col overflow-auto bg-ecmp-secondary-muted/40 p-3 sm:p-5"
        />
      </div>
    </div>
  );
}
