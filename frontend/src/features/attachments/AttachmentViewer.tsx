"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  ApiError,
  downloadAttachment,
  type Attachment,
} from "@/lib/api";
import {
  IconClose,
  IconDownload,
  IconExternalLink,
  IconSpinner,
  IconZoomIn,
  IconZoomOut,
} from "@/shared/icons";
import { Alert, Button } from "@/shared/ui";
import { getPreviewKind, type PreviewKind } from "./fileTypes";

function mapLoadError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 404) return "Attachment not found (404).";
    if (error.status === 403) return "You do not have permission to view this file (403).";
    if (error.status === 500) return "Server error while loading file (500).";
    return error.message || "Failed to load file.";
  }
  return "Failed to load file.";
}

export interface AttachmentViewerProps {
  attachment: Attachment;
  open: boolean;
  onClose: () => void;
}

/**
 * Lazy preview modal: downloads bytes only after open.
 * Images: zoom. PDF: browser iframe viewer. Unsupported: message + download.
 */
export function AttachmentViewer({
  attachment,
  open,
  onClose,
}: AttachmentViewerProps) {
  const kind: PreviewKind = getPreviewKind(
    attachment.mimeType,
    attachment.extension,
    attachment.originalName,
  );

  const [objectUrl, setObjectUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [zoom, setZoom] = useState(1);
  const urlRef = useRef<string | null>(null);

  const revoke = useCallback(() => {
    if (urlRef.current) {
      URL.revokeObjectURL(urlRef.current);
      urlRef.current = null;
    }
    setObjectUrl(null);
  }, []);

  const loadPreview = useCallback(async () => {
    if (kind === "unsupported") {
      setError("Preview not supported for this file type.");
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const result = await downloadAttachment(attachment.id);
      revoke();
      const url = URL.createObjectURL(result.blob);
      urlRef.current = url;
      setObjectUrl(url);
    } catch (err) {
      setError(mapLoadError(err));
    } finally {
      setLoading(false);
    }
  }, [attachment.id, kind, revoke]);

  useEffect(() => {
    if (!open) {
      revoke();
      setError(null);
      setLoading(false);
      setZoom(1);
      return;
    }
    void loadPreview();
    return () => {
      revoke();
    };
  }, [open, loadPreview, revoke]);

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

  const handleDownload = useCallback(async () => {
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
      setError(mapLoadError(err));
    }
  }, [attachment.originalName, attachment.id]);

  const handleOpenTab = useCallback(async () => {
    try {
      const result = await downloadAttachment(attachment.id);
      const url = URL.createObjectURL(result.blob);
      const opened = window.open(url, "_blank", "noopener,noreferrer");
      if (!opened) {
        URL.revokeObjectURL(url);
        setError("Popup blocked. Allow popups to open in a new tab.");
        return;
      }
      // Revoke after the new tab has a chance to load.
      window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch (err) {
      setError(mapLoadError(err));
    }
  }, [attachment.id]);

  if (!open || typeof document === "undefined") return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center p-0 sm:items-center sm:p-4"
      role="dialog"
      aria-modal="true"
      aria-label={`Preview ${attachment.originalName}`}
      data-testid="attachment-viewer"
    >
      <button
        type="button"
        aria-label="Close preview overlay"
        className="absolute inset-0 bg-ecmp-overlay"
        onClick={onClose}
      />
      <div className="relative z-10 flex h-[100dvh] w-full max-w-5xl flex-col overflow-hidden rounded-none border border-ecmp-border bg-ecmp-surface shadow-ecmp-lg sm:h-auto sm:max-h-[92vh] sm:rounded-[var(--ecmp-radius-xl)]">
        <header className="flex items-center justify-between gap-3 border-b border-ecmp-border px-3 py-3 sm:px-5">
          <div className="min-w-0">
            <h2 className="truncate text-[length:var(--ecmp-font-title-size)] font-semibold text-ecmp-text-primary">
              {attachment.originalName}
            </h2>
            <p className="truncate text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
              {attachment.mimeType}
            </p>
          </div>
          <div className="flex shrink-0 flex-wrap items-center justify-end gap-1">
            {kind === "image" ? (
              <>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  aria-label="Zoom out"
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
                  aria-label="Zoom in"
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
              onClick={() => void handleOpenTab()}
              leftIcon={<IconExternalLink />}
            >
              <span className="hidden sm:inline">New tab</span>
            </Button>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => void handleDownload()}
              leftIcon={<IconDownload />}
            >
              <span className="hidden sm:inline">Download</span>
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              aria-label="Close preview"
              onClick={onClose}
              className="!min-h-[44px] !min-w-[44px] px-0"
            >
              <IconClose />
            </Button>
          </div>
        </header>

        <div className="flex min-h-0 flex-1 flex-col overflow-auto bg-ecmp-secondary-muted/40 p-3 sm:p-5">
          {loading ? (
            <div className="flex flex-1 flex-col items-center justify-center gap-3 py-16 text-ecmp-text-secondary">
              <IconSpinner className="size-8" />
              <p>Loading preview…</p>
            </div>
          ) : null}

          {!loading && error ? (
            <div className="mx-auto w-full max-w-lg space-y-4 py-8">
              <Alert
                tone={error.includes("not supported") ? "warning" : "danger"}
                title={
                  error.includes("not supported")
                    ? "Preview not supported"
                    : "Preview failed"
                }
                description={error}
                actionLabel="Download file"
                onAction={() => void handleDownload()}
              />
            </div>
          ) : null}

          {!loading && !error && kind === "image" && objectUrl ? (
            <div className="flex min-h-[50vh] items-center justify-center overflow-auto">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={objectUrl}
                alt={attachment.originalName}
                className="max-h-none origin-center transition-transform duration-150"
                style={{ transform: `scale(${zoom})` }}
                data-testid="attachment-image-preview"
              />
            </div>
          ) : null}

          {!loading && !error && kind === "pdf" && objectUrl ? (
            <iframe
              title={`PDF preview — ${attachment.originalName}`}
              src={objectUrl}
              className="h-[70vh] w-full rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-white"
              data-testid="attachment-pdf-preview"
            />
          ) : null}
        </div>
      </div>
    </div>
  );
}
