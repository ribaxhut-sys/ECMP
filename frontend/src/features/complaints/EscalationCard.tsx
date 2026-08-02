"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { useLocale, useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  approveEscalation,
  fetchComplaintEscalations,
  fetchEscalation,
  rejectEscalation,
  requestEscalation,
} from "@/lib/api";
import type {
  ComplaintStatus,
  Escalation,
  EscalationReasonCode,
} from "@/lib/api/types";
import { formatDateTime } from "@/i18n/formatting";
import {
  Alert,
  Button,
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  Modal,
  Select,
  Textarea,
  Toast,
} from "@/shared/ui";

const REASON_VALUES: readonly EscalationReasonCode[] = [
  "SPECIALIST_REQUIRED",
  "COMPLEX_CASE",
  "POLICY_EXCEPTION",
  "CUSTOMER_REQUEST",
  "OTHER",
];

const REQUEST_FLOW_STATUSES = new Set([
  "REQUESTED",
  "APPROVED",
  "REJECTED",
  "CLOSED",
]);

function DetailField({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0 space-y-1">
      <dt className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
        {label}
      </dt>
      <dd className="whitespace-pre-wrap break-words text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
        {value}
      </dd>
    </div>
  );
}

/** Blocks a new Branch→HO request while REQUESTED / OPEN / APPROVED. */
function blocksNewRequest(row: Escalation): boolean {
  return (
    row.status === "REQUESTED" ||
    row.status === "OPEN" ||
    row.status === "APPROVED"
  );
}

function isRequestFlowEscalation(row: Escalation): boolean {
  return Boolean(row.reasonCode) || REQUEST_FLOW_STATUSES.has(row.status);
}

function pickDisplayEscalation(rows: Escalation[]): Escalation | null {
  const requestFlow = rows.filter(isRequestFlowEscalation);
  if (requestFlow.length > 0) {
    return (
      requestFlow.find((row) => row.status === "CLOSED") ??
      requestFlow.find((row) => row.status === "REQUESTED") ??
      requestFlow.find((row) => row.status === "APPROVED") ??
      requestFlow[0] ??
      null
    );
  }
  return rows.find(blocksNewRequest) ?? null;
}

type ReviewAction = "approve" | "reject";

