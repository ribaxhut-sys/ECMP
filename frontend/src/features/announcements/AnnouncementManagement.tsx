"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type FormEvent,
} from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  createAnnouncement,
  deleteAnnouncement,
  fetchAnnouncement,
  fetchAnnouncements,
  fetchUsers,
  publishAnnouncement,
  updateAnnouncement,
} from "@/lib/api";
import type {
  Announcement,
  AnnouncementAttachment,
  AnnouncementEffectiveStatus,
} from "@/lib/api/types";
import { formatDateTime } from "@/i18n/formatting";
import { useLocaleContext } from "@/shared/i18n";
import {
  Alert,
  Button,
  Card,
  CardBody,
  Empty,
  ErrorState,
  QuickFilters,
  SectionHeader,
  Skeleton,
} from "@/shared/ui";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { useToast } from "@/shared/providers";
import {
  AnnouncementAttachmentManagedList,
  AnnouncementAttachmentUploadControls,
} from "./AnnouncementAttachmentManager";
import {
  AnnouncementPriorityBadge,
  AnnouncementStatusBadge,
} from "./AnnouncementBadges";
import { AnnouncementFormFields } from "./AnnouncementFormFields";
import { AnnouncementManageActions } from "./AnnouncementManageActions";
import {
  createEmptyAnnouncementForm,
  toAnnouncementCreateRequest,
  toAnnouncementPublishRequest,
  validateAnnouncementForm,
  type AnnouncementFieldErrors,
  type AnnouncementFormValues,
} from "./announcementForm";

type StatusFilter = "ALL" | AnnouncementEffectiveStatus;

const STATUS_FILTERS: readonly StatusFilter[] = [
  "ALL",
  "DRAFT",
  "SCHEDULED",
  "PUBLISHED",
  "EXPIRED",
  "ARCHIVED",
] as const;

function statusFilterLabelKey(
  status: Exclude<StatusFilter, "ALL">,
):
  | "statusDraft"
  | "statusScheduled"
  | "statusPublished"
  | "statusExpired"
  | "statusArchived" {
  switch (status) {
    case "SCHEDULED":
      return "statusScheduled";
    case "PUBLISHED":
      return "statusPublished";
    case "EXPIRED":
      return "statusExpired";
    case "ARCHIVED":
      return "statusArchived";
    default:
      return "statusDraft";
  }
}

/**
 * Kelola Pengumuman — list + create.
 * List follows the intake-history pattern: status chips, one-line summary;
 * click row to expand full body, attachment count, and manage actions.
 * Sort is always createdAt newest-first (management work queue).
 */
