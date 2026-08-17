"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ChangeEvent,
} from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  fetchBranches,
  type Branch,
  type CmBatch1ComplaintBrief,
} from "@/lib/api";
import { translateValidationErrors, resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import {
  Alert,
  Button,
  Card,
  CardBody,
  Input,
  PageContainer,
  PageHeader,
  SectionHeader,
} from "@/shared/ui";
import { CustomerSearchPanel } from "./CustomerSearchPanel";
import { ActiveComplaintsBanner } from "./ActiveComplaintsBanner";
import { KnowledgeMentionTextarea } from "./KnowledgeMentionTextarea";
import { StagingAttachmentsPanel } from "./StagingAttachmentsPanel";
import {
  createEmptyComplaintForm,
  newCmBatch1StagingToken,
  validateCmBatch1CreateForm,
  type CreateComplaintFieldErrors,
  type CreateComplaintFormValues,
} from "./createComplaintForm";
import {
  clearEscalateIntakeDraft,
  consumeIntakeFormResume,
  peekEscalateIntakeDraft,
  stashEscalateIntakeDraft,
} from "./escalateIntakeDraft";
import {
  MAX_EXTRA_INTAKE_CASES,
  emptyExtraCaseDraft,
  sanitizeExtraCaseDrafts,
  type IntakeExtraCaseDraft,
} from "./intakeCaseDrafts";

/**
 * Create Complaint — Mode A Batch-1 Aggregate intake.
 * This screen only collects the draft; Lanjut opens per-Case decisions.
 */
export function CreateComplaintView() {
  const router = useRouter();
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  const tValidation = useTranslations("validation");
  const tErrors = useTranslations("errors");
  const { user, hasPermission } = useAuth();
  const canCreate = hasPermission("complaints:create");
  const officerBranchId = user?.branchId ?? null;

  const [values, setValues] = useState<CreateComplaintFormValues>(() =>
    createEmptyComplaintForm({ branchId: officerBranchId, channel: "BRANCH" }),
  );
  const [errors, setErrors] = useState<CreateComplaintFieldErrors>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [infoMessage, setInfoMessage] = useState<string | null>(null);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [branchesError, setBranchesError] = useState<string | null>(null);
  const [overrideJustification, setOverrideJustification] = useState<
    string | null
  >(null);
  const [stagingToken, setStagingToken] = useState(() =>
    newCmBatch1StagingToken(),
  );
  const [hasStagedAttachments, setHasStagedAttachments] = useState(false);
  const [stagingBusy, setStagingBusy] = useState(false);
  /** False until session draft restore (if any) has been applied. */
  const [formReady, setFormReady] = useState(false);
  const [activeComplaints, setActiveComplaints] = useState<
    CmBatch1ComplaintBrief[]
  >([]);
  const [extraCaseDrafts, setExtraCaseDrafts] = useState<
    IntakeExtraCaseDraft[]
  >([]);

  useEffect(() => {
    // Always restore stashed intake draft when present (Lanjut → Back /
    // breadcrumb / browser Back). Do not gate on the legacy resume flag —
    // that flag was one-shot and broke breadcrumb + React Strict remounts.
    const draft = peekEscalateIntakeDraft();
    if (draft) {
      setValues(draft.values);
      setStagingToken(
        draft.stagingToken.trim() || newCmBatch1StagingToken(),
      );
      setHasStagedAttachments(Boolean(draft.hasStagedAttachments));
      setOverrideJustification(draft.overrideJustification);
      setExtraCaseDrafts(sanitizeExtraCaseDrafts(draft.extraCaseDrafts));
    }
    consumeIntakeFormResume(); // clear legacy flag if still present
    setFormReady(true);
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setBranchesError(null);
      try {
        const res = await fetchBranches(100);
        if (cancelled) return;
        setBranches(res.data);
        const locked =
          (officerBranchId
            ? res.data.find((b) => b.id === officerBranchId)
            : null) ??
          res.data.find((b) => b.code.toUpperCase() === "PUSAT") ??
          null;
        if (locked) {
          setValues((prev) => ({
            ...prev,
            branchId: locked.id,
            channel: prev.channel || "BRANCH",
          }));
        }
      } catch (err) {
        if (!cancelled) {
          setBranchesError(
            resolveApiErrorMessage(err, tErrors, tCommon, "unexpectedError") ||
              t("unableToLoadBranches"),
          );
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [officerBranchId, t, tCommon, tErrors]);

  const lockedBranch = useMemo(() => {
    if (officerBranchId) {
      return branches.find((b) => b.id === officerBranchId) ?? null;
    }
    return branches.find((b) => b.code.toUpperCase() === "PUSAT") ?? null;
  }, [officerBranchId, branches]);

  const updateField = useCallback(
    <K extends keyof CreateComplaintFormValues>(
      key: K,
      value: CreateComplaintFormValues[K],
    ) => {
      setValues((prev) => ({ ...prev, [key]: value }));
      setErrors((prev) => {
        if (!prev[key]) return prev;
        const next = { ...prev };
        delete next[key];
        return next;
      });
    },
    [],
  );

  const onCustomerConfirmed = useCallback(
    (payload: { customerId: string; displayName: string }) => {
      setValues((prev) => ({
        ...prev,
        customerId: payload.customerId,
        customerName: payload.displayName,
      }));
      setErrors((prev) => {
        const next = { ...prev };
        delete next.customerId;
        delete next.customerName;
        return next;
      });
      setOverrideJustification(null);
      setInfoMessage(null);
    },
    [],
  );

  const onCustomerCleared = useCallback(() => {
    setValues((prev) => ({
      ...prev,
      customerId: "",
      customerName: "",
    }));
    setActiveComplaints([]);
    setOverrideJustification(null);
  }, []);

  if (!formReady) {
    return null;
  }

  function onTextChange(
    key: keyof CreateComplaintFormValues,
  ): (
    event: ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >,
  ) => void {
    return (event) => {
      updateField(
        key,
        event.target.value as CreateComplaintFormValues[typeof key],
      );
      setOverrideJustification(null);
    };
  }

  function onCancel(): void {
    clearEscalateIntakeDraft();
    router.push("/complaints");
  }

  function validateIntakeForm(): CreateComplaintFieldErrors {
    const nextErrors = translateValidationErrors(
      validateCmBatch1CreateForm(values),
      tValidation,
    );
    // Catatan wajib sebelum Lanjut (putusan per Case di langkah berikutnya).
    if (!values.resolution.trim() && !nextErrors.resolution) {
      nextErrors.resolution = tValidation("intakeNoteRequired");
    }
    return nextErrors;
  }

  /** Lanjut — putusan per Case dipilih di langkah berikutnya. */
  function continueToPriority(): void {
    if (!canCreate) return;
    setSubmitError(null);
    setInfoMessage(null);
    const nextErrors = validateIntakeForm();
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) {
      const firstKey = Object.keys(nextErrors)[0];
      const el = firstKey ? document.getElementById(firstKey) : null;
      el?.focus();
      return;
    }
    stashEscalateIntakeDraft({
      values,
      stagingToken,
      hasStagedAttachments,
      overrideJustification,
      recordingUnitCode: lockedBranch?.code ?? null,
      extraCaseDrafts,
    });
    router.push("/complaints/new/escalate");
  }

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={t("create")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title"), href: "/complaints" },
          { label: tCommon("create") },
        ]}
        description={t("batch1IntakeDescription")}
      />

      {!canCreate ? (
        <Alert
          tone="warning"
          title={t("createRestrictedTitle")}
          description={t("createAccessRestrictedDescription")}
        />
      ) : null}

      <form
        noValidate
        onSubmit={(event) => {
          event.preventDefault();
        }}
        aria-label={t("createFormAriaLabel")}
        className="space-y-[var(--ecmp-section-gap)]"
      >
        {submitError ? (
          <Alert
            tone="danger"
            title={t("couldNotCreate")}
            description={submitError}
          />
        ) : null}

        {infoMessage ? (
          <Alert tone="info" title={t("notice")} description={infoMessage} />
        ) : null}

        {branchesError ? (
          <Alert
            tone="danger"
            title={t("couldNotLoadBranches")}
            description={branchesError}
          />
        ) : null}

        <fieldset
          disabled={!canCreate}
          className="min-w-0 space-y-[var(--ecmp-section-gap)] border-0 p-0"
        >
        <CustomerSearchPanel
          confirmedCustomerId={values.customerId}
          confirmedDisplayName={values.customerName}
          onConfirmed={onCustomerConfirmed}
          onCleared={onCustomerCleared}
          onActiveComplaintsChange={setActiveComplaints}
          disabled={stagingBusy}
        />

        {values.customerId.trim() ? (
          <ActiveComplaintsBanner
            complaints={activeComplaints}
            disabled={stagingBusy}
          />
        ) : null}

        {(errors.customerId || errors.customerName) && !values.customerId ? (
          <Alert
            tone="danger"
            title={t("customerRequiredTitle")}
            description={
              errors.customerId ||
              errors.customerName ||
              t("confirmCustomerBeforeCreating")
            }
          />
        ) : null}

        <section className="space-y-[var(--ecmp-panel-gap)]">
          <SectionHeader
            id="section-complaint-info"
            title={t("complaintInformation")}
            description={t("complaintInformationDescription")}
          />
          <Card>
            <CardBody>
              <fieldset
                aria-labelledby="section-complaint-info"
                className="grid grid-cols-1 gap-[var(--ecmp-form-gap)]"
              >
                <legend className="sr-only">{t("complaintInformation")}</legend>
                <Input
                  name="subject"
                  id="subject"
                  label={t("subject")}
                  required
                  maxLength={200}
                  value={values.subject}
                  onChange={onTextChange("subject")}
                  error={errors.subject}
                  aria-required="true"
                  autoComplete="off"
                />
                <KnowledgeMentionTextarea
                  name="description"
                  id="description"
                  label={t("intakeCaseNLabel", { n: 1 })}
                  required
                  rows={5}
                  maxLength={5000}
                  value={values.description}
                  onChange={(next) => updateField("description", next)}
                  error={errors.description}
                  hint={t("intakeCase1Hint", {
                    count: values.description.trim().length,
                    max: 5000,
                  })}
                  disabled={stagingBusy}
                />
                <div className="space-y-3">
                  {extraCaseDrafts.map((draft, index) => (
                    <div
                      key={draft.id}
                      className="space-y-2 rounded-[var(--ecmp-radius-md)] border border-ecmp-border p-3"
                    >
                      <div className="flex justify-end">
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          disabled={stagingBusy}
                          onClick={() => {
                            const filled = draft.description.trim().length > 0;
                            if (
                              filled &&
                              !window.confirm(t("intakeExtraCaseDiscardConfirm"))
                            ) {
                              return;
                            }
                            setExtraCaseDrafts((prev) =>
                              prev.filter((item) => item.id !== draft.id),
                            );
                          }}
                        >
                          {tCommon("cancel")}
                        </Button>
                      </div>
                      <KnowledgeMentionTextarea
                        name={`extraCase-${draft.id}`}
                        id={`extraCase-${draft.id}`}
                        label={t("intakeCaseNLabel", { n: index + 2 })}
                        rows={4}
                        maxLength={5000}
                        value={draft.description}
                        onChange={(next) => {
                          setExtraCaseDrafts((prev) =>
                            prev.map((item) =>
                              item.id === draft.id
                                ? { ...item, description: next }
                                : item,
                            ),
                          );
                        }}
                        hint={t("charCounter", {
                          count: draft.description.trim().length,
                          max: 5000,
                        })}
                        disabled={stagingBusy}
                      />
                    </div>
                  ))}
                  {extraCaseDrafts.length < MAX_EXTRA_INTAKE_CASES ? (
                    <Button
                      type="button"
                      variant="outline"
                      disabled={stagingBusy}
                      onClick={() =>
                        setExtraCaseDrafts((prev) => [
                          ...prev,
                          emptyExtraCaseDraft(),
                        ])
                      }
                    >
                      {t("penangananAddCase")}
                    </Button>
                  ) : (
                    <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                      {t("intakeExtraCaseMax")}
                    </p>
                  )}
                  <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                    {t("intakeExtraCaseRegisterHint")}
                  </p>
                </div>
                <KnowledgeMentionTextarea
                  name="resolution"
                  id="resolution"
                  label={t("intakeNoteLabel")}
                  rows={5}
                  maxLength={5000}
                  value={values.resolution}
                  onChange={(next) => {
                    updateField("resolution", next);
                    setOverrideJustification(null);
                  }}
                  error={errors.resolution}
                  hint={t("intakeNoteHint", {
                    count: values.resolution.trim().length,
                    max: 5000,
                  })}
                  disabled={stagingBusy}
                />
              </fieldset>
            </CardBody>
          </Card>
        </section>

        {overrideJustification ? (
          <Alert
            tone="warning"
            title={t("duplicateOverrideArmed")}
            description={t("duplicateOverrideArmedDescription")}
          />
        ) : null}

        <StagingAttachmentsPanel
          stagingToken={stagingToken}
          customerId={values.customerId}
          disabled={stagingBusy}
          onStagingTokenResolved={setStagingToken}
          onHasStagedChange={setHasStagedAttachments}
          onBusyChange={setStagingBusy}
        />
        </fieldset>

        <div className="flex flex-col-reverse gap-[var(--ecmp-form-gap)] border-t border-ecmp-border pt-[var(--ecmp-panel-gap)] sm:flex-row sm:flex-wrap sm:justify-end">
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={stagingBusy}
            aria-label={t("backAriaLabel")}
          >
            {tCommon("back")}
          </Button>
          <Button
            type="button"
            disabled={!canCreate || stagingBusy}
            onClick={continueToPriority}
            aria-label={t("submitRegisterContinueAriaLabel")}
          >
            {t("submitRegisterContinue")}
          </Button>
        </div>
      </form>
    </PageContainer>
  );
}
