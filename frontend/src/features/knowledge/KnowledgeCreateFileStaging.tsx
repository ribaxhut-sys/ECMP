"use client";

import { useRef } from "react";
import { useTranslations } from "next-intl";
import { Button } from "@/shared/ui";
import { IconClose } from "@/shared/icons";
import { formatFileSize, fileTypeLabel } from "@/features/attachments/fileTypes";
import { KnowledgeFileTypeIcon } from "./KnowledgeFileTypeIcon";
import { KNOWLEDGE_FILE_ACCEPT } from "./KnowledgeFileManager";

export interface StagedKnowledgeFile {
  file: File;
}

/**
 * Files picked before the Knowledge record exists — held client-side and
 * uploaded (one `uploadKnowledgeFile` call each) right after create succeeds.
 * No staging endpoint on the backend for Knowledge, unlike Complaint attachments.
 * First file becomes PRIMARY on upload; additional files are SUPPORTING.
 */
export function KnowledgeCreateFileStaging({
  files,
  onChange,
  disabled,
}: {
  files: StagedKnowledgeFile[];
  onChange: (next: StagedKnowledgeFile[]) => void;
  disabled?: boolean;
}) {
  const t = useTranslations("knowledge");
  const inputRef = useRef<HTMLInputElement>(null);

  function addFiles(event: React.ChangeEvent<HTMLInputElement>) {
    const picked = Array.from(event.target.files ?? []);
    event.target.value = "";
    if (picked.length === 0) return;
    onChange([...files, ...picked.map((file) => ({ file }))]);
  }

  function remove(index: number) {
    onChange(files.filter((_, i) => i !== index));
  }

  return (
    <div className="space-y-[var(--ecmp-form-gap)]">
      <p className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
        {t("documentsSectionTitle")}
      </p>
      <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
        {t("documentsHint")}
      </p>

      {files.length > 0 ? (
        <ul className="space-y-2">
          {files.map((staged, index) => (
            <li
              key={`${staged.file.name}-${index}`}
              className="flex min-w-0 items-center gap-2 rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface px-3 py-2"
            >
              <KnowledgeFileTypeIcon
                file={{ mimeType: staged.file.type, fileName: staged.file.name }}
                size="sm"
              />
              <span className="min-w-0 flex-1 truncate text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-primary">
                {staged.file.name}
              </span>
              <span className="shrink-0 text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
                {formatFileSize(staged.file.size)} ·{" "}
                {fileTypeLabel(staged.file.type, null, staged.file.name)}
              </span>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                disabled={disabled}
                aria-label={t("removeFile")}
                onClick={() => remove(index)}
                className="!min-h-[32px] !min-w-[32px] shrink-0 px-0"
              >
                <IconClose className="size-4" />
              </Button>
            </li>
          ))}
        </ul>
      ) : null}

      <div className="flex flex-wrap gap-2">
        <input
          ref={inputRef}
          type="file"
          accept={KNOWLEDGE_FILE_ACCEPT}
          multiple
          aria-label={t("uploadFile")}
          className="hidden"
          onChange={addFiles}
        />
        <Button
          type="button"
          variant="secondary"
          size="sm"
          disabled={disabled}
          onClick={() => inputRef.current?.click()}
        >
          {files.length === 0 ? t("uploadFile") : t("addFile")}
        </Button>
      </div>
    </div>
  );
}
