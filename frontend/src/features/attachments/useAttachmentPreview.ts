"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import { ApiError, downloadAttachment, type Attachment } from "@/lib/api";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { getPreviewKind, type PreviewKind } from "./fileTypes";

type Translator = ReturnType<typeof useTranslations>;

/** Shared 404/403/500 wording for both the modal and the preview page. */
export function mapPreviewError(
  error: unknown,
  t: Translator,
  tErrors: Translator,
  tCommon: Translator,
): string {
  if (error instanceof ApiError) {
    if (error.status === 404) return t("notFound404");
    if (error.status === 403) return t("noPermissionToViewFile403");
    if (error.status === 500) return t("serverErrorLoadingFile500");
    return (
      resolveApiErrorMessage(error, tErrors, tCommon, "unexpectedError") ||
      t("failedToLoadFile")
    );
  }
  return t("failedToLoadFile");
}

export interface AttachmentPreviewState {
  kind: PreviewKind;
  loading: boolean;
  error: string | null;
  /** Images and PDFs render from an object URL; docx renders from the blob. */
  objectUrl: string | null;
  docxBlob: Blob | null;
  /** Save the file to disk (re-fetches; bytes are never cached in state). */
  download: () => Promise<void>;
}

/**
 * Fetches attachment bytes once `enabled` turns true and keeps the object URL
 * alive for exactly as long as the preview is on screen.
 */
export function useAttachmentPreview(
  attachment: Attachment | null,
  enabled: boolean,
): AttachmentPreviewState {
  const t = useTranslations("attachments");
  const tErrors = useTranslations("errors");
  const tCommon = useTranslations("common");

  const kind: PreviewKind = attachment
    ? getPreviewKind(
        attachment.mimeType,
        attachment.extension,
        attachment.originalName,
      )
    : "unsupported";

  const [objectUrl, setObjectUrl] = useState<string | null>(null);
  const [docxBlob, setDocxBlob] = useState<Blob | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const urlRef = useRef<string | null>(null);

  const revoke = useCallback(() => {
    if (urlRef.current) {
      URL.revokeObjectURL(urlRef.current);
      urlRef.current = null;
    }
    setObjectUrl(null);
    setDocxBlob(null);
  }, []);

  const attachmentId = attachment?.id ?? null;

  const loadPreview = useCallback(async () => {
    if (!attachmentId) return;
    if (kind === "unsupported") {
      setError(t("previewNotSupportedDescription"));
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const result = await downloadAttachment(attachmentId);
      revoke();
      if (kind === "docx") {
        // DocxPreview owns the render pass (and its own spinner) from here.
        setDocxBlob(result.blob);
        setLoading(false);
        return;
      }
      const url = URL.createObjectURL(result.blob);
      urlRef.current = url;
      setObjectUrl(url);
      setLoading(false);
    } catch (err) {
      setError(mapPreviewError(err, t, tErrors, tCommon));
      setLoading(false);
    }
  }, [attachmentId, kind, revoke, t, tErrors, tCommon]);

  useEffect(() => {
    if (!enabled || !attachmentId) {
      revoke();
      setError(null);
      setLoading(false);
      return;
    }
    void loadPreview();
    return () => {
      revoke();
    };
  }, [enabled, attachmentId, loadPreview, revoke]);

  const download = useCallback(async () => {
    if (!attachment) return;
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
      setError(mapPreviewError(err, t, tErrors, tCommon));
    }
  }, [attachment, t, tErrors, tCommon]);

  return { kind, loading, error, objectUrl, docxBlob, download };
}
