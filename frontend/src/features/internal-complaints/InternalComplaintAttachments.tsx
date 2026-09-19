"use client";

import { useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import {
  ApiError,
  fetchAttachments,
  uploadAttachment,
  type Attachment,
} from "@/lib/api";
import { AttachmentCard } from "@/features/attachments/AttachmentCard";
import {
  INTERNAL_COMPLAINT_FILE_ACCEPT,
  fileTypeLabel,
  formatFileSize,
  isAllowedInternalComplaintFile,
} from "@/features/attachments/fileTypes";
import { IconClose, IconFile, IconImage } from "@/shared/icons";
import { Alert, Button, Empty } from "@/shared/ui";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";

export const INTERNAL_ATTACHMENT_MAX_FILES = 5;
export const INTERNAL_ATTACHMENT_MAX_BYTES = 50 * 1024 * 1024;

function FileCue({ file }: { file: File }) {
  const isImage = (file.type || "").startsWith("image/");
  const Icon = isImage ? IconImage : IconFile;
  return (
    <Icon
      className={
        isImage
          ? "size-4 shrink-0 text-ecmp-primary"
          : "size-4 shrink-0 text-ecmp-text-secondary"
      }
      aria-hidden
    />
  );
}

export function InternalComplaintFileStaging({
  files,
  onChange,
  disabled,
  error,
}: {
  files: File[];
  onChange: (next: File[]) => void;
  disabled?: boolean;
  error?: string;
}) {
  const t = useTranslations("internalComplaints");
  const inputRef = useRef<HTMLInputElement>(null);
  const [localError, setLocalError] = useState<string | null>(null);

  function addFiles(event: React.ChangeEvent<HTMLInputElement>) {
    const picked = Array.from(event.target.files ?? []);
    event.target.value = "";
    if (picked.length === 0) return;
    const allowed = picked.filter(isAllowedInternalComplaintFile);
    if (allowed.length !== picked.length) {
      setLocalError(t("attachmentsTypeError"));
    } else {
      setLocalError(null);
    }
    const oversized = allowed.some((file) => file.size > INTERNAL_ATTACHMENT_MAX_BYTES);
    if (oversized) {
      setLocalError(t("attachmentsSizeError"));
      return;
    }
    const next = [...files, ...allowed];
    if (next.length > INTERNAL_ATTACHMENT_MAX_FILES) {
      setLocalError(t("attachmentsMaxFilesError"));
      onChange(next.slice(0, INTERNAL_ATTACHMENT_MAX_FILES));
      return;
    }
    onChange(next);
  }

  function remove(index: number) {
    onChange(files.filter((_, i) => i !== index));
    setLocalError(null);
  }

  return (
    <div className="space-y-[var(--ecmp-form-gap)]">
      <p className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
        {t("sectionAttachments")}
      </p>
      <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
        {t("attachmentsHint")}
      </p>
      {error || localError ? (
        <Alert tone="danger" title={error || localError || ""} />
      ) : null}

      {files.length > 0 ? (
        <ul className="space-y-2">
          {files.map((file, index) => (
            <li
              key={`${file.name}-${file.size}-${index}`}
              className="flex min-w-0 items-center gap-2 rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface px-3 py-2"
            >
              <FileCue file={file} />
              <span className="min-w-0 flex-1 truncate text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-primary">
                {file.name}
              </span>
              <span className="shrink-0 text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
                {formatFileSize(file.size)} ·{" "}
                {fileTypeLabel(file.type, null, file.name)}
              </span>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                disabled={disabled}
                aria-label={t("removeAttachment")}
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
          accept={INTERNAL_COMPLAINT_FILE_ACCEPT}
          multiple
          aria-label={t("addAttachment")}
          className="hidden"
          onChange={addFiles}
        />
        <Button
          type="button"
          variant="secondary"
          size="sm"
          disabled={disabled || files.length >= INTERNAL_ATTACHMENT_MAX_FILES}
          onClick={() => inputRef.current?.click()}
        >
          {files.length === 0 ? t("addAttachment") : t("addAnotherAttachment")}
        </Button>
      </div>
    </div>
  );
}

export function InternalComplaintAttachmentsPanel({
  complaintId,
  canUpload,
}: {
  complaintId: string;
  canUpload: boolean;
}) {
  const t = useTranslations("internalComplaints");
  const tErrors = useTranslations("errors");
  const tCommon = useTranslations("common");
  const tAttach = useTranslations("attachments");
  const inputRef = useRef<HTMLInputElement>(null);
  const [items, setItems] = useState<Attachment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    setError(null);
  }, [complaintId]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchAttachments("InternalComplaint", complaintId)
      .then((res) => {
        if (cancelled) return;
        setItems(res.data ?? []);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        if (err instanceof ApiError) {
          setError(resolveApiErrorMessage(err, tErrors, tCommon, "unexpectedError"));
        } else {
          setError(tAttach("unableToLoad"));
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [complaintId, refreshKey, tAttach, tCommon, tErrors]);

  async function onFileSelected(event: React.ChangeEvent<HTMLInputElement>) {
    const picked = Array.from(event.target.files ?? []);
    event.target.value = "";
    if (picked.length === 0) return;
    const allowed = picked.filter(isAllowedInternalComplaintFile);
    if (allowed.length === 0) {
      setError(t("attachmentsTypeError"));
      return;
    }
    if (allowed.some((file) => file.size > INTERNAL_ATTACHMENT_MAX_BYTES)) {
      setError(t("attachmentsSizeError"));
      return;
    }
    if (items.length + allowed.length > INTERNAL_ATTACHMENT_MAX_FILES) {
      setError(t("attachmentsMaxFilesError"));
      return;
    }
    setUploading(true);
    setError(null);
    const failed: string[] = [];
    for (const file of allowed) {
      try {
        await uploadAttachment("InternalComplaint", complaintId, file);
      } catch (err) {
        failed.push(file.name);
        if (err instanceof ApiError) {
          setError(resolveApiErrorMessage(err, tErrors, tCommon, "unexpectedError"));
        }
      }
    }
    if (failed.length > 0) {
      setError(t("attachmentsPartialFail", { detail: failed.join(", ") }));
    }
    setUploading(false);
    setRefreshKey((n) => n + 1);
  }

  return (
    <div className="space-y-3">
      {error ? <Alert tone="danger" title={error} /> : null}
      <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
        {t("attachmentsHint")}
      </p>
      {loading ? (
        <Empty title={tCommon("loading")} description="" />
      ) : items.length === 0 ? (
        <Empty title={t("noAttachments")} description="" />
      ) : (
        <ul className="space-y-2">
          {items.map((item) => (
            <li key={item.id}>
              <AttachmentCard attachment={item} />
            </li>
          ))}
        </ul>
      )}
      {canUpload ? (
        <div className="flex flex-wrap gap-2">
          <input
            ref={inputRef}
            type="file"
            accept={INTERNAL_COMPLAINT_FILE_ACCEPT}
            multiple
            className="hidden"
            aria-label={t("addAttachment")}
            onChange={(event) => void onFileSelected(event)}
          />
          <Button
            type="button"
            variant="secondary"
            size="sm"
            loading={uploading}
            disabled={uploading || items.length >= INTERNAL_ATTACHMENT_MAX_FILES}
            onClick={() => inputRef.current?.click()}
          >
            {t("addAttachment")}
          </Button>
        </div>
      ) : null}
    </div>
  );
}
