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
  PageContainer,
  PageHeader,
  SectionHeader,
  Textarea,
} from "@/shared/ui";
import { CustomerSearchPanel } from "./CustomerSearchPanel";
import { DuplicateWarningPanel } from "./DuplicateWarningPanel";
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
import { stashEscalateIntakeDraft } from "./escalateIntakeDraft";

export type IntakeSubmitIntent = "resolve_branch" | "escalate";

/**
 * Create Complaint — Mode A Batch-1 Aggregate intake (API-500).
 * Dual outcomes: selesai di cabang (CLOSED) vs ajukan eskalasi (priority step).
 */
export function CreateComplaintView() {
  const router = useRouter();
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  const tValidation = useTranslations("validation");
  const tErrors = useTranslations("errors");
  const { user, hasPermission } = useAuth();
  const canCreate = hasPermission("complaints:create");
  const agentBranchId = user?.branchId ?? null;

  const [values, setValues] = useState<CreateComplaintFormValues>(() =>
    createEmptyComplaintForm({ branchId: agentBranchId, channel: "BRANCH" }),
  );
  const [errors, setErrors] = useState<CreateComplaintFieldErrors>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [infoMessage, setInfoMessage] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [branchesLoading, setBranchesLoading] = useState(true);
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
  const [activeIntent, setActiveIntent] =
    useState<IntakeSubmitIntent>("resolve_branch");
  const intakeIntentRef = useRef<IntakeSubmitIntent>("resolve_branch");

  useEffect(() => {
    if (!canCreate) {
      setBranchesLoading(false);
      return;
    }
    let cancelled = false;
    (async () => {
      setBranchesLoading(true);
      setBranchesError(null);
      try {
        const res = await fetchBranches(100);
        if (cancelled) return;
        setBranches(res.data);
        const locked =
          (agentBranchId
            ? res.data.find((b) => b.id === agentBranchId)
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
      } finally {
        if (!cancelled) setBranchesLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [agentBranchId, canCreate, t, tCommon, tErrors]);

  const lockedBranch = useMemo(() => {
    if (agentBranchId) {
      return branches.find((b) => b.id === agentBranchId) ?? null;
    }
    return branches.find((b) => b.code.toUpperCase() === "PUSAT") ?? null;
  }, [agentBranchId, branches]);

  const lockedBranchLabel = lockedBranch
    ? `${lockedBranch.code} — ${lockedBranch.name}`
    : branchesLoading
      ? t("loadingBranches")
      : t("noActiveBranches");

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
    router.push("/complaints");
  }

  async function createAggregate(
    justification: string | null,
  ): Promise<void> {
    const response = await createCmBatch1Complaint(
      toCmBatch1CreateRequest(values, {
        duplicateOverrideJustification: justification,
        stagingToken: hasStagedAttachments ? stagingToken : null,
        closeAtBranch: true,
      }),
      { idempotencyKey: newCmBatch1IdempotencyKey() },
    );
    const complaintId = response.data.complaintId;
    router.push(
      `/complaints/cm/${encodeURIComponent(complaintId)}?intake=closed`,
    );
  }

  async function submitIntake(intent: IntakeSubmitIntent): Promise<void> {
    intakeIntentRef.current = intent;
    setActiveIntent(intent);
    setSubmitError(null);
    setInfoMessage(null);

    const nextErrors = translateValidationErrors(
      validateCmBatch1CreateForm(values),
      tValidation,
    );
    if (intent === "resolve_branch" && !values.resolution.trim()) {
      nextErrors.resolution = tValidation("resolutionRequired");
    }
    if (intent === "escalate" && !values.resolution.trim()) {
      nextErrors.resolution = tValidation("escalationReasonRequired");
    }
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) {
      const firstKey = Object.keys(nextErrors)[0];
      const el = firstKey ? document.getElementById(firstKey) : null;
      el?.focus();
      return;
    }

    if (intent === "escalate") {
      stashEscalateIntakeDraft({
        values,
        stagingToken,
        hasStagedAttachments,
        overrideJustification,
      });
      router.push("/complaints/new/escalate");
      return;
    }

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
          stagingToken: hasStagedAttachments ? stagingToken : null,
        });
        setDuplicateOpen(false);
        router.push(`/complaints/cm/${surviving}`);
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
          void submitIntake("resolve_branch");
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
          disabled={submitting}
        />

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
              <Textarea
                name="resolution"
                id="resolution"
                label={t("resolutionOrEscalationReason")}
                rows={5}
                maxLength={5000}
                value={values.resolution}
                onChange={onTextChange("resolution")}
                error={errors.resolution}
                hint={t("resolutionOrEscalationReasonHint", {
                  count: values.resolution.trim().length,
                  max: 5000,
                })}
              />
            </fieldset>
          </CardBody>
          </Card>
        </section>

        <section className="space-y-[var(--ecmp-panel-gap)]">
          <SectionHeader
            id="section-location"
            title={t("recordingUnit")}
            description={t("recordingUnitLockedHint")}
          />
          <Card>
          <CardBody>
            <fieldset
              aria-labelledby="section-location"
              className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] md:grid-cols-2"
            >
              <legend className="sr-only">{t("recordingUnit")}</legend>
              <Input
                name="branchId"
                id="branchId"
                label={t("branch")}
                value={lockedBranchLabel}
                readOnly
                disabled
                error={errors.branchId}
                hint={t("recordingUnitLockedHint")}
                aria-readonly="true"
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
        />

        <div className="flex flex-col-reverse gap-[var(--ecmp-form-gap)] border-t border-ecmp-border pt-[var(--ecmp-panel-gap)] sm:flex-row sm:flex-wrap sm:justify-end">
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={submitting || duplicateBusy}
            aria-label={t("backAriaLabel")}
          >
            {tCommon("back")}
          </Button>
          <Button
            type="button"
            variant="outline"
            loading={submitting && activeIntent === "escalate"}
            disabled={submitting || duplicateBusy}
            onClick={() => void submitIntake("escalate")}
            aria-label={t("submitEscalateAriaLabel")}
          >
            {submitting && activeIntent === "escalate"
              ? t("creating")
              : t("submitEscalate")}
          </Button>
          <Button
            type="submit"
            loading={submitting && activeIntent === "resolve_branch"}
            disabled={submitting || duplicateBusy}
            aria-label={t("submitResolveBranchAriaLabel")}
          >
            {submitting && activeIntent === "resolve_branch"
              ? t("creating")
              : t("submitResolveBranch")}
          </Button>
        </div>
      </form>

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
