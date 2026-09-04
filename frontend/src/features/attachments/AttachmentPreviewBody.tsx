"use client";

import { useTranslations } from "next-intl";
import type { Attachment } from "@/lib/api";
import { IconSpinner } from "@/shared/icons";
import { Alert } from "@/shared/ui";
import { DocxPreview } from "./DocxPreview";
import type { AttachmentPreviewState } from "./useAttachmentPreview";

export interface AttachmentPreviewBodyProps {
  attachment: Attachment;
  state: AttachmentPreviewState;
  /** Image scale factor (modal zoom controls); 1 = natural size. */
  zoom?: number;
  className?: string;
}

/**
 * Renders the preview surface for one attachment — shared by the modal viewer
 * and the standalone preview page so both stay in step.
 */
export function AttachmentPreviewBody({
  attachment,
  state,
  zoom = 1,
  className,
}: AttachmentPreviewBodyProps) {
  const t = useTranslations("attachments");
  const { kind, loading, error, objectUrl, docxBlob, download } = state;

  return (
    <div className={className}>
      {loading ? (
        <div className="flex flex-1 flex-col items-center justify-center gap-[var(--ecmp-form-gap)] py-16 text-ecmp-text-secondary">
          <IconSpinner className="size-8" />
          <p>{t("loadingPreview")}</p>
        </div>
      ) : null}

      {!loading && error ? (
        <div className="mx-auto w-full max-w-lg space-y-[var(--ecmp-panel-gap)] py-8">
          <Alert
            tone={kind === "unsupported" ? "warning" : "danger"}
            title={
              kind === "unsupported"
                ? t("previewNotSupported")
                : t("previewFailed")
            }
            description={error}
            actionLabel={t("downloadFile")}
            onAction={() => void download()}
          />
        </div>
      ) : null}

      {!loading && !error && kind === "image" && objectUrl ? (
        <div className="flex min-h-[50vh] items-center justify-center overflow-auto">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={objectUrl}
            alt={attachment.originalName}
            className="max-h-none origin-center transition-transform duration-[var(--ecmp-duration-fast)]"
            style={{ transform: `scale(${zoom})` }}
            data-testid="attachment-image-preview"
          />
        </div>
      ) : null}

      {!loading && !error && kind === "pdf" && objectUrl ? (
        <iframe
          title={t("pdfPreviewTitle", { name: attachment.originalName })}
          src={objectUrl}
          className="h-[70vh] w-full rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface"
          data-testid="attachment-pdf-preview"
        />
      ) : null}

      {!loading && !error && kind === "docx" && docxBlob ? (
        <DocxPreview
          blob={docxBlob}
          onDownload={() => void download()}
          className="w-full"
          zoom={zoom}
        />
      ) : null}
    </div>
  );
}
