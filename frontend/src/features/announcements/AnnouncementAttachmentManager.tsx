"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import {
  fetchAnnouncementAttachmentLibrary,
  linkAnnouncementAttachment,
  removeAnnouncementAttachment,
  updateAnnouncementAttachmentVisibility,
  uploadAnnouncementAttachment,
} from "@/lib/api";
import type {
  AnnouncementAttachment,
  AnnouncementAttachmentLibraryItem,
  AnnouncementAttachmentVisibility,
} from "@/lib/api/types";
import { fileTypeLabel, formatFileSize } from "@/features/attachments/fileTypes";
import { IconClose, IconFile } from "@/shared/icons";
import { Alert, Button, Checkbox, Input, Modal, RadioGroup } from "@/shared/ui";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";

function visibilityOptions(t: ReturnType<typeof useTranslations<"announcements">>) {
  return [
    {
      value: "IMMEDIATE",
      label: (
        <span className="flex flex-col gap-0.5">
          <span className="font-medium text-ecmp-text-primary">
            {t("visibilityImmediate")}
          </span>
          <span className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
            {t("visibilityImmediateHelper")}
          </span>
        </span>
      ),
    },
    {
      value: "PUBLISHED",
      label: (
        <span className="flex flex-col gap-0.5">
          <span className="font-medium text-ecmp-text-primary">
            {t("visibilityPublished")}
          </span>
          <span className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
            {t("visibilityPublishedHelper")}
          </span>
        </span>
      ),
    },
  ] as const;
}