export function AnnouncementManagement() {
  const router = useRouter();
  const t = useTranslations("announcements");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const { hasPermission } = useAuth();
  const { locale } = useLocaleContext();
  const { pushSuccess } = useToast();
  const canManage = hasPermission("announcement:manage");

  const [rows, setRows] = useState<Announcement[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [creatorNames, setCreatorNames] = useState<Record<string, string>>({});
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("ALL");

  const [showCreate, setShowCreate] = useState(false);
  const [createValues, setCreateValues] = useState<AnnouncementFormValues>(
    createEmptyAnnouncementForm,
  );
  const [createErrors, setCreateErrors] = useState<AnnouncementFieldErrors>({});
  const [creating, setCreating] = useState<"draft" | "publish" | null>(null);
  // Draft-parent attachment flow (business decision, LOCKED — attachments
  // must be addable directly from Create, never a separate "create then
  // edit" trip): a DRAFT is created silently the first time the user adds
  // an attachment while the create form is open, and reused for the actual
  // Save/Publish. If the form is closed without saving, this draft is
  // cleaned up (deleted) so it never lingers as an orphan.
  const [createDraft, setCreateDraft] = useState<Announcement | null>(null);
  const [addingCreateAttachment, setAddingCreateAttachment] = useState(false);
  const [autoOpenCreatePicker, setAutoOpenCreatePicker] = useState(false);

  const load = useCallback(async (opts?: { silent?: boolean }) => {
    if (!canManage) {
      setLoading(false);
      setRows([]);
      return;
    }
    // Silent refresh keeps expand/edit UI mounted — a full skeleton remount
    // was wiping attachment state right after upload.
    if (!opts?.silent) {
      setLoading(true);
    }
    setLoadError(null);
    try {
      const res = await fetchAnnouncements();
      setRows(res.data);
    } catch (err) {
      setRows([]);
      setLoadError(
        resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToLoad"),
      );
    } finally {
      if (!opts?.silent) {
        setLoading(false);
      }
    }
  }, [canManage, t, tCommon, tErrors]);

  useEffect(() => {
    void load();
  }, [load]);

  function patchRow(next: Announcement) {
    setRows((prev) =>
      prev.map((row) => (row.id === next.id ? { ...row, ...next } : row)),
    );
  }

  // "Pembuat" — best-effort id → name lookup (users:read, already held by
  // all three manage roles). Failure just falls back to a short id.
  useEffect(() => {
    if (!canManage) return;
    let cancelled = false;
    fetchUsers({ pageSize: 100 })
      .then((res) => {
        if (cancelled) return;
        const byId: Record<string, string> = {};
        for (const user of res.data) byId[user.id] = user.fullName;
        setCreatorNames(byId);
      })
      .catch(() => {
        if (!cancelled) setCreatorNames({});
      });
    return () => {
      cancelled = true;
    };
  }, [canManage]);

  function creatorLabel(userId: string | null): string {
    if (!userId) return tCommon("emDash");
    return creatorNames[userId] ?? `${userId.slice(0, 8)}…`;
  }

  function resolveFieldErrors(
    values: AnnouncementFormValues,
  ): AnnouncementFieldErrors {
    return validateAnnouncementForm(values);
  }

  async function ensureCreateDraft(): Promise<Announcement | null> {
    if (createDraft) return createDraft;
    const errors = resolveFieldErrors(createValues);
    setCreateErrors(errors);
    if (Object.keys(errors).length > 0) return null;

    setAddingCreateAttachment(true);
    try {
      const created = await createAnnouncement(
        toAnnouncementCreateRequest(createValues),
      );
      const draft = {
        ...created.data,
        attachments: created.data.attachments ?? [],
        attachmentCount: created.data.attachmentCount ?? 0,
      };
      setCreateDraft(draft);
      setAutoOpenCreatePicker(true);
      // Draft is now on the management list — keep counts in sync without remount.
      void load({ silent: true });
      return draft;
    } catch (err) {
      setActionError(
        resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToSave"),
      );
      return null;
    } finally {
      setAddingCreateAttachment(false);
    }
  }

  async function onCreateAttachmentsChanged(
    announcementId: string,
    added: AnnouncementAttachment[] = [],
  ) {
    setCreateDraft((prev) => {
      if (!prev || prev.id !== announcementId) return prev;
      const currentAttachments = prev.attachments ?? [];
      if (added.length === 0) return prev;
      const seen = new Set(currentAttachments.map((item) => item.id));
      const merged = [
        ...currentAttachments,
        ...added.filter((item) => !seen.has(item.id)),
      ];
      return {
        ...prev,
        attachments: merged,
        attachmentCount: merged.length,
      };
    });
    try {
      const res = await fetchAnnouncement(announcementId);
      const fresh = {
        ...res.data,
        attachments: res.data.attachments ?? [],
        attachmentCount:
          res.data.attachmentCount ?? res.data.attachments?.length ?? 0,
      };
      setCreateDraft(fresh);
      patchRow(fresh);
    } catch {
      await load({ silent: true });
    }
  }

  function resetCreateForm() {
    setCreateValues(createEmptyAnnouncementForm());
    setCreateErrors({});
    setCreateDraft(null);
    setAutoOpenCreatePicker(false);
  }

  async function closeCreateForm() {
    if (createDraft) {
      try {
        await deleteAnnouncement(createDraft.id);
      } catch {
        // best-effort cleanup
      }
    }
    resetCreateForm();
    setShowCreate(false);
  }

  async function submitCreate(mode: "draft" | "publish") {
    setActionError(null);
    const errors = resolveFieldErrors(createValues);
    setCreateErrors(errors);
    if (Object.keys(errors).length > 0) return;

    setCreating(mode);
    try {
      const request = toAnnouncementCreateRequest(createValues);
      const id = createDraft
        ? (await updateAnnouncement(createDraft.id, request)).data.id
        : (await createAnnouncement(request)).data.id;
      if (mode === "publish") {
        await publishAnnouncement(
          id,
          toAnnouncementPublishRequest(createValues.startAt),
        );
      }
      resetCreateForm();
      setShowCreate(false);
      pushSuccess(
        tCommon("success"),
        mode === "publish" ? t("publishedSuccess") : t("draftSavedSuccess"),
      );
      await load();
    } catch (err) {
      setActionError(
        resolveApiErrorMessage(err, tErrors, tCommon) || t("unableToSave"),
      );
    } finally {
      setCreating(null);
    }
  }

  function onCreateSubmit(event: FormEvent) {
    event.preventDefault();
    void submitCreate("draft");
  }

  const statusCounts = useMemo(() => {
    const counts: Record<StatusFilter, number> = {
      ALL: rows.length,
      DRAFT: 0,
      SCHEDULED: 0,
      PUBLISHED: 0,
      EXPIRED: 0,
      ARCHIVED: 0,
    };
    for (const row of rows) {
      counts[row.effectiveStatus] += 1;
    }
    return counts;
  }, [rows]);

  const statusFilterOptions = useMemo(
    () =>
      STATUS_FILTERS.map((id) => ({
        id,
        label:
          id === "ALL" ? t("filterStatusAll") : t(statusFilterLabelKey(id)),
        active: statusFilter === id,
        count: statusCounts[id],
      })),
    [statusCounts, statusFilter, t],
  );

  const filteredRows = useMemo(() => {
    const sorted = [...rows].sort(
      (a, b) =>
        new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
    );
    if (statusFilter === "ALL") return sorted;
    return sorted.filter((row) => row.effectiveStatus === statusFilter);
  }, [rows, statusFilter]);

  if (!canManage) {
    return (
      <Empty
        title={tCommon("accessRestricted")}
        description={t("accessRestrictedDescription")}
        primaryAction={{
          label: tCommon("goHome"),
          onClick: () => router.push("/dashboard"),
        }}
      />
    );
  }

  return (
    <section className="space-y-[var(--ecmp-panel-gap)]">
      <SectionHeader
        title={t("managementTitle")}
        description={t("managementDescription")}
        actions={
          <Button
            type="button"
            className="min-h-[var(--ecmp-touch-min)]"
            onClick={() => {
              setActionError(null);
              if (showCreate) {
                void closeCreateForm();
              } else {
                setShowCreate(true);
              }
            }}
          >
            {showCreate ? tCommon("cancel") : t("createAnnouncement")}
          </Button>
        }
      />

      <Card>
        <CardBody className="space-y-[var(--ecmp-panel-gap)]">
          {actionError ? (
            <Alert
              tone="danger"
              title={t("actionFailed")}
              description={actionError}
            />
          ) : null}

          {showCreate ? (
            <form
              className="space-y-[var(--ecmp-form-gap)] rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface-sunken p-[var(--ecmp-panel-gap)]"
              onSubmit={onCreateSubmit}
              noValidate
            >
              <AnnouncementFormFields
                values={createValues}
                fieldErrors={createErrors}
                onChange={(key, value) =>
                  setCreateValues((prev) => ({ ...prev, [key]: value }))
                }
                attachmentSlot={
                  <div className="space-y-3">
                    <p className="text-[length:var(--ecmp-font-label-size)] font-[number:var(--ecmp-font-label-weight)] text-ecmp-text-primary">
                      {t("attachmentsSectionTitle")}
                    </p>
                    {createDraft ? (
                      <>
                        <AnnouncementAttachmentManagedList
                          announcementId={createDraft.id}
                          attachments={createDraft.attachments ?? []}
                          onChange={() =>
                            void onCreateAttachmentsChanged(createDraft.id)
                          }
                        />
                        <AnnouncementAttachmentUploadControls
                          announcementId={createDraft.id}
                          autoOpen={autoOpenCreatePicker}
                          existingAttachmentIds={(
                            createDraft.attachments ?? []
                          ).map((item) => item.id)}
                          onUploaded={(added) => {
                            setAutoOpenCreatePicker(false);
                            void onCreateAttachmentsChanged(
                              createDraft.id,
                              added,
                            );
                          }}
                        />
                      </>
                    ) : (
                      <Button
                        type="button"
                        variant="secondary"
                        size="sm"
                        loading={addingCreateAttachment}
                        disabled={addingCreateAttachment}
                        onClick={() => void ensureCreateDraft()}
                      >
                        {addingCreateAttachment
                          ? t("saving")
                          : t("addAttachment")}
                      </Button>
                    )}
                  </div>
                }
              />
              <div className="flex flex-wrap justify-end gap-2">
                <Button
                  type="submit"
                  variant="secondary"
                  disabled={creating !== null}
                  loading={creating === "draft"}
                >
                  {creating === "draft" ? t("saving") : t("saveDraft")}
                </Button>
                <Button
                  type="button"
                  disabled={creating !== null}
                  loading={creating === "publish"}
                  onClick={() => void submitCreate("publish")}
                >
                  {creating === "publish" ? t("publishing") : t("publish")}
                </Button>
              </div>
            </form>
          ) : null}

          {loadError ? (
            <ErrorState
              title={t("unableToLoad")}
              message={loadError}
              onRetry={() => void load()}
            />
          ) : null}

          {loading ? (
            <Skeleton rows={5} />
          ) : !loadError && rows.length === 0 ? (
            <Empty title={t("listEmpty")} description={t("historyEmptyDescription")} />
          ) : !loadError && filteredRows.length === 0 ? (
            <div className="space-y-[var(--ecmp-form-gap)]">
              <QuickFilters
                label={t("filterStatusLabel")}
                options={statusFilterOptions}
                onSelect={(id) => {
                  setStatusFilter(id as StatusFilter);
                  setExpandedId(null);
                }}
              />
              <Empty
                title={t("listEmptyFiltered")}
                description={t("managementDescription")}
              />
            </div>
          ) : !loadError ? (
            <div className="space-y-[var(--ecmp-form-gap)]">
              <QuickFilters
                label={t("filterStatusLabel")}
                options={statusFilterOptions}
                onSelect={(id) => {
                  setStatusFilter(id as StatusFilter);
                  setExpandedId(null);
                }}
              />
            <ol
              className="space-y-[var(--ecmp-form-gap)]"
              aria-label={t("tableCaption")}
            >
              {filteredRows.map((row, index) => {
                const open = expandedId === row.id;
                const body = row.body.trim();
                const detailId = `announcement-manage-detail-${row.id}`;
                return (
                  <li
                    key={row.id}
                    className={`rounded-[var(--ecmp-radius-md)] border border-ecmp-border ${
                      index % 2 === 0
                        ? "bg-ecmp-surface"
                        : "bg-ecmp-surface-sunken"
                    }`}
                  >
                    <button
                      type="button"
                      onClick={() =>
                        setExpandedId((current) =>
                          current === row.id ? null : row.id,
                        )
                      }
                      aria-expanded={open}
                      aria-controls={detailId}
                      className="flex w-full items-center gap-3 rounded-[var(--ecmp-radius-md)] p-3 text-left hover:bg-ecmp-hover focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ecmp-primary"
                    >
                      <AnnouncementStatusBadge status={row.effectiveStatus} />
                      <span className="flex min-w-0 flex-1 flex-wrap items-center gap-x-3 gap-y-1">
                        <span className="shrink-0 font-medium tabular-nums text-ecmp-text-secondary">
                          {row.referenceNumber}
                        </span>
                        <span className="line-clamp-1 min-w-0 flex-1 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                          <span className="font-medium">{row.title}</span>
                          {body ? (
                            <span className="font-normal text-ecmp-text-secondary">
                              {" — "}
                              {body}
                            </span>
                          ) : null}
                        </span>
                        <AnnouncementPriorityBadge priority={row.priority} />
                        <span className="shrink-0 text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                          {creatorLabel(row.createdBy)}
                        </span>
                        <span className="shrink-0 text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                          {row.publishedAt
                            ? formatDateTime(row.publishedAt, locale)
                            : tCommon("emDash")}
                        </span>
                      </span>
                      <span className="shrink-0 text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                        {open ? t("listHideDetail") : t("listShowDetail")}
                      </span>
                    </button>
                    {open ? (
                      <div
                        id={detailId}
                        className="space-y-3 border-t border-ecmp-border px-3 pb-3 pt-2"
                      >
                        <p className="max-h-48 overflow-y-auto whitespace-pre-wrap text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                          {body || tCommon("emDash")}
                        </p>
                        <div className="space-y-1 text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                          <p>
                            {t("listAttachmentCount", {
                              count: row.attachmentCount,
                            })}
                          </p>
                          {(row.attachments ?? []).length > 0 ? (
                            <ul className="list-disc space-y-0.5 pl-5">
                              {(row.attachments ?? []).map((att) => (
                                <li key={att.id}>{att.fileName}</li>
                              ))}
                            </ul>
                          ) : null}
                        </div>
                        <AnnouncementManageActions
                          announcement={row}
                          showView
                          onChanged={(opts) => void load(opts)}
                          onDeleted={async () => {
                            setExpandedId(null);
                            await load({ silent: true });
                          }}
                        />
                      </div>
                    ) : null}
                  </li>
                );
              })}
            </ol>
            </div>
          ) : null}
        </CardBody>
      </Card>
    </section>
  );
}
