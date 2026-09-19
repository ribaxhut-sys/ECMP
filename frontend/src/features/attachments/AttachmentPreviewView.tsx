"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useLocale, useTranslations } from "next-intl";
import { fetchAttachment, type Attachment } from "@/lib/api";
import { IconDownload, IconSpinner, IconZoomIn, IconZoomOut } from "@/shared/icons";
import {
  Badge,
  Button,
  Card,
  CardBody,
  ErrorState,
  PageContainer,
  PageHeader,
} from "@/shared/ui";
import { AttachmentPreviewBody } from "./AttachmentPreviewBody";
import { normalizeAttachmentMeta } from "./attachmentMeta";
import { fileTypeLabel, formatFileSize, formatUploadDate } from "./fileTypes";
import { mapPreviewError, useAttachmentPreview } from "./useAttachmentPreview";

/**
 * Standalone preview page ("Open in new tab" target).
 *
 * A real route rather than a `blob:` URL: Word files render instead of
 * downloading, and the tab survives a refresh or being shared with a colleague.
 * Auth is unchanged — a cold tab starts without an access token, gets a 401,
 * and the API client swaps the refresh cookie for a fresh token.
 */
export function AttachmentPreviewView({ id }: { id: string }) {
  const t = useTranslations("attachments");
  const tErrors = useTranslations("errors");
  const tCommon = useTranslations("common");
  const locale = useLocale();

  const [attachment, setAttachment] = useState<Attachment | null>(null);
  const [metaLoading, setMetaLoading] = useState(true);
  const [metaError, setMetaError] = useState<string | null>(null);
  const [zoom, setZoom] = useState(1);

  const loadMeta = useCallback(async () => {
    setMetaLoading(true);
    setMetaError(null);
    try {
      const body = await fetchAttachment(id);
      const meta = normalizeAttachmentMeta(body.data);
      setAttachment(meta);
      if (!meta) setMetaError(t("failedToLoadFile"));
    } catch (err) {
      setAttachment(null);
      setMetaError(mapPreviewError(err, t, tErrors, tCommon));
    } finally {
      setMetaLoading(false);
    }
  }, [id, t, tErrors, tCommon]);

  useEffect(() => {
    void loadMeta();
  }, [loadMeta]);

  // Every route in this app shares one static browser-tab title (root
  // layout metadata) — fine for in-app navigation, but this page is opened
  // as its own tab (often several at once), so it needs the file name to
  // be tellable apart in the tab strip. Restore the app name on unmount so
  // a tab that later navigates elsewhere doesn't keep a stale file title.
  useEffect(() => {
    if (!attachment) return;
    const previousTitle = document.title;
    document.title = attachment.originalName;
    return () => {
      document.title = previousTitle;
    };
  }, [attachment]);

  const state = useAttachmentPreview(attachment, attachment !== null);
  const { kind, download } = state;

  if (metaLoading) {
    return (
      <PageContainer>
        <div className="flex items-center justify-center gap-[var(--ecmp-form-gap)] py-24 text-ecmp-text-secondary">
          <IconSpinner className="size-8" />
          <p>{t("loadingPreview")}</p>
        </div>
      </PageContainer>
    );
  }

  if (metaError || !attachment) {
    return (
      <PageContainer>
        <ErrorState
          title={t("couldNotLoad")}
          message={metaError ?? t("failedToLoadFile")}
          actionLabel={t("retry")}
          onRetry={() => void loadMeta()}
          secondaryAction={
            <Link href="/attachments">
              <Button type="button" variant="ghost" size="sm">
                {t("title")}
              </Button>
            </Link>
          }
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageHeader
        title={attachment.originalName}
        description={attachment.mimeType}
        breadcrumbs={[
          { label: t("home"), href: "/" },
          { label: t("title"), href: "/attachments" },
          { label: t("preview") },
        ]}
        meta={
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone="neutral">
              {fileTypeLabel(
                attachment.mimeType,
                attachment.extension,
                attachment.originalName,
              )}
            </Badge>
            <span className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
              {formatFileSize(attachment.sizeBytes)}
            </span>
            <span className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
              {formatUploadDate(attachment.uploadedAt, locale)}
            </span>
          </div>
        }
        actions={
          <div className="flex flex-wrap items-center gap-1">
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
              leftIcon={<IconDownload />}
              onClick={() => void download()}
            >
              {t("download")}
            </Button>
          </div>
        }
      />

      <Card>
        <CardBody>
          <AttachmentPreviewBody
            attachment={attachment}
            state={state}
            zoom={zoom}
            className="flex min-h-[50vh] flex-col overflow-auto"
          />
        </CardBody>
      </Card>
    </PageContainer>
  );
}
