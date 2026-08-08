"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  checkCmBatch1Duplicates,
  createCmBatch1Complaint,
  recordCmBatch1DuplicateDecision,
  type CmBatch1DuplicateCheckResponse,
} from "@/lib/api";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import {
  Alert,
  Button,
  Card,
  CardBody,
  Empty,
  PageContainer,
  PageHeader,
  SectionHeader,
  Select,
} from "@/shared/ui";
import { DuplicateWarningPanel } from "./DuplicateWarningPanel";
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
} from "./escalateIntakeDraft";

/**
 * Step after "Ajukan eskalasi": set priority for HQ triage, then create Aggregate.
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
  const [infoMessage, setInfoMessage] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [duplicateOpen, setDuplicateOpen] = useState(false);
  const [duplicateBusy, setDuplicateBusy] = useState(false);
  const [duplicateResult, setDuplicateResult] =
    useState<CmBatch1DuplicateCheckResponse | null>(null);

  useEffect(() => {
    const loaded = peekEscalateIntakeDraft();
    setDraft(loaded);
    setReady(true);
  }, []);

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

  async function createAggregate(
    values: CreateComplaintFormValues,
    justification: string | null,
    stagingToken: string,
    hasStagedAttachments: boolean,
  ): Promise<void> {
    const response = await createCmBatch1Complaint(
      toCmBatch1CreateRequest(withPriority(values), {
        duplicateOverrideJustification: justification,
        stagingToken: hasStagedAttachments ? stagingToken : null,
        escalate: true,
      }),
      { idempotencyKey: newCmBatch1IdempotencyKey() },
    );
    clearEscalateIntakeDraft();
    router.push(
      `/complaints/cm/${encodeURIComponent(response.data.complaintId)}?intake=escalate`,
    );
  }

  async function submitEscalate(): Promise<void> {
    if (!draft) return;
    setSubmitError(null);
    setInfoMessage(null);
    if (!priority.trim()) {
      setPriorityError(tValidation("priorityRequired"));
      document.getElementById("priority")?.focus();
      return;
    }
    setPriorityError(null);
    setSubmitting(true);
    try {
      if (draft.overrideJustification) {
        await createAggregate(
          draft.values,
          draft.overrideJustification,
          draft.stagingToken,
          draft.hasStagedAttachments,
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
      await createAggregate(
        draft.values,
        null,
        draft.stagingToken,
        draft.hasStagedAttachments,
      );
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
    if (!draft) return;
    setDuplicateBusy(true);
    setSubmitError(null);
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
          setSubmitError(t("survivingIdRequired"));
          return;
        }
        await recordCmBatch1DuplicateDecision({
          decision: "link_existing",
          customerId: draft.values.customerId.trim(),
          survivingComplaintId: surviving,
          stagingToken: draft.hasStagedAttachments
            ? draft.stagingToken
            : null,
        });
        clearEscalateIntakeDraft();
        setDuplicateOpen(false);
        router.push(`/complaints/cm/${surviving}`);
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
            next.hasStagedAttachments,
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
          title={t("escalatePriorityTitle")}
          breadcrumbs={[
            { label: tCommon("home"), href: "/dashboard" },
            { label: t("title"), href: "/complaints" },
            { label: tCommon("create"), href: "/complaints/new" },
            { label: t("escalatePriorityTitle") },
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
          title={t("escalatePriorityTitle")}
          breadcrumbs={[
            { label: tCommon("home"), href: "/dashboard" },
            { label: t("title"), href: "/complaints" },
            { label: tCommon("create"), href: "/complaints/new" },
            { label: t("escalatePriorityTitle") },
          ]}
        />
        <Empty
          title={t("escalateDraftMissingTitle")}
          description={t("escalateDraftMissingDescription")}
          primaryAction={{
            label: t("create"),
            onClick: () => router.push("/complaints/new"),
          }}
        />
      </PageContainer>
    );
  }

  const values = draft.values;

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        title={t("escalatePriorityTitle")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title"), href: "/complaints" },
          { label: tCommon("create"), href: "/complaints/new" },
          { label: t("escalatePriorityTitle") },
        ]}
        description={t("escalatePriorityDescription")}
      />

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

      <section className="space-y-[var(--ecmp-panel-gap)]">
        <SectionHeader
          title={t("registrationDetails")}
          description={t("escalatePrioritySummaryHint")}
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
              <div className="space-y-1 md:col-span-2">
                <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                  {t("escalationReasonLabel")}
                </dt>
                <dd className="whitespace-pre-wrap text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                  {values.resolution.trim() || t("escalationReasonEmpty")}
                </dd>
              </div>
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
          description={t("priorityEscalateHint")}
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

      <div className="flex flex-col-reverse gap-[var(--ecmp-form-gap)] border-t border-ecmp-border pt-[var(--ecmp-panel-gap)] sm:flex-row sm:justify-end">
        <Button
          type="button"
          variant="outline"
          disabled={submitting || duplicateBusy}
          onClick={() => router.push("/complaints/new")}
        >
          {tCommon("back")}
        </Button>
        <Button
          type="button"
          loading={submitting}
          disabled={duplicateBusy}
          onClick={() => void submitEscalate()}
        >
          {submitting ? t("creating") : t("submitEscalate")}
        </Button>
      </div>

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
