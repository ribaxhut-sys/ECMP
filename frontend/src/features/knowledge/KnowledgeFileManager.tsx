"use client";

import { useRef, useState } from "react";
import { useTranslations } from "next-intl";
import {
  ApiError,
  removeKnowledgeFile,
  uploadKnowledgeFile,
} from "@/lib/api";
import type { Knowledge, KnowledgeFile } from "@/lib/api/types";
import { AttachmentViewer } from "@/features/attachments/AttachmentViewer";
import { fileTypeLabel, formatFileSize } from "@/features/attachments/fileTypes";
import { Alert, Button } from "@/shared/ui";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { KnowledgeFileTypeIcon } from "./KnowledgeFileTypeIcon";
import { KnowledgeInlineDocumentPreview } from "./KnowledgeInlineDocumentPreview";
import { pickKnowledgeDisplayFile } from "./knowledgeListMeta";

/** Same accept list as shared attachment storage defaults (PDF, image, office). */
export const KNOWLEDGE_FILE_ACCEPT =
  ".pdf,.png,.jpg,.jpeg,.gif,.webp,.txt,.doc,.docx,.xls,.xlsx";

export function toViewerAttachment(file: KnowledgeFile, knowledgeId: string) {
  const ext = file.fileName.includes(".")
    ? file.fileName.slice(file.fileName.lastIndexOf(".") + 1)
    : null;
  return {
    id: file.id,
    aggregateType: "Knowledge" as const,
    aggregateId: knowledgeId,
    fileName: file.fileName,
    originalName: file.fileName,
    mimeType: file.mimeType,
    extension: ext,
    sizeBytes: file.sizeBytes,
    checksumSha256: "",
    storageProvider: "local",
    uploadedBy: null,
    uploadedAt: file.createdAt,
    status: "AVAILABLE" as const,
  };
}

function FileRow({
  file,
  knowledgeId,
  canMutate,
  busy,
  onRemove,
}: {
  file: KnowledgeFile;
  knowledgeId: string;
  canMutate: boolean;
  busy: boolean;
  onRemove: () => void;
}) {
  const t = useTranslations("knowledge");
  const tAttachments = useTranslations("attachments");
  const [previewOpen, setPreviewOpen] = useState(false);

  return (
    <div className="flex flex-col gap-2 rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface p-[var(--ecmp-card-gap)] sm:flex-row sm:items-center sm:justify-between">
      <div className="flex min-w-0 items-start gap-3">
        <KnowledgeFileTypeIcon file={file} />
        <div className="min-w-0">
          <p className="truncate text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary">
            {file.fileName}
          </p>
          <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
            {formatFileSize(file.sizeBytes)} ·{" "}
            {fileTypeLabel(file.mimeType, null, file.fileName)}
          </p>
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <Button type="button" size="sm" variant="outline" onClick={() => setPreviewOpen(true)}>
          {tAttachments("preview")}
        </Button>
        {canMutate ? (
          <Button
            type="button"
            size="sm"
            variant="danger"
            disabled={busy}
            onClick={onRemove}
          >
            {t("removeFile")}
          </Button>
        ) : null}
      </div>
      <AttachmentViewer
        attachment={toViewerAttachment(file, knowledgeId)}
        open={previewOpen}
        onClose={() => setPreviewOpen(false)}
      />
    </div>
  );
}

export function KnowledgeFileManager({
  knowledge,
  canManage,
  onChanged,
  showInlinePreview = true,
}: {
  knowledge: Knowledge;
  /** knowledge:manage holder for THIS record (Pusat-proven). */
  canManage: boolean;
  onChanged: (next: Knowledge) => void;
  /** When false (e.g. inside edit modal), skip the large inline preview. */
  showInlinePreview?: boolean;
}) {
  const t = useTranslations("knowledge");
  const tErrors = useTranslations("errors");
  const tCommon = useTranslations("common");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const canMutate = canManage && knowledge.status === "DRAFT";
  const displayFile = pickKnowledgeDisplayFile(knowledge.files);

  async function onFileSelected(event: React.ChangeEvent<HTMLInputElement>) {
    const picked = Array.from(event.target.files ?? []);
    event.target.value = "";
    if (picked.length === 0) return;
    setBusy(true);
    setError(null);
    try {
      let next = knowledge;
      for (let i = 0; i < picked.length; i++) {
        const role =
          next.files.length === 0 && i === 0 ? "PRIMARY" : "SUPPORTING";
        const res = await uploadKnowledgeFile(knowledge.id, picked[i], role);
        next = res.data;
      }
      onChanged(next);
    } catch (err) {
      const message =
        err instanceof ApiError && err.message
          ? err.message
          : resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToUploadFile");
      setError(message);
    } finally {
      setBusy(false);
    }
  }

  async function onRemove(attachmentId: string) {
    setBusy(true);
    setError(null);
    try {
      const res = await removeKnowledgeFile(knowledge.id, attachmentId);
      onChanged(res.data);
    } catch (err) {
      const message =
        err instanceof ApiError && err.status === 409
          ? t("filesDraftOnly")
          : err instanceof ApiError && err.message
            ? err.message
            : resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToRemoveFile");
      setError(message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-[var(--ecmp-form-gap)]">
      {error ? <Alert tone="danger" title={t("actionFailed")} description={error} /> : null}

      {showInlinePreview && displayFile ? (
        <KnowledgeInlineDocumentPreview file={displayFile} knowledgeId={knowledge.id} />
      ) : null}

      {knowledge.files.length === 0 ? (
        <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
          {t("noFilesYet")}
        </p>
      ) : (
        <div className="space-y-2">
          {knowledge.files.map((file) => (
            <FileRow
              key={file.id}
              file={file}
              knowledgeId={knowledge.id}
              canMutate={canMutate}
              busy={busy}
              onRemove={() => void onRemove(file.id)}
            />
          ))}
        </div>
      )}

      {canMutate ? (
        <div className="flex flex-wrap gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept={KNOWLEDGE_FILE_ACCEPT}
            multiple
            className="hidden"
            onChange={(e) => void onFileSelected(e)}
          />
          <Button
            type="button"
            variant="secondary"
            size="sm"
            loading={busy}
            disabled={busy}
            onClick={() => fileInputRef.current?.click()}
          >
            {knowledge.files.length === 0 ? t("uploadFile") : t("addFile")}
          </Button>
        </div>
      ) : null}
    </div>
  );
}
