"use client";

import { useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import { IconSpinner } from "@/shared/icons";
import { Alert } from "@/shared/ui";

export interface DocxPreviewProps {
  /** Downloaded .docx bytes; null while the caller is still fetching. */
  blob: Blob | null;
  /** Optional download fallback offered when rendering fails. */
  onDownload?: () => void;
  className?: string;
  /** Page scale factor (shared zoom controls); 1 = natural size. */
  zoom?: number;
}

/**
 * Client-side .docx renderer (docx-preview). The library chunk is imported
 * lazily so it only ships to browsers that actually open a Word file.
 *
 * Legacy binary .doc is NOT handled here — `getPreviewKind` keeps it
 * "unsupported" (download only).
 */
export function DocxPreview({ blob, onDownload, className, zoom = 1 }: DocxPreviewProps) {
  const t = useTranslations("attachments");
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [rendering, setRendering] = useState(true);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    const container = containerRef.current;
    if (!container || !blob) return;
    let cancelled = false;
    setRendering(true);
    setFailed(false);
    void (async () => {
      try {
        const { renderAsync } = await import("docx-preview");
        if (cancelled) return;
        container.innerHTML = "";
        await renderAsync(blob, container, undefined, {
          className: "ecmp-docx",
          inWrapper: true,
          breakPages: true,
          renderHeaders: true,
          renderFooters: true,
          // Files come from external reporters: never render embedded HTML
          // chunks, tracked changes, or comment payloads.
          renderAltChunks: false,
          renderChanges: false,
          renderComments: false,
        });
        if (cancelled) return;
        setRendering(false);
      } catch {
        if (cancelled) return;
        container.innerHTML = "";
        setFailed(true);
        setRendering(false);
      }
    })();
    return () => {
      cancelled = true;
      container.innerHTML = "";
    };
  }, [blob]);

  return (
    <div className={className} data-testid="attachment-docx-preview">
      {rendering && !failed ? (
        <div className="flex items-center justify-center gap-2 py-16 text-ecmp-text-secondary">
          <IconSpinner className="size-6" />
          <span>{t("loadingPreview")}</span>
        </div>
      ) : null}

      {failed ? (
        <div className="mx-auto w-full max-w-lg py-8">
          <Alert
            tone="warning"
            title={t("previewFailed")}
            description={t("docxRenderFailed")}
            actionLabel={onDownload ? t("downloadFile") : undefined}
            onAction={onDownload}
          />
        </div>
      ) : null}

      {/* docx-preview writes into this node (and its scoped <style>). Scale
          from the top so zooming in keeps the page you're reading in place
          instead of re-centering the whole document. */}
      <div
        ref={containerRef}
        className={
          rendering || failed
            ? "hidden"
            : "w-full origin-top overflow-x-auto transition-transform duration-[var(--ecmp-duration-fast)]"
        }
        style={{ transform: `scale(${zoom})` }}
      />
    </div>
  );
}
