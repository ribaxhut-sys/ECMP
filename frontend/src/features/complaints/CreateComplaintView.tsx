"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ChangeEvent,
} from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  checkCmBatch1Duplicates,
  createCmBatch1Complaint,
  fetchBranches,
  recordCmBatch1DuplicateDecision,
  type Branch,
  type CmBatch1ComplaintBrief,
  type CmBatch1DuplicateCheckResponse,
} from "@/lib/api";
import {
  resolveApiErrorMessage,
  translateValidationErrors,
} from "@/shared/i18n/resolveApiErrorMessage";
import {
  Alert,
  Button,
  Card,
  CardBody,
  Empty,
  Input,
  Modal,
  PageContainer,
  PageHeader,
  SectionHeader,
  Textarea,
} from "@/shared/ui";
import { CustomerSearchPanel } from "./CustomerSearchPanel";
import { ActiveComplaintsBanner } from "./ActiveComplaintsBanner";
import { DuplicateWarningPanel } from "./DuplicateWarningPanel";
import { KnowledgeMentionTextarea } from "./KnowledgeMentionTextarea";
import { StagingAttachmentsPanel } from "./StagingAttachmentsPanel";
import {
  createEmptyComplaintForm,
  newCmBatch1IdempotencyKey,
  newCmBatch1StagingToken,
  toCmBatch1CreateRequest,
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

export type IntakeSubmitIntent = "resolve_branch";

/**
 * Create Complaint — Mode A Batch-1 Aggregate intake (API-500).
 * Outcomes: Lanjut → priority → Daftarkan | Ajukan eskalasi; Selesai (BRANCH_CLOSED).
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
  const [submitting, setSubmitting] = useState(false);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [branchesError, setBranchesError] = useState<string | null>(null);

  const [duplicateOpen, setDuplicateOpen] = useState(false);
  const [duplicateResult, setDuplicateResult] =
    useState<CmBatch1DuplicateCheckResponse | null>(null);
  const [duplicateBusy, setDuplicateBusy] = useState(false);
  const [overrideJustification, setOverrideJustification] = useState<
    string | null
  >(null);
  const [stagingToken, setStagingToken] = useState(() =>
    newCmBatch1StagingToken(),
  );
  const [hasStagedAttachments, setHasStagedAttachments] = useState(false);
  const [stagingBusy, setStagingBusy] = useState(false);
  const intakeIntentRef = useRef<IntakeSubmitIntent>("resolve_branch");
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [confirmIntent, setConfirmIntent] = useState<"resolve_branch" | null>(
    null,
  );
  /** False until session draft restore (if any) has been applied. */
  const [formReady, setFormReady] = useState(false);
  const [activeComplaints, setActiveComplaints] = useState<
    CmBatch1ComplaintBrief[]
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
    }
    consumeIntakeFormResume(); // clear legacy flag if still present
    setFormReady(true);
  }, []);

  useEffect(() => {
    if (!canCreate) {
      return;
    }
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
  }, [officerBranchId, canCreate, t, tCommon, tErrors]);

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
      setDuplicateResult(null);
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
    setDuplicateResult(null);
  }, []);

  if (!canCreate) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <PageHeader
          title={t("create")}
          breadcrumbs={[
            { label: tCommon("home"), href: "/dashboard" },
            { label: t("title"), href: "/complaints" },
            { label: tCommon("create") },
          ]}
        />
        <Empty
          title={tCommon("accessRestricted")}
          description={t("createAccessRestrictedDescription")}
          primaryAction={{
            label: tCommon("goHome"),
            onClick: () => router.push("/dashboard"),
          }}
        />
      </PageContainer>
    );
  }

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
    // Catatan wajib untuk Lanjut/Daftarkan dan Selesai di cabang.
    if (!values.resolution.trim() && !nextErrors.resolution) {
      nextErrors.resolution = tValidation("intakeNoteRequired");
    }
    return nextErrors;
  }

  function requestConfirmResolveBranch(): void {
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
    setConfirmIntent("resolve_branch");
    setConfirmOpen(true);
  }

  /** Continue to priority step — Daftarkan / Ajukan eskalasi chosen there. */
  function continueToPriority(): void {
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
    });
    router.push("/complaints/new/escalate");
  }

  function closeConfirm(): void {
    if (submitting) return;
    setConfirmOpen(false);
    setConfirmIntent(null);
  }

  async function createAggregate(
    justification: string | null,
  ): Promise<void> {
    const intent = intakeIntentRef.current;
    const closeAtBranch = intent === "resolve_branch";
    const response = await createCmBatch1Complaint(
      toCmBatch1CreateRequest(values, {
        duplicateOverrideJustification: justification,
        // Always send token: BE bind is a no-op if nothing staged; omitting
        // it after upload (race / stale hasStaged flag) leaves orphans.
        stagingToken: stagingToken.trim() || null,
        closeAtBranch,
        recordingUnitCode: lockedBranch?.code ?? null,
      }),
      { idempotencyKey: newCmBatch1IdempotencyKey() },
    );
    clearEscalateIntakeDraft();
    const complaintId = response.data.complaintId;
    const suffix = closeAtBranch ? "?intake=closed" : "";
    router.push(`/complaints/cm/${encodeURIComponent(complaintId)}${suffix}`);
  }

  async function executeIntake(intent: IntakeSubmitIntent): Promise<void> {
    intakeIntentRef.current = intent;
    setSubmitError(null);
    setInfoMessage(null);

    setSubmitting(true);
    try {
      if (overrideJustification) {
        await createAggregate(overrideJustification);
        return;
      }

      const dup = await checkCmBatch1Duplicates({
        customerId: values.customerId.trim(),
        category: values.category.trim() || "GENERAL",
        subject: values.subject.trim(),
        channel: values.channel.trim(),
      });
      setDuplicateResult(dup.data);

      if (dup.data.warning) {
        setDuplicateOpen(true);
        return;
      }

      await createAggregate(null);
    } catch (err) {
      setSubmitError(
        resolveApiErrorMessage(err, tErrors, tCommon, "unexpectedError") ||
          t("unableToCreate"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  async function onConfirmAction(): Promise<void> {
    if (!confirmIntent) return;
    setConfirmOpen(false);
    setConfirmIntent(null);
    await executeIntake("resolve_branch");
  }

  async function onDuplicateDecide(payload: {
    decision: "link_existing" | "override" | "recommend_only" | "blocked";
    survivingComplaintId?: string;
    justification?: string;
  }): Promise<void> {
    setDuplicateBusy(true);
    setSubmitError(null);
    try {
      if (payload.decision === "recommend_only") {
        await recordCmBatch1DuplicateDecision({
          decision: "recommend_only",
          customerId: values.customerId.trim(),
          survivingComplaintId: payload.survivingComplaintId,
        });
        setDuplicateOpen(false);
        setInfoMessage(t("recommendOnlyRecorded"));
        return;
      }

      if (payload.decision === "link_existing") {
        const surviving = payload.survivingComplaintId?.trim();
        if (!surviving) {
          setSubmitError(t("survivingIdRequired"));
          return;
        }
        await recordCmBatch1DuplicateDecision({
          decision: "link_existing",
          customerId: values.customerId.trim(),
          survivingComplaintId: surviving,
          // FE always mints STG-*; only send when files were actually staged.
          stagingToken: hasStagedAttachments
            ? stagingToken.trim() || null
            : null,
        });
        clearEscalateIntakeDraft();
        setDuplicateOpen(false);
        router.replace(
          `/complaints/cm/${encodeURIComponent(surviving)}`,
        );
        return;
      }

      if (payload.decision === "override") {
        const justification = payload.justification?.trim() ?? "";
        setOverrideJustification(justification);
        setDuplicateOpen(false);
        setSubmitting(true);
        try {
          await createAggregate(justification);
        } finally {
          setSubmitting(false);
        }
        return;
      }

      if (payload.decision === "blocked") {
        await recordCmBatch1DuplicateDecision({
          decision: "blocked",
          customerId: values.customerId.trim(),
        });
        setDuplicateOpen(false);
        setSubmitError(t("createBlockedByDuplicate"));
      }
    } catch (err) {
      setSubmitError(
        resolveApiErrorMessage(err, tErrors, tCommon, "unexpectedError") ||
          t("unableToRecordDuplicateDecision"),
      );
    } finally {
      setDuplicateBusy(false);
    }
  }

  const confirmCopy = {
    title: t("confirmCloseTitle"),
    body: t("confirmCloseBody"),
    action: t("confirmCloseAction"),
  };

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

        <CustomerSearchPanel
          confirmedCustomerId={values.customerId}
          confirmedDisplayName={values.customerName}
          onConfirmed={onCustomerConfirmed}
          onCleared={onCustomerCleared}
          onActiveComplaintsChange={setActiveComplaints}
          disabled={submitting}
        />

        {values.customerId.trim() ? (
          <ActiveComplaintsBanner
            complaints={activeComplaints}
            disabled={submitting || duplicateBusy}
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
                <Textarea
                  name="description"
                  id="description"
                  label={t("descriptionComplaint")}
                  required
                  rows={5}
                  maxLength={5000}
                  value={values.description}
                  onChange={onTextChange("description")}
                  error={errors.description}
                  aria-required="true"
                  hint={t("charCounter", {
                    count: values.description.trim().length,
                    max: 5000,
                  })}
                />
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
                  disabled={submitting}
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
          disabled={submitting || duplicateBusy}
          onStagingTokenResolved={setStagingToken}
          onHasStagedChange={setHasStagedAttachments}
          onBusyChange={setStagingBusy}
        />

        <div className="flex flex-col-reverse gap-[var(--ecmp-form-gap)] border-t border-ecmp-border pt-[var(--ecmp-panel-gap)] sm:flex-row sm:flex-wrap sm:justify-end">
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={submitting || duplicateBusy || stagingBusy}
            aria-label={t("backAriaLabel")}
          >
            {tCommon("back")}
          </Button>
          <Button
            type="button"
            variant="outline"
            disabled={submitting || duplicateBusy || stagingBusy}
            onClick={continueToPriority}
            aria-label={t("submitRegisterContinueAriaLabel")}
          >
            {t("submitRegisterContinue")}
          </Button>
          <Button
            type="button"
            loading={submitting}
            disabled={submitting || duplicateBusy || stagingBusy}
            onClick={requestConfirmResolveBranch}
            aria-label={t("submitResolveBranchAriaLabel")}
          >
            {submitting ? t("creating") : t("submitResolveBranch")}
          </Button>
        </div>
      </form>

      <Modal
        open={confirmOpen}
        onClose={closeConfirm}
        title={confirmCopy.title}
        size="sm"
        footer={
          <>
            <Button
              type="button"
              variant="outline"
              disabled={submitting}
              onClick={closeConfirm}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              variant="primary"
              disabled={submitting}
              onClick={() => void onConfirmAction()}
            >
              {confirmCopy.action}
            </Button>
          </>
        }
      >
        <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
          {confirmCopy.body}
        </p>
      </Modal>

      <DuplicateWarningPanel
        open={duplicateOpen}
        result={duplicateResult}
        busy={duplicateBusy || submitting}
        onClose={() => setDuplicateOpen(false)}
        onDecide={onDuplicateDecide}
      />
    </PageContainer>
  );
}
