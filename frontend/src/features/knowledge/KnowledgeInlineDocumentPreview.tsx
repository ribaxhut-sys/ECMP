"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import {
  ApiError,
  downloadAttachment,
  type Attachment,
} from "@/lib/api";
import type { KnowledgeFile } from "@/lib/api/types";
import { getPreviewKind, type PreviewKind } from "@/features/attachments/fileTypes";
import { Alert, Button } from "@/shared/ui";
import { IconDownload, IconSpinner } from "@/shared/icons";
import { toViewerAttachment } from "./KnowledgeFileManager";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";

/**
 * Inline document preview for Knowledge detail (content-first).
 * PDF → iframe; image → img; other → download prompt.
 */
export function KnowledgeInlineDocumentPreview({
  file,
  knowledgeId,
}: {
  file: KnowledgeFile;
  knowledgeId: string;
}) {
  const t = useTranslations("attachments");
  const tKnowledge = useTranslations("knowledge");
  const tErrors = useTranslations("errors");
  const tCommon = useTranslations("common");
  const attachment: Attachment = toViewerAttachment(file, knowledgeId);
  const kind: PreviewKind = getPreviewKind(
    attachment.mimeType,
    attachment.extension,
    attachment.originalName,
  );

  const [objectUrl, setObjectUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const urlRef = useRef<string | null>(null);

  const revoke = useCallback(() => {
    if (urlRef.current) {
      URL.revokeObjectURL(urlRef.current);
      urlRef.current = null;
    }
    setObjectUrl(null);
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      revoke();
      setError(null);
      if (kind === "unsupported") {
        setLoading(false);
        setError(t("previewNotSupportedDescription"));
        return;
      }
      setLoading(true);
      try {
        const result = await downloadAttachment(attachment.id);
        if (cancelled) return;
        const url = URL.createObjectURL(result.blob);
        urlRef.current = url;
        setObjectUrl(url);
      } catch (err) {
        if (cancelled) return;
        if (err instanceof ApiError) {
          setError(resolveApiErrorMessage(err, tErrors, tCommon, "unexpectedError") || t("failedToLoadFile"));
        } else {
          setError(t("failedToLoadFile"));
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void load();
    return () => {
      cancelled = true;
      revoke();
    };
  }, [attachment.id, kind, revoke, t, tErrors, tCommon]);

  async function onDownload() {
    try {
      const result = await downloadAttachment(attachment.id);
      const url = URL.createObjectURL(result.blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = attachment.originalName || file.fileName;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      setError(t("failedToLoadFile"));
    }
  }

  return (
    <div
      className="overflow-hidden rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface"
      data-testid="knowledge-inline-preview"
    >
      <div className="flex items-center justify-between gap-2 border-b border-ecmp-border px-3 py-2">
        <p className="min-w-0 truncate text-[length:var(--ecmp-font-body-small-size)] font-medium text-ecmp-text-primary">
          {file.fileName}
        </p>
        <Button type="button" size="sm" variant="outline" onClick={() => void onDownload()}>
          <IconDownload className="size-4" aria-hidden />
          <span className="sr-only">{t("download")}</span>
        </Button>
      </div>
      <div className="relative min-h-[280px] bg-ecmp-canvas">
        {loading ? (
          <div className="flex min-h-[280px] items-center justify-center gap-2 text-ecmp-text-secondary">
            <IconSpinner className="size-5 animate-spin" aria-hidden />
            <span className="text-[length:var(--ecmp-font-body-small-size)]">
              {tKnowledge("documentLoading")}
            </span>
          </div>
        ) : null}
        {!loading && error ? (
          <div className="space-y-3 p-4">
            <Alert tone="warning" title={tKnowledge("documentPreviewUnavailable")} description={error} />
            <Button type="button" size="sm" variant="secondary" onClick={() => void onDownload()}>
              {t("download")}
            </Button>
          </div>
        ) : null}
        {!loading && !error && kind === "pdf" && objectUrl ? (
          <iframe
            title={file.fileName}
            src={objectUrl}
            className="h-[min(70vh,720px)] w-full border-0"
          />
        ) : null}
        {!loading && !error && kind === "image" && objectUrl ? (
          <div className="flex max-h-[min(70vh,720px)] items-center justify-center overflow-auto p-4">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={objectUrl}
              alt={file.fileName}
              className="max-h-[min(70vh,720px)] max-w-full object-contain"
            />
          </div>
        ) : null}
      </div>
    </div>
  );
}
