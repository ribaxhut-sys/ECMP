"use client";

import { useState, type ChangeEvent, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import {
  deleteAnnouncement,
  fetchAnnouncement,
  publishAnnouncement,
  unpublishAnnouncement,
  updateAnnouncement,
} from "@/lib/api";
import type { Announcement, AnnouncementAttachment } from "@/lib/api/types";
import { Alert, Button, Input, Modal } from "@/shared/ui";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { useToast } from "@/shared/providers";
import {
  AnnouncementAttachmentManagedList,
  AnnouncementAttachmentUploadControls,
} from "./AnnouncementAttachmentManager";
import { AnnouncementFormFields } from "./AnnouncementFormFields";
import {
  announcementFormFromExisting,
  createEmptyAnnouncementForm,
  toAnnouncementPublishRequest,
  toAnnouncementUpdateRequest,
  validateAnnouncementForm,
  type AnnouncementFieldErrors,
  type AnnouncementFormValues,
} from "./announcementForm";

/**
 * Edit / Publish / Publish now / Unpublish / Delete (+ optional View).
 * Used on expanded management rows and on detail when ``?from=manage``.
 */
export function AnnouncementManageActions({
  announcement,
  onChanged,
  onDeleted,
  showView = false,
}: {
  announcement: Announcement;
  /** Refresh parent after a successful mutation (except delete). */
  onChanged: (opts?: { silent?: boolean }) => void | Promise<void>;
  /** After delete — list collapses/reloads; detail navigates home if omitted. */
  onDeleted?: () => void | Promise<void>;
  /** Show View → full detail page (management list expand). */
  showView?: boolean;
}) {
  const router = useRouter();
  const t = useTranslations("announcements");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const { pushSuccess } = useToast();

  const [actionError, setActionError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const [editing, setEditing] = useState(false);
  const [editValues, setEditValues] = useState<AnnouncementFormValues>(
    createEmptyAnnouncementForm,
  );
  const [editErrors, setEditErrors] = useState<AnnouncementFieldErrors>({});
  const [editAnnouncement, setEditAnnouncement] =
    useState<Announcement | null>(null);
  const [savingEdit, setSavingEdit] = useState(false);

  const [showPublish, setShowPublish] = useState(false);
  const [publishStartAt, setPublishStartAt] = useState("");
  const [publishStartAtError, setPublishStartAtError] = useState<string | null>(
    null,
  );
  const [publishBusy, setPublishBusy] = useState(false);

  const [showDelete, setShowDelete] = useState(false);
  const [deleteBusy, setDeleteBusy] = useState(false);

  const isScheduled = announcement.effectiveStatus === "SCHEDULED";
  const isPublishedLive =
    announcement.status === "PUBLISHED" && !isScheduled;

  function openEdit() {
    setActionError(null);
    setEditErrors({});
    setEditing(true);
    setEditAnnouncement(announcement);
    setEditValues(
      announcementFormFromExisting({
        title: announcement.title,
        body: announcement.body,
        priority: announcement.priority,
        startAt: announcement.startAt,
        endAt: announcement.endAt,
      }),
    );
    void (async () => {
      try {
        const res = await fetchAnnouncement(announcement.id);
        setEditAnnouncement(res.data);
        setEditValues(
          announcementFormFromExisting({
            title: res.data.title,
            body: res.data.body,
            priority: res.data.priority,
            startAt: res.data.startAt,
            endAt: res.data.endAt,
          }),
        );
      } catch {
        // keep the list snapshot already shown in the modal
      }
    })();
  }

  function openPublish() {
    setPublishStartAt("");
    setPublishStartAtError(null);
    setActionError(null);
    setShowPublish(true);
  }

  function validatePublishStartAt(startAtLocal: string): string | null {
    if (!startAtLocal.trim()) return null;
    const start = new Date(startAtLocal);
    if (Number.isNaN(start.getTime())) return "announcementStartAtInvalid";
    if (announcement.endAt) {
      const end = new Date(announcement.endAt);
      if (!Number.isNaN(end.getTime()) && start >= end) {
        return "announcementStartBeforeEnd";
      }
    }
    return null;
  }

  function mergeAttachments(
    current: Announcement,
    added: AnnouncementAttachment[],
  ): Announcement {
    if (added.length === 0) return current;
    const seen = new Set(current.attachments.map((item) => item.id));
    const merged = [
      ...current.attachments,
      ...added.filter((item) => !seen.has(item.id)),
    ];
    return {
      ...current,
      attachments: merged,
      attachmentCount: merged.length,
    };
  }

  async function refreshEditAttachments(
    added: AnnouncementAttachment[] = [],
  ) {
    if (!editAnnouncement) return;
    const announcementId = editAnnouncement.id;
    if (added.length > 0) {
      setEditAnnouncement((prev) =>
        prev ? mergeAttachments(prev, added) : prev,
      );
    }
    try {
      const res = await fetchAnnouncement(announcementId);
      const fresh = {
        ...res.data,
        attachments: res.data.attachments ?? [],
        attachmentCount:
          res.data.attachmentCount ?? res.data.attachments?.length ?? 0,
      };
      setEditAnnouncement(fresh);
    } catch {
      // best-effort — keep merged local state if refetch fails
    }
    // Silent: do not remount the expand/edit tree (that was wiping the list).
    await onChanged({ silent: true });
  }

  async function submitEdit(event: FormEvent) {
    event.preventDefault();
    if (!editAnnouncement) return;
    const errors = validateAnnouncementForm(editValues);
    setEditErrors(errors);
    if (Object.keys(errors).length > 0) return;

    setSavingEdit(true);
    try {
      // Always persist startAt from the edit form so schedule changes stick.
      await updateAnnouncement(
        editAnnouncement.id,
        toAnnouncementUpdateRequest(editValues, { includeStartAt: true }),
      );
      pushSuccess(tCommon("success"), t("updatedSuccess"));
      setEditing(false);
      setEditAnnouncement(null);
      await onChanged();
    } catch (err) {
      setActionError(
        resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToSave"),
      );
    } finally {
      setSavingEdit(false);
    }
  }

  async function confirmPublish() {
    const startError = validatePublishStartAt(publishStartAt);
    if (startError) {
      setPublishStartAtError(startError);
      return;
    }
    setPublishBusy(true);
    setActionError(null);
    try {
      await publishAnnouncement(
        announcement.id,
        toAnnouncementPublishRequest(publishStartAt),
      );
      pushSuccess(tCommon("success"), t("publishedSuccess"));
      setShowPublish(false);
      await onChanged();
    } catch (err) {
      setActionError(
        resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToPublish"),
      );
    } finally {
      setPublishBusy(false);
    }
  }

  async function onPublishNow() {
    setActionError(null);
    setBusy(true);
    try {
      await publishAnnouncement(announcement.id);
      pushSuccess(tCommon("success"), t("publishedSuccess"));
      await onChanged();
    } catch (err) {
      setActionError(
        resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToPublish"),
      );
    } finally {
      setBusy(false);
    }
  }

  async function onUnpublish() {
    setActionError(null);
    setBusy(true);
    try {
      await unpublishAnnouncement(announcement.id);
      pushSuccess(tCommon("success"), t("unpublishedSuccess"));
      await onChanged();
    } catch (err) {
      setActionError(
        resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToUnpublish"),
      );
    } finally {
      setBusy(false);
    }
  }

  async function confirmDelete() {
    setDeleteBusy(true);
    setActionError(null);
    try {
      await deleteAnnouncement(announcement.id);
      pushSuccess(tCommon("success"), t("deletedSuccess"));
      setShowDelete(false);
      if (onDeleted) {
        await onDeleted();
      } else {
        router.push("/announcements/manage");
      }
    } catch (err) {
      setActionError(
        resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToDelete"),
      );
    } finally {
      setDeleteBusy(false);
    }
  }

  const detailHref = `/announcements/${encodeURIComponent(announcement.id)}?from=manage`;

  return (
    <div className="space-y-3">
      {actionError ? (
        <Alert
          tone="danger"
          title={t("actionFailed")}
          description={actionError}
        />
      ) : null}

      <div className="flex flex-nowrap items-center gap-2 overflow-x-auto pb-0.5">
        {showView ? (
          <Button
            type="button"
            size="sm"
            variant="secondary"
            className="shrink-0"
            disabled={busy}
            onClick={() => router.push(detailHref)}
          >
            {t("viewDetail")}
          </Button>
        ) : null}
        <Button
          type="button"
          size="sm"
          variant="secondary"
          className="shrink-0"
          disabled={busy}
          onClick={openEdit}
        >
          {tCommon("edit")}
        </Button>
        {isScheduled ? (
          <Button
            type="button"
            size="sm"
            className="shrink-0"
            disabled={busy}
            onClick={() => void onPublishNow()}
          >
            {t("publishNow")}
          </Button>
        ) : null}
        {isPublishedLive || isScheduled ? (
          <Button
            type="button"
            size="sm"
            variant="outline"
            className="shrink-0"
            disabled={busy}
            onClick={() => void onUnpublish()}
          >
            {t("unpublish")}
          </Button>
        ) : (
          <Button
            type="button"
            size="sm"
            className="shrink-0"
            disabled={busy}
            onClick={openPublish}
          >
            {t("publish")}
          </Button>
        )}
        <Button
          type="button"
          size="sm"
          variant="danger"
          className="shrink-0"
          disabled={busy}
          onClick={() => {
            setActionError(null);
            setShowDelete(true);
          }}
        >
          {tCommon("delete")}
        </Button>
      </div>

      <Modal
        open={editing}
        onClose={() => {
          setEditing(false);
          setEditAnnouncement(null);
        }}
        title={t("editTitle")}
        footer={
          <>
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                setEditing(false);
                setEditAnnouncement(null);
              }}
              disabled={savingEdit}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="submit"
              form="announcement-edit-form"
              loading={savingEdit}
              disabled={savingEdit}
            >
              {savingEdit ? tCommon("saving") : tCommon("save")}
            </Button>
          </>
        }
      >
        <form
          id="announcement-edit-form"
          className="space-y-[var(--ecmp-section-gap)]"
          onSubmit={(e) => void submitEdit(e)}
          noValidate
        >
          <AnnouncementFormFields
            values={editValues}
            fieldErrors={editErrors}
            onChange={(key, value) =>
              setEditValues((prev) => ({ ...prev, [key]: value }))
            }
            showStartAt
            attachmentSlot={
              editAnnouncement ? (
                <div className="space-y-3">
                  <p className="text-[length:var(--ecmp-font-label-size)] font-[number:var(--ecmp-font-label-weight)] text-ecmp-text-primary">
                    {t("attachmentsSectionTitle")}
                  </p>
                  <AnnouncementAttachmentManagedList
                    announcementId={editAnnouncement.id}
                    attachments={editAnnouncement.attachments ?? []}
                    onChange={() => void refreshEditAttachments()}
                  />
                  <AnnouncementAttachmentUploadControls
                    announcementId={editAnnouncement.id}
                    existingAttachmentIds={(
                      editAnnouncement.attachments ?? []
                    ).map((item) => item.id)}
                    onUploaded={(added) => void refreshEditAttachments(added)}
                  />
                </div>
              ) : null
            }
          />
        </form>
      </Modal>

      <Modal
        open={showPublish}
        onClose={() => setShowPublish(false)}
        title={t("publishConfirmTitle")}
        size="sm"
        footer={
          <>
            <Button
              type="button"
              variant="secondary"
              onClick={() => setShowPublish(false)}
              disabled={publishBusy}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              loading={publishBusy}
              disabled={publishBusy}
              onClick={() => void confirmPublish()}
            >
              {publishBusy
                ? t("publishing")
                : publishStartAt.trim()
                  ? t("publish")
                  : t("publishNow")}
            </Button>
          </>
        }
      >
        <div className="space-y-[var(--ecmp-form-gap)]">
          <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
            {t("publishConfirmDescription")}
          </p>
          <Input
            type="datetime-local"
            label={t("fieldStartAtLabel")}
            helper={t("fieldStartAtHelper")}
            value={publishStartAt}
            onChange={(e: ChangeEvent<HTMLInputElement>) => {
              setPublishStartAt(e.target.value);
              setPublishStartAtError(null);
            }}
            error={
              publishStartAtError === "announcementStartAtInvalid"
                ? t("announcementStartAtInvalid")
                : publishStartAtError === "announcementStartBeforeEnd"
                  ? t("announcementStartBeforeEnd")
                  : undefined
            }
          />
        </div>
      </Modal>

      <Modal
        open={showDelete}
        onClose={() => setShowDelete(false)}
        title={t("deleteConfirmTitle")}
        size="sm"
        footer={
          <>
            <Button
              type="button"
              variant="secondary"
              onClick={() => setShowDelete(false)}
              disabled={deleteBusy}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              variant="danger"
              loading={deleteBusy}
              disabled={deleteBusy}
              onClick={() => void confirmDelete()}
            >
              {deleteBusy ? tCommon("saving") : tCommon("delete")}
            </Button>
          </>
        }
      >
        <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
          {t("deleteConfirmDescription", { title: announcement.title })}
        </p>
      </Modal>
    </div>
  );
}
