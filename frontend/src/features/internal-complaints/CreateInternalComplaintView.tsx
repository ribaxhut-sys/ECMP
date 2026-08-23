"use client";

import { useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { formatDateTime24 } from "@/shared/utils/datetime";
import {
  Alert,
  Button,
  Card,
  CardBody,
  Input,
  Modal,
  ModalSection,
  PageContainer,
  PageHeader,
  Select,
  SectionHeader,
  type SelectOption,
} from "@/shared/ui";
import { useReasonPresets } from "@/shared/hooks";
import { ApiError } from "@/lib/api/client";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import { fetchBranches, type Branch } from "@/lib/api/branches";
import { fetchCmBatch1Complaints } from "@/lib/api/cmBatch1";
import {
  createInternalComplaint,
} from "@/lib/api/internalComplaints";
import { uploadAttachment } from "@/lib/api/attachments";
import { KnowledgeMentionTextarea } from "@/features/complaints/KnowledgeMentionTextarea";
import { PresetTextField } from "@/features/complaints/PresetTextField";
import {
  defaultInternalComplaintForm,
  isInternalComplaintFormValid,
  validateInternalComplaintForm,
  type InternalComplaintFormValues,
} from "./internalComplaintForm";
import {
  CATEGORY_LABEL_KEY,
  INTERNAL_CATEGORIES,
  INTERNAL_PRIORITIES,
  isInternalAgentFamily,
} from "./types";
import {
  looksLikeRelatedComplaintQuery,
  matchRelatedComplaint,
  mergeRelatedComplaintRefs,
  relatedComplaintFromListRow,
  resolveRelatedComplaintPayload,
  type RelatedComplaintRef,
} from "./relatedComplaintMatch";
import {
  CANONICAL_PUSAT_UNIT_CODE,
  filterTransferDestinations,
  formatUnitOptionLabel,
  isAdminFamily,
  isPusatUnitCode,
  resolveCreateSourceUnitCode,
} from "./transferDirection";
import { InternalComplaintFileStaging } from "./InternalComplaintAttachments";

const RELATED_DATALIST_ID = "internal-related-complaint-numbers";

/** Quick-fill presets for the transfer-request reason (PUBLIC setting, JSON array). */
const REQUEST_TRANSFER_PRESET_KEY =
  "internal_complaint.request_transfer_reason_presets";
const PRESET_KEYS = [REQUEST_TRANSFER_PRESET_KEY];

export function CreateInternalComplaintView() {
  const router = useRouter();
  const t = useTranslations("internalComplaints");
  const tCommon = useTranslations("common");
  const tPriority = useTranslations("priority");
  const tErrors = useTranslations("errors");
  const locale = useLocale();
  const { user, userId, roles, hasPermission } = useAuth();
  const canCreate = hasPermission("complaints:create");
  const canAssign = hasPermission("complaints:assign");

  const [values, setValues] = useState<InternalComplaintFormValues>(() =>
    defaultInternalComplaintForm(),
  );
  const [errors, setErrors] = useState<
    ReturnType<typeof validateInternalComplaintForm>
  >({});
  const [branches, setBranches] = useState<Branch[]>([]);
  const [relatedSuggestions, setRelatedSuggestions] = useState<
    RelatedComplaintRef[]
  >([]);
  const [saving, setSaving] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [createdTicket, setCreatedTicket] = useState<{
    id: string;
    number: string;
    uploadFail?: string;
  } | null>(null);
  const [stagedFiles, setStagedFiles] = useState<File[]>([]);
  const presets = useReasonPresets(PRESET_KEYS);

  useEffect(() => {
    fetchBranches(100)
      .then((res) => setBranches(res.data ?? []))
      .catch(() => setBranches([]));
  }, []);

  useEffect(() => {
    const agentOnly = isInternalAgentFamily(roles);
    const filters: {
      status: string;
      pageSize: number;
      createdBy?: string;
    } = { status: "OPEN", pageSize: 20 };
    if (agentOnly && userId) {
      filters.createdBy = userId;
    }
    fetchCmBatch1Complaints(filters)
      .then((res) => {
        setRelatedSuggestions(
          (res.data ?? [])
            .map(relatedComplaintFromListRow)
            .filter((row): row is RelatedComplaintRef => row !== null),
        );
      })
      .catch(() => setRelatedSuggestions([]));
  }, [roles, userId]);

  const relatedSuggestionsRef = useRef(relatedSuggestions);
  relatedSuggestionsRef.current = relatedSuggestions;

  const matchedRelated = useMemo(
    () => matchRelatedComplaint(values.relatedComplaintId, relatedSuggestions),
    [relatedSuggestions, values.relatedComplaintId],
  );

  useEffect(() => {
    const raw = values.relatedComplaintId.trim();
    if (!looksLikeRelatedComplaintQuery(raw)) return;
    const handle = window.setTimeout(() => {
      if (matchRelatedComplaint(raw, relatedSuggestionsRef.current)) return;
      const agentOnly = isInternalAgentFamily(roles);
      const filters: {
        status: string;
        pageSize: number;
        keyword: string;
        createdBy?: string;
      } = { status: "OPEN", pageSize: 10, keyword: raw };
      if (agentOnly && userId) {
        filters.createdBy = userId;
      }
      void fetchCmBatch1Complaints(filters)
        .then((res) => {
          const incoming = (res.data ?? [])
            .map(relatedComplaintFromListRow)
            .filter((row): row is RelatedComplaintRef => row !== null);
          if (incoming.length === 0) return;
          setRelatedSuggestions((prev) =>
            mergeRelatedComplaintRefs(prev, incoming),
          );
        })
        .catch(() => {
          /* preview stays hidden when lookup fails */
        });
    }, 300);
    return () => window.clearTimeout(handle);
  }, [roles, userId, values.relatedComplaintId]);

  function setField<K extends keyof InternalComplaintFormValues>(
    key: K,
    value: InternalComplaintFormValues[K],
  ): void {
    setValues((prev) => ({ ...prev, [key]: value }));
  }

  const categoryOptions: SelectOption[] = INTERNAL_CATEGORIES.map((category) => ({
    value: category,
    label: t(CATEGORY_LABEL_KEY[category]),
  }));
  const priorityOptions: SelectOption[] = INTERNAL_PRIORITIES.map((priority) => ({
    value: priority,
    label: tPriority(priority),
  }));
  const actorBranchCode = useMemo(() => {
    const branchId = user?.branchId;
    if (!branchId) return null;
    return branches.find((b) => b.id === branchId)?.code ?? null;
  }, [branches, user?.branchId]);

  const sourceUnitCode = useMemo(
    () =>
      resolveCreateSourceUnitCode(actorBranchCode, {
        treatMissingAsPusat: isAdminFamily(roles),
      }),
    [actorBranchCode, roles],
  );
  const fromPusat = isPusatUnitCode(sourceUnitCode);

  const pusatBranch = useMemo(
    () => branches.find((b) => isPusatUnitCode(b.code)) ?? null,
    [branches],
  );
  const pusatDestinationCode =
    pusatBranch?.code.trim() || CANONICAL_PUSAT_UNIT_CODE;

  useEffect(() => {
    if (fromPusat) return;
    setValues((prev) =>
      prev.destinationUnitId === pusatDestinationCode
        ? prev
        : { ...prev, destinationUnitId: pusatDestinationCode },
    );
  }, [fromPusat, pusatDestinationCode]);

  const transferDestinations = useMemo(
    () => filterTransferDestinations(branches, sourceUnitCode),
    [branches, sourceUnitCode],
  );

  const unitOptions: SelectOption[] = [
    { value: "", label: t("keepAtOwnerUnit") },
    ...transferDestinations.map((b) => ({
      value: b.code,
      label: formatUnitOptionLabel(b.code, b.name),
    })),
  ];

  function relatedLinkError(err: unknown): string {
    if (err instanceof ApiError) {
      if (
        err.code === "RELATED_COMPLAINT_NOT_FOUND" ||
        err.code === "NOT_FOUND"
      ) {
        return t("relatedComplaintNotFoundError");
      }
      if (err.code === "RELATED_COMPLAINT_CLOSED") {
        return t("relatedComplaintClosedError");
      }
      if (err.code === "RELATED_COMPLAINT_NOT_VISIBLE") {
        return t("relatedComplaintNotVisibleError");
      }
      return resolveApiErrorMessage(err, tErrors, tCommon, "validationError");
    }
    return t("submitFailed");
  }

  function goToCreatedTicket(id: string): void {
    router.push(`/internal/complaints/${encodeURIComponent(id)}`);
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (!canCreate || createdTicket) return;
    const related = resolveRelatedComplaintPayload(
      values.relatedComplaintId,
      relatedSuggestions,
    );
    const fieldErrors = validateInternalComplaintForm(values, {
      canAssign,
      requireRequestReason: !canAssign && fromPusat,
      relatedUnresolved: related.status === "unresolved",
    });
    setErrors(fieldErrors);
    if (!isInternalComplaintFormValid(fieldErrors)) return;

    setSaving(true);
    setSubmitError(null);
    try {
      const dest = values.destinationUnitId.trim();
      const created = await createInternalComplaint({
        subject: values.title.trim(),
        description: values.description.trim(),
        category: values.category || "OTHER",
        priority: values.priority,
        chronology: values.chronology.trim() || null,
        impact: values.impact.trim() || null,
        relatedComplaintId:
          related.status === "matched" || related.status === "literal"
            ? related.id
            : null,
        handlingUnitId: dest || null,
        requestReason:
          !canAssign && fromPusat && dest
            ? values.requestReason.trim() || null
            : null,
      });
      const id = created.data.complaintId;
      const number = created.data.complaintNumber?.trim() || id;
      const failed: string[] = [];
      for (const file of stagedFiles) {
        try {
          await uploadAttachment("InternalComplaint", id, file);
        } catch {
          failed.push(file.name);
        }
      }
      setCreatedTicket({
        id,
        number,
        uploadFail: failed.length > 0 ? failed.join(", ") : undefined,
      });
    } catch (err) {
      setSubmitError(relatedLinkError(err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <div className="mx-auto w-full max-w-4xl space-y-[var(--ecmp-section-gap)]">
        <PageHeader
          className="text-center md:flex-col md:items-center [&_ol]:justify-center [&_h1+div]:mx-auto"
          title={t("createTitle")}
          description={t("createDescription")}
          breadcrumbs={[
            { label: tCommon("home"), href: "/dashboard" },
            { label: t("title"), href: "/internal" },
            { label: t("listTitle"), href: "/internal/complaints" },
            { label: t("createTitle") },
          ]}
        />

        {!canCreate ? (
          <Alert
            tone="warning"
            title={t("createRestrictedTitle")}
            description={t("createAccessRestrictedDescription")}
          />
        ) : null}

        {submitError ? <Alert tone="danger" title={submitError} /> : null}

        <Card className="w-full">
          <CardBody>
            <form className="space-y-6" onSubmit={onSubmit}>
              <fieldset
                disabled={!canCreate || Boolean(createdTicket)}
                className="min-w-0 space-y-6 border-0 p-0"
              >
              <SectionHeader title={t("sectionBasics")} />
              <Input
                label={t("titleField")}
                value={values.title}
                onChange={(e) => setField("title", e.target.value)}
                error={errors.title ? t(errors.title) : undefined}
                required
              />
              <div className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] sm:grid-cols-2">
                <Select
                  label={t("category")}
                  options={categoryOptions}
                  value={values.category}
                  placeholder={t("categoryPlaceholder")}
                  onChange={(e) =>
                    setField(
                      "category",
                      e.target.value as InternalComplaintFormValues["category"],
                    )
                  }
                  error={errors.category ? t(errors.category) : undefined}
                  required
                />
                <Select
                  label={t("priority")}
                  options={priorityOptions}
                  value={values.priority}
                  onChange={(e) =>
                    setField(
                      "priority",
                      e.target.value as InternalComplaintFormValues["priority"],
                    )
                  }
                />
              </div>
              <div className="space-y-2">
              <Input
                label={t("relatedComplaint")}
                value={values.relatedComplaintId}
                onChange={(e) => setField("relatedComplaintId", e.target.value)}
                placeholder={t("relatedComplaintPlaceholder")}
                hint={t("relatedComplaintHint")}
                list={RELATED_DATALIST_ID}
                autoComplete="off"
                error={
                  errors.relatedComplaintId
                    ? t(errors.relatedComplaintId)
                    : undefined
                }
              />
              <datalist id={RELATED_DATALIST_ID}>
                {relatedSuggestions.map((row) => (
                  <option key={row.id} value={row.number} />
                ))}
              </datalist>
              {matchedRelated ? (
                <div
                  role="status"
                  aria-live="polite"
                  className="rounded-[var(--ecmp-radius-md)] border border-ecmp-border bg-ecmp-surface-sunken px-4 py-3"
                >
                  <dl className="grid gap-3 sm:grid-cols-3">
                    <div className="min-w-0">
                      <dt className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                        {t("subject")}
                      </dt>
                      <dd className="truncate text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                        {matchedRelated.subject || tCommon("emDash")}
                      </dd>
                    </div>
                    <div className="min-w-0">
                      <dt className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                        {t("createdAt")}
                      </dt>
                      <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                        {formatDateTime24(
                          matchedRelated.createdAt,
                          locale,
                          tCommon("emDash"),
                        )}
                      </dd>
                    </div>
                    <div className="min-w-0">
                      <dt className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                        {t("createdBy")}
                      </dt>
                      <dd className="truncate text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                        {matchedRelated.createdByName || tCommon("emDash")}
                      </dd>
                    </div>
                  </dl>
                </div>
              ) : null}
              </div>
              {fromPusat ? (
                <Select
                  label={t("initialTransferUnit")}
                  options={unitOptions}
                  value={values.destinationUnitId}
                  onChange={(e) => setField("destinationUnitId", e.target.value)}
                  hint={
                    canAssign
                      ? t("initialTransferHint")
                      : t("transferRequestHint")
                  }
                />
              ) : (
                <Input
                  name="destinationUnitId"
                  label={t("initialTransferUnit")}
                  value={formatUnitOptionLabel(
                    pusatDestinationCode,
                    pusatBranch?.name,
                  )}
                  readOnly
                  hint={t("destinationLockedToPusatHint")}
                />
              )}
              {!canAssign && fromPusat && values.destinationUnitId ? (
                <>
                  <PresetTextField
                    presets={presets[REQUEST_TRANSFER_PRESET_KEY] ?? []}
                    id="internal-request-reason"
                    label={t("requestReason")}
                    value={values.requestReason}
                    onChange={(next) => setField("requestReason", next)}
                    error={
                      errors.requestReason ? t(errors.requestReason) : undefined
                    }
                    hint={t("requestReasonHint")}
                    required
                  />
                </>
              ) : null}

              <SectionHeader title={t("sectionNarrative")} />
              <KnowledgeMentionTextarea
                id="internal-description"
                label={t("description")}
                value={values.description}
                onChange={(next) => setField("description", next)}
                error={errors.description ? t(errors.description) : undefined}
                required
              />
              <KnowledgeMentionTextarea
                id="internal-chronology"
                label={t("chronology")}
                value={values.chronology}
                onChange={(next) => setField("chronology", next)}
              />
              <KnowledgeMentionTextarea
                id="internal-impact"
                label={t("impact")}
                value={values.impact}
                onChange={(next) => setField("impact", next)}
              />
              <InternalComplaintFileStaging
                files={stagedFiles}
                onChange={setStagedFiles}
                disabled={!canCreate || Boolean(createdTicket) || saving}
              />
              </fieldset>

              <div className="flex flex-wrap justify-center gap-3">
                <Button
                  type="submit"
                  disabled={saving || !canCreate || Boolean(createdTicket)}
                >
                  {saving ? tCommon("loading") : t("submitComplaint")}
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => router.push("/internal/complaints")}
                >
                  {tCommon("cancel")}
                </Button>
              </div>
            </form>
          </CardBody>
        </Card>
      </div>

      <Modal
        open={Boolean(createdTicket)}
        onClose={() => {
          if (createdTicket) goToCreatedTicket(createdTicket.id);
        }}
        title={t("submittedTitle")}
        size="sm"
        footer={
          <Button
            type="button"
            onClick={() => {
              if (createdTicket) goToCreatedTicket(createdTicket.id);
            }}
          >
            {t("submittedView")}
          </Button>
        }
      >
        <ModalSection>
          <p className="text-sm text-ecmp-text-primary">
            {t("submittedBody", {
              number: createdTicket?.number ?? tCommon("emDash"),
            })}
          </p>
          {createdTicket?.uploadFail ? (
            <p className="mt-2 text-sm text-ecmp-danger">
              {t("attachmentsPartialFail", {
                detail: createdTicket.uploadFail,
              })}
            </p>
          ) : null}
        </ModalSection>
      </Modal>
    </PageContainer>
  );
}