export function EscalationCard({
  complaintId,
  status,
  hasResolution,
  onRequested,
  onReviewed,
}: {
  complaintId: string;
  status: ComplaintStatus;
  hasResolution: boolean;
  onRequested?: () => void;
  onReviewed?: () => void;
}) {
  const { hasPermission } = useAuth();
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  const tReason = useTranslations("escalationReason");
  const locale = useLocale();
  const canUpdate = hasPermission("complaints:update");
  const canReview = hasPermission("escalations:review");

  const reasonOptions = REASON_VALUES.map((value) => ({
    value,
    label: tReason(value),
  }));

  function reasonLabel(value: string | null | undefined): string {
    if (!value) return tCommon("emDash");
    return (REASON_VALUES as readonly string[]).includes(value)
      ? tReason(value)
      : value.replaceAll("_", " ");
  }

  const [escalation, setEscalation] = useState<Escalation | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [formOpen, setFormOpen] = useState(false);

  const [reasonCode, setReasonCode] = useState<EscalationReasonCode | "">("");
  const [reasonDescription, setReasonDescription] = useState("");
  const [diagnosis, setDiagnosis] = useState("");
  const [notes, setNotes] = useState("");
  const [fieldErrors, setFieldErrors] = useState<{
    reasonCode?: string;
    reasonDescription?: string;
    diagnosis?: string;
  }>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [toastOpen, setToastOpen] = useState(false);
  const [toastTitle, setToastTitle] = useState("");
  const [toastDescription, setToastDescription] = useState("");

  const [reviewAction, setReviewAction] = useState<ReviewAction | null>(null);
  const [reviewNotes, setReviewNotes] = useState("");
  const [reviewNotesError, setReviewNotesError] = useState<string | undefined>();
  const [reviewError, setReviewError] = useState<string | null>(null);
  const [reviewing, setReviewing] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const res = await fetchComplaintEscalations(complaintId);
      const selected = pickDisplayEscalation(res.data);
      if (selected) {
        try {
          const detail = await fetchEscalation(selected.id);
          setEscalation(detail.data);
        } catch {
          setEscalation(selected);
        }
      } else {
        setEscalation(null);
      }
    } catch (err) {
      setEscalation(null);
      setLoadError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : t("unableToLoadEscalation"),
      );
    } finally {
      setLoading(false);
    }
  }, [complaintId, t]);

  useEffect(() => {
    void load();
  }, [load, status]);

  const hasBlockingEscalation =
    escalation != null && blocksNewRequest(escalation);

  const canRequest =
    canUpdate &&
    status === "IN_PROGRESS" &&
    !hasResolution &&
    !hasBlockingEscalation &&
    !loading;

  const canShowReviewActions =
    canReview && escalation?.status === "REQUESTED" && !loading;

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitError(null);

    const nextErrors: typeof fieldErrors = {};
    if (!reasonCode) nextErrors.reasonCode = t("reasonCodeRequired");
    if (!reasonDescription.trim()) {
      nextErrors.reasonDescription = t("reasonDescriptionRequired");
    }
    if (!diagnosis.trim()) nextErrors.diagnosis = t("diagnosisRequired");
    setFieldErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;

    setSubmitting(true);
    try {
      const created = await requestEscalation(complaintId, {
        reasonCode: reasonCode as EscalationReasonCode,
        reasonDescription: reasonDescription.trim(),
        diagnosis: diagnosis.trim(),
        notes: notes.trim() || null,
      });
      const detail = await fetchEscalation(created.data.id);
      setEscalation(detail.data);
      setFormOpen(false);
      setReasonCode("");
      setReasonDescription("");
      setDiagnosis("");
      setNotes("");
      setToastTitle(t("escalationRequested"));
      setToastDescription(t("awaitingHeadOfficeReview"));
      setToastOpen(true);
      onRequested?.();
    } catch (err) {
      setSubmitError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : t("escalationRequestFailed"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  function openReview(action: ReviewAction) {
    setReviewAction(action);
    setReviewNotes("");
    setReviewNotesError(undefined);
    setReviewError(null);
  }

  function closeReview() {
    if (reviewing) return;
    setReviewAction(null);
    setReviewNotes("");
    setReviewNotesError(undefined);
    setReviewError(null);
  }

  async function confirmReview() {
    if (!escalation || !reviewAction) return;
    const notesTrimmed = reviewNotes.trim();
    if (!notesTrimmed) {
      setReviewNotesError(t("reviewNotesRequired"));
      return;
    }
    setReviewNotesError(undefined);
    setReviewError(null);
    setReviewing(true);
    try {
      const body = { reviewNotes: notesTrimmed };
      if (reviewAction === "approve") {
        await approveEscalation(escalation.id, body);
        setToastTitle(t("escalationApproved"));
        setToastDescription(t("headOfficeWillHandle"));
      } else {
        await rejectEscalation(escalation.id, body);
        setToastTitle(t("escalationRejected"));
        setToastDescription(t("issueRemainsWithBranch"));
      }
      const detail = await fetchEscalation(escalation.id);
      setEscalation(detail.data);
      setReviewAction(null);
      setReviewNotes("");
      setToastOpen(true);
      onReviewed?.();
    } catch (err) {
      setReviewError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : t("reviewFailed"),
      );
    } finally {
      setReviewing(false);
    }
  }

  const reviewed =
    escalation?.status === "APPROVED" || escalation?.status === "REJECTED";

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>{t("escalationCard")}</CardTitle>
        </CardHeader>
        <CardBody className="space-y-[var(--ecmp-panel-gap)]">
          {loading ? (
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              {t("loadingEscalation")}
            </p>
          ) : loadError ? (
            <Alert
              tone="danger"
              title={t("couldNotLoadEscalation")}
              description={loadError}
              actionLabel={tCommon("retry")}
              onAction={() => void load()}
            />
          ) : escalation ? (
            <div className="space-y-[var(--ecmp-panel-gap)]">
              <dl className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] sm:grid-cols-2">
                <DetailField label={t("status")} value={escalation.status} />
                <DetailField
                  label={t("requestedBy")}
                  value={escalation.requestedByName?.trim() || tCommon("emDash")}
                />
                <DetailField
                  label={t("reasonCode")}
                  value={reasonLabel(escalation.reasonCode)}
                />
                <DetailField
                  label={t("requestedAt")}
                  value={formatDateTime(escalation.requestedAt, locale)}
                />
                <div className="sm:col-span-2">
                  <DetailField
                    label={t("reasonDescription")}
                    value={
                      escalation.reasonDescription?.trim() || escalation.reason
                    }
                  />
                </div>
                <div className="sm:col-span-2">
                  <DetailField
                    label={t("diagnosis")}
                    value={escalation.diagnosis?.trim() || tCommon("emDash")}
                  />
                </div>
                {escalation.notes?.trim() ? (
                  <div className="sm:col-span-2">
                    <DetailField label={t("notes")} value={escalation.notes} />
                  </div>
                ) : null}
              </dl>

              {reviewed ? (
                <div className="space-y-3 border-t border-ecmp-border pt-[var(--ecmp-panel-gap)]">
                  <p className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                    {t("reviewDecision")}
                  </p>
                  <dl className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] sm:grid-cols-2">
                    <DetailField
                      label={t("reviewedBy")}
                      value={escalation.reviewedByName?.trim() || tCommon("emDash")}
                    />
                    <DetailField
                      label={t("reviewedAt")}
                      value={formatDateTime(escalation.reviewedAt, locale)}
                    />
                    <div className="sm:col-span-2">
                      <DetailField
                        label={t("reviewNotes")}
                        value={escalation.reviewNotes?.trim() || tCommon("emDash")}
                      />
                    </div>
                  </dl>
                </div>
              ) : null}

              {canShowReviewActions ? (
                <div className="space-y-3 border-t border-ecmp-border pt-[var(--ecmp-panel-gap)]">
                  <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                    {t("headOfficeReviewHint")}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    <Button
                      type="button"
                      variant="primary"
                      onClick={() => openReview("approve")}
                    >
                      {t("approve")}
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => openReview("reject")}
                    >
                      {t("reject")}
                    </Button>
                  </div>
                </div>
              ) : escalation.status === "REQUESTED" && !canReview ? (
                <p className="border-t border-ecmp-border pt-[var(--ecmp-panel-gap)] text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                  {t("awaitingHeadOfficeSchedulerReview")}
                </p>
              ) : null}
            </div>
          ) : canRequest && !formOpen ? (
            <div className="space-y-3">
              <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                {t("requestEscalationHint")}
              </p>
              <Button
                type="button"
                variant="outline"
                onClick={() => setFormOpen(true)}
              >
                {t("requestEscalation")}
              </Button>
            </div>
          ) : !canRequest ? (
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              {hasResolution
                ? t("escalationNotAvailableAfterResolution")
                : status !== "IN_PROGRESS"
                  ? t("escalationOnlyWhileInProgress")
                  : t("noEscalationRequested")}
            </p>
          ) : null}

          {canRequest && formOpen ? (
            <form
              className="space-y-[var(--ecmp-panel-gap)] border-t border-ecmp-border pt-[var(--ecmp-panel-gap)]"
              onSubmit={onSubmit}
            >
              <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
                {t("escalationRequestFormHint")}
              </p>
              {submitError ? (
                <Alert
                  tone="danger"
                  title={t("escalationRequestFailed")}
                  description={submitError}
                />
              ) : null}
              <Select
                label={t("reasonCode")}
                name="reasonCode"
                required
                placeholder={t("selectReasonPlaceholder")}
                options={reasonOptions}
                value={reasonCode}
                error={fieldErrors.reasonCode}
                onChange={(event) =>
                  setReasonCode(event.target.value as EscalationReasonCode | "")
                }
              />
              <Textarea
                label={t("reasonDescription")}
                name="reasonDescription"
                required
                rows={2}
                value={reasonDescription}
                error={fieldErrors.reasonDescription}
                onChange={(event) => setReasonDescription(event.target.value)}
              />
              <Textarea
                label={t("diagnosis")}
                name="diagnosis"
                required
                rows={3}
                value={diagnosis}
                error={fieldErrors.diagnosis}
                onChange={(event) => setDiagnosis(event.target.value)}
              />
              <Textarea
                label={t("notes")}
                name="notes"
                rows={2}
                value={notes}
                onChange={(event) => setNotes(event.target.value)}
              />
              <div className="flex flex-wrap justify-end gap-2">
                <Button
                  type="button"
                  variant="outline"
                  disabled={submitting}
                  onClick={() => {
                    setFormOpen(false);
                    setSubmitError(null);
                    setFieldErrors({});
                  }}
                >
                  {tCommon("cancel")}
                </Button>
                <Button type="submit" variant="primary" disabled={submitting}>
                  {submitting ? tCommon("submitting") : t("submitRequest")}
                </Button>
              </div>
            </form>
          ) : null}
        </CardBody>
      </Card>

      <Modal
        open={reviewAction !== null}
        onClose={closeReview}
        title={
          reviewAction === "approve"
            ? t("approveEscalationConfirm")
            : t("rejectEscalationConfirm")
        }
        size="sm"
        footer={
          <>
            <Button
              type="button"
              variant="outline"
              disabled={reviewing}
              onClick={closeReview}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              variant={reviewAction === "reject" ? "outline" : "primary"}
              disabled={reviewing}
              onClick={() => void confirmReview()}
            >
              {reviewing
                ? tCommon("saving")
                : reviewAction === "approve"
                  ? t("confirmApprove")
                  : t("confirmReject")}
            </Button>
          </>
        }
      >
        <div className="space-y-[var(--ecmp-panel-gap)]">
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
            {reviewAction === "approve"
              ? t("confirmApprovalHint")
              : t("confirmRejectionHint")}
          </p>
          {reviewError ? (
            <Alert
              tone="danger"
              title={t("reviewFailed")}
              description={reviewError}
            />
          ) : null}
          <Textarea
            label={t("reviewNotes")}
            name="reviewNotes"
            required
            rows={3}
            value={reviewNotes}
            error={reviewNotesError}
            onChange={(event) => setReviewNotes(event.target.value)}
          />
        </div>
      </Modal>

      <Toast
        open={toastOpen}
        onClose={() => setToastOpen(false)}
        tone="success"
        title={toastTitle}
        description={toastDescription}
      />
    </>
  );
}
