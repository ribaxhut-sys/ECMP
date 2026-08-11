"use client";

import { useRef, useState } from "react";
import { useTranslations } from "next-intl";
import {
  ApiError,
  removeKnowledgeFile,
  setPrimaryKnowledgeFile,
  uploadKnowledgeFile,
} from "@/lib/api";
import type { Knowledge, KnowledgeFile } from "@/lib/api/types";
import { AttachmentViewer } from "@/features/attachments/AttachmentViewer";
import { fileTypeLabel, formatFileSize } from "@/features/attachments/fileTypes";
import { Alert, Badge, Button } from "@/shared/ui";
import { IconFile } from "@/shared/icons";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";

function toViewerAttachment(file: KnowledgeFile, knowledgeId: string) {
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
  onSetPrimary,
  onRemove,
}: {
  file: KnowledgeFile;
  knowledgeId: string;
  canMutate: boolean;
  busy: boolean;
  onSetPrimary: () => void;
  onRemove: () => void;
}) {
  const t = useTranslations("knowledge");
  const tAttachments = useTranslations("attachments");
  const [previewOpen, setPreviewOpen] = useState(false);

  return (
    <div className="flex flex-col gap-2 rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface p-[var(--ecmp-card-gap)] sm:flex-row sm:items-center sm:justify-between">
      <div className="flex min-w-0 items-start gap-3">
        <IconFile className="mt-0.5 size-5 shrink-0 text-ecmp-text-secondary" aria-hidden />
        <div className="min-w-0">
          <p className="truncate text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary">
            {file.fileName}
          </p>
          <p className="flex flex-wrap items-center gap-2 text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
            <Badge tone={file.role === "PRIMARY" ? "success" : "neutral"}>
              {file.role === "PRIMARY" ? t("filePrimary") : t("fileSupporting")}
            </Badge>
            <span>
              {formatFileSize(file.sizeBytes)} ·{" "}
              {fileTypeLabel(file.mimeType, null, file.fileName)}
            </span>
          </p>
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <Button type="button" size="sm" variant="outline" onClick={() => setPreviewOpen(true)}>
          {tAttachments("preview")}
        </Button>
        {canMutate ? (
          <>
            {file.role !== "PRIMARY" ? (
              <Button
                type="button"
                size="sm"
                variant="secondary"
                disabled={busy}
                onClick={onSetPrimary}
              >
                {t("setAsPrimary")}
              </Button>
            ) : null}
            <Button
              type="button"
              size="sm"
              variant="danger"
              disabled={busy}
              onClick={onRemove}
            >
              {t("removeFile")}
            </Button>
          </>
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
}: {
  knowledge: Knowledge;
  /** knowledge:manage holder for THIS record (Pusat-proven). */
  canManage: boolean;
  onChanged: (next: Knowledge) => void;
}) {
  const t = useTranslations("knowledge");
  const tErrors = useTranslations("errors");
  const tCommon = useTranslations("common");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const pendingRoleRef = useRef<"PRIMARY" | "SUPPORTING">("SUPPORTING");

  const canMutate = canManage && knowledge.status === "DRAFT";

  function openPicker(role: "PRIMARY" | "SUPPORTING") {
    pendingRoleRef.current = role;
    fileInputRef.current?.click();
  }

  async function onFileSelected(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    setBusy(true);
    setError(null);
    try {
      const res = await uploadKnowledgeFile(knowledge.id, file, pendingRoleRef.current);
      onChanged(res.data);
    } catch (err) {
      setError(resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToUploadFile"));
    } finally {
      setBusy(false);
    }
  }

  async function onSetPrimary(attachmentId: string) {
    setBusy(true);
    setError(null);
    try {
      const res = await setPrimaryKnowledgeFile(knowledge.id, attachmentId);
      onChanged(res.data);
    } catch (err) {
      setError(resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToSave"));
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
          : resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToRemoveFile");
      setError(message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-[var(--ecmp-form-gap)]">
      {error ? <Alert tone="danger" title={t("actionFailed")} description={error} /> : null}

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
              onSetPrimary={() => void onSetPrimary(file.id)}
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
            className="hidden"
            onChange={(e) => void onFileSelected(e)}
          />
          <Button
            type="button"
            variant="secondary"
            size="sm"
            loading={busy}
            disabled={busy}
            onClick={() => openPicker("PRIMARY")}
          >
            {t("uploadPrimaryFile")}
          </Button>
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={busy}
            onClick={() => openPicker("SUPPORTING")}
          >
            {t("uploadSupportingFile")}
          </Button>
        </div>
      ) : null}
    </div>
  );
}
