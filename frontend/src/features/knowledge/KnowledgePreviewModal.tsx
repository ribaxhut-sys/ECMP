"use client";

import { useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { fetchKnowledge } from "@/lib/api";
import type { Knowledge } from "@/lib/api/types";
import { formatDateTime } from "@/i18n/formatting";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { ErrorState, Modal, Skeleton } from "@/shared/ui";
import { IconExternalLink, IconFile } from "@/shared/icons";
import { formatFileSize, fileTypeLabel } from "@/features/attachments/fileTypes";
import { AttachmentViewer } from "@/features/attachments/AttachmentViewer";
import { KnowledgeStatusBadge, KnowledgeTypeBadge } from "./KnowledgeBadges";
import { toViewerAttachment } from "./KnowledgeFileManager";

function PreviewField({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0 space-y-1">
      <dt className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
        {label}
      </dt>
      <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
        {value}
      </dd>
    </div>
  );
}

function PreviewFileRow({
  fileName,
  sizeBytes,
  mimeType,
  onPreview,
}: {
  fileName: string;
  sizeBytes: number;
  mimeType: string | null;
  onPreview: () => void;
}) {
  const tAttachments = useTranslations("attachments");
  return (
    <button
      type="button"
      onClick={onPreview}
      className="flex w-full min-w-0 items-center gap-2 rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface px-3 py-2 text-left hover:bg-ecmp-hover"
    >
      <IconFile className="size-4 shrink-0 text-ecmp-text-secondary" aria-hidden />
      <span className="min-w-0 flex-1 truncate text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-primary">
        {fileName}
      </span>
      <span className="shrink-0 text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
        {formatFileSize(sizeBytes)} · {fileTypeLabel(mimeType ?? "", null, fileName)}
      </span>
      <span className="shrink-0 text-[length:var(--ecmp-font-caption-size)] font-medium text-ecmp-primary">
        {tAttachments("preview")}
      </span>
    </button>
  );
}

/** Read-only preview so an in-progress form (e.g. Create Complaint) stays mounted. */
export function KnowledgePreviewModal({
  open,
  knowledgeId,
  onClose,
}: {
  open: boolean;
  knowledgeId: string | null;
  onClose: () => void;
}) {
  const t = useTranslations("knowledgeMention");
  const tKnowledge = useTranslations("knowledge");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const locale = useLocale();

  const [knowledge, setKnowledge] = useState<Knowledge | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [previewFileId, setPreviewFileId] = useState<string | null>(null);

  useEffect(() => {
    if (!open || !knowledgeId) return;
    let cancelled = false;
    setKnowledge(null);
    setLoadError(null);
    setLoading(true);
    fetchKnowledge(knowledgeId)
      .then((res) => {
        if (cancelled) return;
        setKnowledge(res.data);
      })
      .catch((err) => {
        if (cancelled) return;
        setLoadError(resolveApiErrorMessage(err, tErrors, tCommon) || t("previewLoadError"));
      })
      .finally(() => {
        if (cancelled) return;
        setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [open, knowledgeId, t, tCommon, tErrors]);

  const previewFile = knowledge?.files.find((file) => file.id === previewFileId) ?? null;

  const effectiveRange = knowledge
    ? [
        knowledge.effectiveFrom ? formatDateTime(knowledge.effectiveFrom, locale) : tCommon("emDash"),
        knowledge.effectiveTo ? formatDateTime(knowledge.effectiveTo, locale) : tCommon("emDash"),
      ].join(" – ")
    : "";

  return (
    <Modal open={open} onClose={onClose} title={knowledge?.title ?? t("previewTitle")}>
      {loading ? <Skeleton rows={6} /> : null}

      {!loading && loadError ? (
        <ErrorState title={t("previewLoadError")} message={loadError} />
      ) : null}

      {!loading && !loadError && knowledge ? (
        <div className="space-y-[var(--ecmp-panel-gap)]">
          <div className="flex flex-wrap items-center gap-2">
            <KnowledgeTypeBadge type={knowledge.knowledgeType} />
            <KnowledgeStatusBadge status={knowledge.status} />
          </div>

          <dl className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] sm:grid-cols-2">
            <PreviewField
              label={tKnowledge("fieldDocumentNumberLabel")}
              value={knowledge.documentNumber || tCommon("emDash")}
            />
            <PreviewField
              label={tKnowledge("fieldVersionLabel")}
              value={knowledge.versionLabel || tCommon("emDash")}
            />
            <PreviewField label={tKnowledge("effectiveRange")} value={effectiveRange} />
          </dl>

          <div className="space-y-1">
            <p className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
              {tKnowledge("fieldSummaryLabel")}
            </p>
            <p className="whitespace-pre-wrap text-[length:var(--ecmp-font-body-size)] leading-relaxed text-ecmp-text-primary">
              {knowledge.summary || tCommon("emDash")}
            </p>
          </div>

          <div className="space-y-2">
            <p className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
              {tKnowledge("documentsSectionTitle")}
            </p>
            {knowledge.files.length === 0 ? (
              <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                {tKnowledge("noFilesYet")}
              </p>
            ) : (
              <div className="space-y-2">
                {knowledge.files.map((file) => (
                  <PreviewFileRow
                    key={file.id}
                    fileName={file.fileName}
                    sizeBytes={file.sizeBytes}
                    mimeType={file.mimeType}
                    onPreview={() => setPreviewFileId(file.id)}
                  />
                ))}
              </div>
            )}
          </div>

          <a
            href={`/knowledge/${knowledge.id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-[length:var(--ecmp-font-body-small-size)] font-medium text-ecmp-primary underline-offset-2 hover:underline"
          >
            {t("openFullPage")}
            <IconExternalLink className="size-3.5" aria-hidden />
          </a>
        </div>
      ) : null}

      {previewFile && knowledge ? (
        <AttachmentViewer
          attachment={toViewerAttachment(previewFile, knowledge.id)}
          open
          onClose={() => setPreviewFileId(null)}
        />
      ) : null}
    </Modal>
  );
}
