"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  checkCmBatch1Duplicates,
  createCmBatch1Complaint,
  fetchCmBatch1Customer360,
  recordCmBatch1DuplicateDecision,
  type CmBatch1ComplaintBrief,
  type CmBatch1DuplicateCheckResponse,
} from "@/lib/api";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import {
  Alert,
  Button,
  Card,
  CardBody,
  Empty,
  Modal,
  PageContainer,
  PageHeader,
  SectionHeader,
  Select,
} from "@/shared/ui";
import { DuplicateWarningPanel } from "./DuplicateWarningPanel";
import { ActiveComplaintsBanner } from "./ActiveComplaintsBanner";
import {
  newCmBatch1IdempotencyKey,
  toCmBatch1CreateRequest,
  type CreateComplaintFormValues,
} from "./createComplaintForm";
import {
  clearEscalateIntakeDraft,
  peekEscalateIntakeDraft,
  stashEscalateIntakeDraft,
  type EscalateIntakeDraft,
  type IntakePriorityDraftIntent,
} from "./escalateIntakeDraft";
import { createIntakeCasesForRegisteredComplaint } from "./intakeCaseDrafts";

/**
 * Priority + action step after "Lanjut":
 * set priority, then Daftarkan or Ajukan eskalasi (with confirm).
 */