function AttachmentRow({
  announcementId,
  attachment,
  onChange,
}: {
  announcementId: string;
  attachment: AnnouncementAttachment;
  onChange: () => void;
}) {
  const t = useTranslations("announcements");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onVisibilityChange(next: string) {
    setBusy(true);
    setError(null);
    try {
      await updateAnnouncementAttachmentVisibility(
        announcementId,
        attachment.id,
        next as AnnouncementAttachmentVisibility,
      );
      onChange();
    } catch (err) {
      setError(resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToSave"));
    } finally {
      setBusy(false);
    }
  }

  async function onRemove() {
    setBusy(true);
    setError(null);
    try {
      await removeAnnouncementAttachment(announcementId, attachment.id);
      onChange();
    } catch (err) {
      setError(resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToRemoveAttachment"));
      setBusy(false);
    }
  }

  return (
    <div className="space-y-2 rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface p-[var(--ecmp-card-gap)]">
      <div className="flex items-start justify-between gap-3">
        <div className="flex min-w-0 items-start gap-3">
          <IconFile className="mt-0.5 size-5 shrink-0 text-ecmp-text-secondary" aria-hidden />
          <div className="min-w-0">
            <p className="truncate text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary">
              {attachment.fileName}
            </p>
            <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
              {formatFileSize(attachment.sizeBytes)} ·{" "}
              {fileTypeLabel(attachment.mimeType, null, attachment.fileName)}
            </p>
          </div>
        </div>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          aria-label={t("removeAttachment")}
          disabled={busy}
          onClick={() => void onRemove()}
        >
          <IconClose className="size-4" aria-hidden />
        </Button>
      </div>
      {error ? <Alert tone="danger" title={t("actionFailed")} description={error} /> : null}
      <RadioGroup
        name={`visibility-${attachment.id}`}
        label={t("attachmentVisibilityLabel")}
        value={attachment.visibility}
        onChange={(next) => void onVisibilityChange(next)}
        disabled={busy}
        options={visibilityOptions(t)}
      />
    </div>
  );
}

function LinkExistingAttachmentModal({
  open,
  announcementId,
  visibility,
  alreadyLinkedIds,
  onClose,
  onLinked,
}: {
  open: boolean;
  announcementId: string;
  visibility: AnnouncementAttachmentVisibility;
  alreadyLinkedIds: ReadonlySet<string>;
  onClose: () => void;
  onLinked: (added: AnnouncementAttachment[]) => void;
}) {
  const t = useTranslations("announcements");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const [items, setItems] = useState<AnnouncementAttachmentLibraryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [linking, setLinking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (!open) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    setSearch("");
    setSelected(new Set());
    void fetchAnnouncementAttachmentLibrary({
      excludeAnnouncementId: announcementId,
    })
      .then((res) => {
        if (!cancelled) setItems(res.data);
      })
      .catch((err) => {
        if (!cancelled) {
          setItems([]);
          setError(
            resolveApiErrorMessage(err, tErrors, tCommon) ||
              t("unableToLoadAttachmentLibrary"),
          );
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [open, announcementId, t, tCommon, tErrors]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return items;
    return items.filter((item) => item.fileName.toLowerCase().includes(q));
  }, [items, search]);

  function toggle(id: string) {
    if (alreadyLinkedIds.has(id)) return;
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  async function confirmLink() {
    const ids = [...selected].filter((id) => !alreadyLinkedIds.has(id));
    if (ids.length === 0) return;
    setLinking(true);
    setError(null);
    const failures: string[] = [];
    const added: AnnouncementAttachment[] = [];
    try {
      for (const attachmentId of ids) {
        try {
          const res = await linkAnnouncementAttachment(announcementId, {
            attachmentId,
            visibility,
          });
          added.push(res.data);
        } catch (err) {
          const name =
            items.find((item) => item.id === attachmentId)?.fileName ?? attachmentId;
          failures.push(
            `${name}: ${
              resolveApiErrorMessage(err, tErrors, tCommon) ||
              t("unableToLinkAttachment")
            }`,
          );
        }
      }
      onLinked(added);
      if (failures.length > 0) {
        setError(
          failures.length === ids.length
            ? failures.join(" ")
            : t("partialLinkFailed", { detail: failures.join(" ") }),
        );
        return;
      }
      onClose();
    } finally {
      setLinking(false);
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={t("linkAttachmentLibraryTitle")}
      size="lg"
      footer={
        <>
          <Button
            type="button"
            variant="secondary"
            disabled={linking}
            onClick={onClose}
          >
            {t("linkAttachmentCancel")}
          </Button>
          <Button
            type="button"
            loading={linking}
            disabled={linking || selected.size === 0}
            onClick={() => void confirmLink()}
          >
            {linking ? t("linkingAttachments") : t("linkAttachmentConfirm")}
          </Button>
        </>
      }
    >
      <div className="space-y-[var(--ecmp-form-gap)]">
        {error ? (
          <Alert tone="danger" title={t("actionFailed")} description={error} />
        ) : null}
        <Input
          label={t("linkAttachmentSearchLabel")}
          placeholder={t("linkAttachmentSearchPlaceholder")}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          disabled={loading || linking}
        />
        {loading ? (
          <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
            {tCommon("loading")}
          </p>
        ) : filtered.length === 0 ? (
          <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
            {items.length === 0
              ? t("linkAttachmentEmpty")
              : t("linkAttachmentEmptyFiltered")}
          </p>
        ) : (
          <ul className="max-h-72 space-y-2 overflow-y-auto">
            {filtered.map((item) => {
              const disabled = alreadyLinkedIds.has(item.id);
              const checked = selected.has(item.id);
              return (
                <li
                  key={item.id}
                  className={`rounded-[var(--ecmp-radius-md)] border border-ecmp-border p-3 ${
                    disabled ? "opacity-50" : "hover:bg-ecmp-hover"
                  }`}
                >
                  <Checkbox
                    id={`link-att-${item.id}`}
                    name={`link-att-${item.id}`}
                    checked={checked}
                    disabled={disabled || linking}
                    onChange={() => toggle(item.id)}
                    labelContent={
                      <span className="min-w-0">
                        <span className="block truncate font-medium text-ecmp-text-primary">
                          {item.fileName}
                        </span>
                        <span className="block text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
                          {formatFileSize(item.sizeBytes)} ·{" "}
                          {fileTypeLabel(item.mimeType, null, item.fileName)}
                          {" · "}
                          {item.accessLevel === "PUBLIC"
                            ? t("accessPublic")
                            : t("accessPrivate")}
                        </span>
                      </span>
                    }
                  />
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </Modal>
  );
}

/** Upload controls only — visibility + file picker (for the compact meta row). */
export function AnnouncementAttachmentUploadControls({
  announcementId,
  onUploaded,
  autoOpen = false,
  existingAttachmentIds = [],
}: {
  announcementId: string;
  /** Called after the batch finishes; ``added`` are successful uploads (may be empty if all failed). */
  onUploaded: (added: AnnouncementAttachment[]) => void;
  /** Open the native file picker once on mount (e.g. right after draft create). */
  autoOpen?: boolean;
  /** IDs already on this announcement — disabled in the link picker. */
  existingAttachmentIds?: readonly string[];
}) {
  const t = useTranslations("announcements");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const autoOpenedRef = useRef(false);
  const [pendingVisibility, setPendingVisibility] =
    useState<AnnouncementAttachmentVisibility>("PUBLISHED");
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [linkOpen, setLinkOpen] = useState(false);
  const alreadyLinkedIds = useMemo(
    () => new Set(existingAttachmentIds),
    [existingAttachmentIds],
  );

  useEffect(() => {
    if (!autoOpen || autoOpenedRef.current) return;
    autoOpenedRef.current = true;
    // Defer so the input is mounted and click isn't swallowed by the creating button.
    const timer = window.setTimeout(() => {
      fileInputRef.current?.click();
    }, 0);
    return () => window.clearTimeout(timer);
  }, [autoOpen]);

  async function onFileSelected(event: React.ChangeEvent<HTMLInputElement>) {
    // Copy before clearing — FileList can be emptied in place when value is reset.
    const files = Array.from(event.target.files ?? []);
    event.target.value = "";
    if (files.length === 0) return;

    setUploading(true);
    setError(null);
    const failures: string[] = [];
    const added: AnnouncementAttachment[] = [];

    try {
      // Sequential — same visibility for the whole batch; one API call per file
      // (backend accepts a single multipart file per request).
      for (const file of files) {
        try {
          const res = await uploadAnnouncementAttachment(
            announcementId,
            file,
            pendingVisibility,
          );
          added.push(res.data);
        } catch (err) {
          failures.push(
            `${file.name}: ${
              resolveApiErrorMessage(err, tErrors, tCommon) ||
              t("unableToUploadAttachment")
            }`,
          );
        }
      }
      onUploaded(added);
      if (failures.length > 0) {
        setError(
          failures.length === files.length
            ? failures.join(" ")
            : t("partialUploadFailed", { detail: failures.join(" ") }),
        );
      }
    } finally {
      setUploading(false);
    }
  }

  const busy = uploading;

  return (
    <div className="space-y-2">
      {error ? <Alert tone="danger" title={t("actionFailed")} description={error} /> : null}
      <RadioGroup
        name={`new-attachment-visibility-${announcementId}`}
        label={t("attachmentVisibilityLabel")}
        value={pendingVisibility}
        onChange={(next) =>
          setPendingVisibility(next as AnnouncementAttachmentVisibility)
        }
        disabled={busy}
        options={visibilityOptions(t)}
      />
      <input
        ref={fileInputRef}
        type="file"
        multiple
        className="hidden"
        accept=".pdf,.png,.jpg,.jpeg,.gif,.webp,.txt,.doc,.docx,.xls,.xlsx,.zip,application/zip,image/jpeg,image/png,image/gif,image/webp"
        onChange={(e) => void onFileSelected(e)}
      />
      <div className="flex flex-wrap gap-2">
        <Button
          type="button"
          variant="secondary"
          size="sm"
          loading={uploading}
          disabled={busy}
          onClick={() => fileInputRef.current?.click()}
        >
          {uploading ? t("uploading") : t("uploadAttachment")}
        </Button>
        <Button
          type="button"
          variant="secondary"
          size="sm"
          disabled={busy}
          onClick={() => setLinkOpen(true)}
        >
          {t("linkExistingAttachment")}
        </Button>
      </div>
      <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
        {t("addAttachmentMultipleHint")}
      </p>
      <LinkExistingAttachmentModal
        open={linkOpen}
        announcementId={announcementId}
        visibility={pendingVisibility}
        alreadyLinkedIds={alreadyLinkedIds}
        onClose={() => setLinkOpen(false)}
        onLinked={(added) => {
          onUploaded(added);
        }}
      />
    </div>
  );
}

/** Managed attachment rows (edit visibility / remove) — full width below the meta row. */
export function AnnouncementAttachmentManagedList({
  announcementId,
  attachments,
  onChange,
}: {
  announcementId: string;
  attachments: AnnouncementAttachment[];
  onChange: () => void;
}) {
  const t = useTranslations("announcements");
  const items = attachments ?? [];

  if (items.length === 0) {
    return (
      <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
        {t("noAttachmentsYet")}
      </p>
    );
  }

  return (
    <div className="space-y-2">
      {items.map((attachment) => (
        <AttachmentRow
          key={attachment.id}
          announcementId={announcementId}
          attachment={attachment}
          onChange={onChange}
        />
      ))}
    </div>
  );
}

/** Stacked compose (list + upload) — used by tests and any non-meta-row call sites. */
export function AnnouncementAttachmentManager({
  announcementId,
  attachments,
  onChange,
}: {
  announcementId: string;
  attachments: AnnouncementAttachment[];
  onChange: () => void;
}) {
  return (
    <div className="space-y-[var(--ecmp-form-gap)]">
      <AnnouncementAttachmentManagedList
        announcementId={announcementId}
        attachments={attachments}
        onChange={onChange}
      />
      <div className="rounded-[var(--ecmp-radius-md)] border border-dashed border-ecmp-border p-[var(--ecmp-card-gap)]">
        <AnnouncementAttachmentUploadControls
          announcementId={announcementId}
          existingAttachmentIds={(attachments ?? []).map((item) => item.id)}
          onUploaded={() => onChange()}
        />
      </div>
    </div>
  );
}