export function EscalateIntakeView() {
  const router = useRouter();
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  const tPriority = useTranslations("priority");
  const tValidation = useTranslations("validation");
  const tErrors = useTranslations("errors");
  const { hasPermission } = useAuth();
  const canCreate = hasPermission("complaints:create");

  const [draft, setDraft] = useState<EscalateIntakeDraft | null>(null);
  const [ready, setReady] = useState(false);
  const [priority, setPriority] = useState("");
  const [priorityError, setPriorityError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  /** True when submitError comes from link_existing (not create). */
  const [linkError, setLinkError] = useState(false);
  const [escalationReasonMissing, setEscalationReasonMissing] = useState(false);
  const [infoMessage, setInfoMessage] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [confirmIntent, setConfirmIntent] =
    useState<IntakePriorityDraftIntent | null>(null);
  const [activeIntent, setActiveIntent] =
    useState<IntakePriorityDraftIntent | null>(null);
  const submitIntentRef = useRef<IntakePriorityDraftIntent>("register");
  const [duplicateOpen, setDuplicateOpen] = useState(false);
  const [duplicateBusy, setDuplicateBusy] = useState(false);
  const [duplicateResult, setDuplicateResult] =
    useState<CmBatch1DuplicateCheckResponse | null>(null);
  const [activeComplaints, setActiveComplaints] = useState<
    CmBatch1ComplaintBrief[]
  >([]);

  useEffect(() => {
    const customerId = draft?.values.customerId?.trim();
    if (!customerId) {
      setActiveComplaints([]);
      return;
    }
    let cancelled = false;
    void fetchCmBatch1Customer360(customerId)
      .then((res) => {
        if (!cancelled) {
          setActiveComplaints(res.data.activeComplaints ?? []);
        }
      })
      .catch(() => {
        if (!cancelled) setActiveComplaints([]);
      });
    return () => {
      cancelled = true;
    };
  }, [draft?.values.customerId]);

  useEffect(() => {
    const loaded = peekEscalateIntakeDraft();
    setDraft(loaded);
    setReady(true);
  }, []);

  const pageTitle = t("intakePriorityTitle");
  const pageDescription = t("intakePriorityDescription");

  const priorityOptions = useMemo(
    () => [
      { value: "LOW", label: tPriority("LOW") },
      { value: "MEDIUM", label: tPriority("MEDIUM") },
      { value: "HIGH", label: tPriority("HIGH") },
      { value: "CRITICAL", label: tPriority("CRITICAL") },
    ],
    [tPriority],
  );

  function withPriority(
    values: CreateComplaintFormValues,
  ): CreateComplaintFormValues {
    const p = priority.trim().toUpperCase();
    const allowed = ["LOW", "MEDIUM", "HIGH", "CRITICAL"] as const;
    const nextPriority = (allowed as readonly string[]).includes(p)
      ? (p as (typeof allowed)[number])
      : "";
    return { ...values, priority: nextPriority };
  }

  function ensurePrioritySelected(): boolean {
    if (!priority.trim()) {
      setPriorityError(tValidation("priorityRequired"));
      document.getElementById("priority")?.focus();
      return false;
    }
    setPriorityError(null);
    return true;
  }

  async function createAggregate(
    values: CreateComplaintFormValues,
    justification: string | null,
    stagingToken: string,
    intent: IntakePriorityDraftIntent,
  ): Promise<void> {
    const escalate = intent === "escalate";
    const response = await createCmBatch1Complaint(
      toCmBatch1CreateRequest(withPriority(values), {
        duplicateOverrideJustification: justification,
        stagingToken: stagingToken.trim() || null,
        escalate,
        recordingUnitCode: draft?.recordingUnitCode ?? null,
      }),
      { idempotencyKey: newCmBatch1IdempotencyKey() },
    );
    if (!escalate) {
      await createIntakeCasesForRegisteredComplaint({
        complaintId: response.data.complaintId,
        values: withPriority(values),
        extraDrafts: draft?.extraCaseDrafts ?? [],
        destinationUnitId:
          draft?.recordingUnitCode?.trim() || values.branchId.trim() || "",
      });
    }
    clearEscalateIntakeDraft();
    const suffix = escalate ? "?intake=escalate" : "";
    router.push(
      `/complaints/cm/${encodeURIComponent(response.data.complaintId)}${suffix}`,
    );
  }

  async function submitWithIntent(
    intent: IntakePriorityDraftIntent,
  ): Promise<void> {
    if (!draft) return;
    submitIntentRef.current = intent;
    setActiveIntent(intent);
    setSubmitError(null);
    setLinkError(false);
    setEscalationReasonMissing(false);
    setInfoMessage(null);
    if (!ensurePrioritySelected()) return;

    setSubmitting(true);
    try {
      if (draft.overrideJustification) {
        await createAggregate(
          draft.values,
          draft.overrideJustification,
          draft.stagingToken,
          intent,
        );
        return;
      }

      const dup = await checkCmBatch1Duplicates({
        customerId: draft.values.customerId.trim(),
        category: draft.values.category.trim() || "GENERAL",
        subject: draft.values.subject.trim(),
        channel: draft.values.channel.trim(),
      });
      setDuplicateResult(dup.data);
      if (dup.data.warning) {
        setDuplicateOpen(true);
        return;
      }
      await createAggregate(draft.values, null, draft.stagingToken, intent);
    } catch (err) {
      setLinkError(false);
      setSubmitError(
        resolveApiErrorMessage(err, tErrors, tCommon, "unexpectedError") ||
          t("unableToCreate"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  function requestConfirm(intent: IntakePriorityDraftIntent): void {
    if (!draft) return;
    setSubmitError(null);
    setLinkError(false);
    setEscalationReasonMissing(false);
    setInfoMessage(null);
    if (!ensurePrioritySelected()) return;

    if (!draft.values.resolution.trim()) {
      setEscalationReasonMissing(true);
      return;
    }

    setConfirmIntent(intent);
    setConfirmOpen(true);
  }

  function closeConfirm(): void {
    if (submitting) return;
    setConfirmOpen(false);
    setConfirmIntent(null);
  }

  async function onConfirmAction(): Promise<void> {
    if (!confirmIntent) return;
    const intent = confirmIntent;
    setConfirmOpen(false);
    setConfirmIntent(null);
    await submitWithIntent(intent);
  }

  /** Only send stagingToken when intake actually staged files (FE always mints STG-*). */
  function stagingTokenForLink(): string | null {
    if (!draft?.hasStagedAttachments) return null;
    return draft.stagingToken.trim() || null;
  }

  async function onDuplicateDecide(payload: {
    decision: "link_existing" | "override" | "recommend_only" | "blocked";
    survivingComplaintId?: string;
    justification?: string;
  }): Promise<void> {
    if (!draft) return;
    const intent = submitIntentRef.current;
    setDuplicateBusy(true);
    setSubmitError(null);
    setLinkError(false);
    try {
      if (payload.decision === "recommend_only") {
        await recordCmBatch1DuplicateDecision({
          decision: "recommend_only",
          customerId: draft.values.customerId.trim(),
          survivingComplaintId: payload.survivingComplaintId,
        });
        setDuplicateOpen(false);
        setInfoMessage(t("recommendOnlyRecorded"));
        return;
      }

      if (payload.decision === "link_existing") {
        const surviving = payload.survivingComplaintId?.trim();
        if (!surviving) {
          setLinkError(true);
          setSubmitError(t("survivingIdRequired"));
          return;
        }
        setLinkError(true);
        await recordCmBatch1DuplicateDecision({
          decision: "link_existing",
          customerId: draft.values.customerId.trim(),
          survivingComplaintId: surviving,
          stagingToken: stagingTokenForLink(),
        });
        clearEscalateIntakeDraft();
        setDuplicateOpen(false);
        // Leave priority step — continue work on the surviving Aggregate.
        router.replace(
          `/complaints/cm/${encodeURIComponent(surviving)}`,
        );
        return;
      }

      if (payload.decision === "override") {
        const justification = payload.justification?.trim() ?? "";
        const next: EscalateIntakeDraft = {
          ...draft,
          overrideJustification: justification,
        };
        stashEscalateIntakeDraft(next);
        setDraft(next);
        setDuplicateOpen(false);
        setSubmitting(true);
        try {
          await createAggregate(
            next.values,
            justification,
            next.stagingToken,
            intent,
          );
        } finally {
          setSubmitting(false);
        }
        return;
      }

      if (payload.decision === "blocked") {
        await recordCmBatch1DuplicateDecision({
          decision: "blocked",
          customerId: draft.values.customerId.trim(),
        });
        setDuplicateOpen(false);
        setSubmitError(t("createBlockedByDuplicate"));
      }
    } catch (err) {
      setLinkError(payload.decision === "link_existing");
      setSubmitError(
        resolveApiErrorMessage(err, tErrors, tCommon, "unexpectedError") ||
          t("unableToRecordDuplicateDecision"),
      );
    } finally {
      setDuplicateBusy(false);
    }
  }

  async function onLinkExistingActive(payload: {
    survivingComplaintId: string;
    label: string;
  }): Promise<void> {
    if (!draft) return;
    const surviving = payload.survivingComplaintId.trim();
    if (!surviving) {
      setLinkError(true);
      setSubmitError(t("survivingIdRequired"));
      return;
    }
    setDuplicateBusy(true);
    setSubmitError(null);
    setLinkError(true);
    try {
      await recordCmBatch1DuplicateDecision({
        decision: "link_existing",
        customerId: draft.values.customerId.trim(),
        survivingComplaintId: surviving,
        stagingToken: stagingTokenForLink(),
      });
      clearEscalateIntakeDraft();
      router.replace(`/complaints/cm/${encodeURIComponent(surviving)}`);
    } catch (err) {
      setSubmitError(
        resolveApiErrorMessage(err, tErrors, tCommon, "unexpectedError") ||
          t("unableToRecordDuplicateDecision"),
      );
    } finally {
      setDuplicateBusy(false);
    }
  }

  if (!canCreate) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <PageHeader
          title={pageTitle}
          breadcrumbs={[
            { label: tCommon("home"), href: "/dashboard" },
            { label: t("title"), href: "/complaints" },
            { label: tCommon("create"), href: "/complaints/new" },
            { label: pageTitle },
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

  if (!ready) {
    return null;
  }

  if (!draft) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <PageHeader
          title={pageTitle}
          breadcrumbs={[
            { label: tCommon("home"), href: "/dashboard" },
            { label: t("title"), href: "/complaints" },
            { label: tCommon("create"), href: "/complaints/new" },
            { label: pageTitle },
          ]}
        />
        <Empty
          title={t("intakeDraftMissingTitle")}
          description={t("intakeDraftMissingDescription")}
          primaryAction={{
            label: t("create"),
            onClick: () => router.push("/complaints/new"),
          }}
        />
      </PageContainer>
    );
  }

  const values = draft.values;
  const showNote = Boolean(values.resolution.trim());
  const priorityKey = priority.trim().toUpperCase();
  const priorityLabel =
    priorityKey === "LOW" ||
    priorityKey === "MEDIUM" ||
    priorityKey === "HIGH" ||
    priorityKey === "CRITICAL"
      ? tPriority(priorityKey)
      : priorityKey;

  const confirmCopy =
    confirmIntent === "escalate"
      ? {
          title: t("confirmEscalateTitle"),
          body: t("confirmEscalateBody", {
            customer: values.customerName.trim() || values.customerId.trim(),
            subject: values.subject.trim(),
            priority: priorityLabel,
          }),
          action: t("confirmEscalateAction"),
        }
      : {
          title: t("confirmRegisterTitle"),
          body: t("confirmRegisterBody", {
            customer: values.customerName.trim() || values.customerId.trim(),
            subject: values.subject.trim(),
            priority: priorityLabel,
          }),
          action: t("confirmRegisterAction"),
        };

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={pageTitle}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title"), href: "/complaints" },
          { label: tCommon("create"), href: "/complaints/new" },
          { label: pageTitle },
        ]}
        description={pageDescription}
      />

      {escalationReasonMissing ? (
        <Alert
          tone="danger"
          title={t("intakeNoteMissingTitle")}
          description={t("intakeNoteMissingDescription")}
        />
      ) : null}

      {submitError ? (
        <Alert
          tone="danger"
          title={
            linkError
              ? t("unableToRecordDuplicateDecision")
              : t("couldNotCreate")
          }
          description={submitError}
        />
      ) : null}

      {infoMessage ? (
        <Alert tone="info" title={t("notice")} description={infoMessage} />
      ) : null}

      <ActiveComplaintsBanner
        complaints={activeComplaints}
        disabled={submitting || duplicateBusy}
        linking={duplicateBusy}
        onLinkExisting={onLinkExistingActive}
      />

      <section className="space-y-[var(--ecmp-panel-gap)]">
        <SectionHeader
          title={t("registrationDetails")}
          description={t("intakePrioritySummaryHint")}
        />
        <Card>
          <CardBody>
            <dl className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] md:grid-cols-2">
              <div className="space-y-1 md:col-span-2">
                <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                  {t("subject")}
                </dt>
                <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                  {values.subject.trim()}
                </dd>
              </div>
              <div className="space-y-1 md:col-span-2">
                <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                  {t("intakeNarrativeLabel")}
                </dt>
                <dd className="whitespace-pre-wrap text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                  {values.description.trim() || t("intakeNarrativeEmpty")}
                </dd>
              </div>
              {showNote ? (
                <div className="space-y-1 md:col-span-2">
                  <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                    {t("intakeNoteLabel")}
                  </dt>
                  <dd className="whitespace-pre-wrap text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                    {values.resolution.trim()}
                  </dd>
                </div>
              ) : null}
              <div className="space-y-1 md:col-span-2">
                <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                  {t("customer")}
                </dt>
                <dd className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                  {values.customerName.trim() || values.customerId.trim()}
                </dd>
              </div>
            </dl>
          </CardBody>
        </Card>
      </section>

      <section className="space-y-[var(--ecmp-panel-gap)]">
        <SectionHeader
          title={t("priority")}
          description={t("intakePriorityHint")}
        />
        <Card>
          <CardBody>
            <div className="max-w-xs">
              <Select
                name="priority"
                id="priority"
                label={t("priority")}
                placeholder={t("selectPriorityPlaceholder")}
                options={priorityOptions}
                value={priority}
                onChange={(e) => {
                  setPriority(e.target.value);
                  setPriorityError(null);
                }}
                error={priorityError ?? undefined}
                required
                aria-required="true"
              />
            </div>
          </CardBody>
        </Card>
      </section>

      <div className="flex flex-col-reverse gap-[var(--ecmp-form-gap)] border-t border-ecmp-border pt-[var(--ecmp-panel-gap)] sm:flex-row sm:flex-wrap sm:justify-end">
        <Button
          type="button"
          variant="outline"
          disabled={submitting || duplicateBusy}
          onClick={() => {
            // Draft stays in sessionStorage; create form restores on mount.
            router.push("/complaints/new");
          }}
        >
          {tCommon("back")}
        </Button>
        <Button
          type="button"
          variant="outline"
          loading={submitting && activeIntent === "escalate"}
          disabled={submitting || duplicateBusy}
          onClick={() => requestConfirm("escalate")}
          aria-label={t("submitEscalateAriaLabel")}
        >
          {submitting && activeIntent === "escalate"
            ? t("creating")
            : t("submitEscalate")}
        </Button>
        <Button
          type="button"
          loading={submitting && activeIntent === "register"}
          disabled={submitting || duplicateBusy}
          onClick={() => requestConfirm("register")}
          aria-label={t("submitRegisterAriaLabel")}
        >
          {submitting && activeIntent === "register"
            ? t("creating")
            : t("submitRegister")}
        </Button>
      </div>

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
