"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
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

const REASON_OPTIONS: ReadonlyArray<{
  value: EscalationReasonCode;
  label: string;
}> = [
  { value: "SPECIALIST_REQUIRED", label: "Specialist Required" },
  { value: "COMPLEX_CASE", label: "Complex Case" },
  { value: "POLICY_EXCEPTION", label: "Policy Exception" },
  { value: "CUSTOMER_REQUEST", label: "Customer Request" },
  { value: "OTHER", label: "Other" },
];

const REQUEST_FLOW_STATUSES = new Set([
  "REQUESTED",
  "APPROVED",
  "REJECTED",
  "CLOSED",
]);

function formatWhen(value: string | null | undefined): string {
  if (!value) return "—";
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

function reasonLabel(value: string | null | undefined): string {
  if (!value) return "—";
  return (
    REASON_OPTIONS.find((option) => option.value === value)?.label ??
    value.replaceAll("_", " ")
  );
}

function DetailField({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0 space-y-1">
      <dt className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary">
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
  const canUpdate = hasPermission("complaints:update");
  const canReview = hasPermission("escalations:review");

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
  const [toastTitle, setToastTitle] = useState("Escalation requested");
  const [toastDescription, setToastDescription] = useState(
    "Status is REQUESTED. Awaiting Head Office review.",
  );

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
            : "Unable to load escalation.",
      );
    } finally {
      setLoading(false);
    }
  }, [complaintId]);

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
    if (!reasonCode) nextErrors.reasonCode = "Reason code is required.";
    if (!reasonDescription.trim()) {
      nextErrors.reasonDescription = "Reason description is required.";
    }
    if (!diagnosis.trim()) nextErrors.diagnosis = "Diagnosis is required.";
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
      setToastTitle("Escalation requested");
      setToastDescription(
        "Status is REQUESTED. Awaiting Head Office review.",
      );
      setToastOpen(true);
      onRequested?.();
    } catch (err) {
      setSubmitError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Escalation request failed.",
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
      setReviewNotesError("Review notes are required.");
      return;
    }
    setReviewNotesError(undefined);
    setReviewError(null);
    setReviewing(true);
    try {
      const body = { reviewNotes: notesTrimmed };
      if (reviewAction === "approve") {
        await approveEscalation(escalation.id, body);
        setToastTitle("Escalation approved");
        setToastDescription("Head Office will handle this escalation.");
      } else {
        await rejectEscalation(escalation.id, body);
        setToastTitle("Escalation rejected");
        setToastDescription("Issue remains with the Branch.");
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
            : "Review failed.",
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
          <CardTitle>Escalation</CardTitle>
        </CardHeader>
        <CardBody className="space-y-4">
          {loading ? (
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              Loading escalation…
            </p>
          ) : loadError ? (
            <Alert
              tone="danger"
              title="Could not load escalation"
              description={loadError}
              actionLabel="Retry"
              onAction={() => void load()}
            />
          ) : escalation ? (
            <div className="space-y-4">
              <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <DetailField label="Status" value={escalation.status} />
                <DetailField
                  label="Requested By"
                  value={escalation.requestedByName?.trim() || "—"}
                />
                <DetailField
                  label="Reason Code"
                  value={reasonLabel(escalation.reasonCode)}
                />
                <DetailField
                  label="Requested At"
                  value={formatWhen(escalation.requestedAt)}
                />
                <div className="sm:col-span-2">
                  <DetailField
                    label="Reason Description"
                    value={
                      escalation.reasonDescription?.trim() || escalation.reason
                    }
                  />
                </div>
                <div className="sm:col-span-2">
                  <DetailField
                    label="Diagnosis"
                    value={escalation.diagnosis?.trim() || "—"}
                  />
                </div>
                {escalation.notes?.trim() ? (
                  <div className="sm:col-span-2">
                    <DetailField label="Notes" value={escalation.notes} />
                  </div>
                ) : null}
              </dl>

              {reviewed ? (
                <div className="space-y-3 border-t border-ecmp-border pt-4">
                  <p className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary">
                    Review Decision
                  </p>
                  <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <DetailField
                      label="Reviewed By"
                      value={escalation.reviewedByName?.trim() || "—"}
                    />
                    <DetailField
                      label="Reviewed At"
                      value={formatWhen(escalation.reviewedAt)}
                    />
                    <div className="sm:col-span-2">
                      <DetailField
                        label="Review Notes"
                        value={escalation.reviewNotes?.trim() || "—"}
                      />
                    </div>
                  </dl>
                </div>
              ) : null}

              {canShowReviewActions ? (
                <div className="space-y-3 border-t border-ecmp-border pt-4">
                  <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                    Head Office review — approve or reject this escalation
                    request. Complaint remains IN PROGRESS.
                  </p>
                  <div className="flex flex-wrap gap-2">
                    <Button
                      type="button"
                      variant="primary"
                      onClick={() => openReview("approve")}
                    >
                      Approve
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => openReview("reject")}
                    >
                      Reject
                    </Button>
                  </div>
                </div>
              ) : escalation.status === "REQUESTED" && !canReview ? (
                <p className="border-t border-ecmp-border pt-4 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                  Awaiting Head Office Scheduler review.
                </p>
              ) : null}
            </div>
          ) : canRequest && !formOpen ? (
            <div className="space-y-3">
              <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                Request Head Office escalation when branch troubleshooting is
                complete. Review and approval are handled separately.
              </p>
              <Button
                type="button"
                variant="outline"
                onClick={() => setFormOpen(true)}
              >
                Request Escalation
              </Button>
            </div>
          ) : !canRequest ? (
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              {hasResolution
                ? "Escalation is not available after resolution."
                : status !== "IN_PROGRESS"
                  ? "Escalation can be requested only while the complaint is IN PROGRESS."
                  : "No escalation requested."}
            </p>
          ) : null}

          {canRequest && formOpen ? (
            <form
              className="space-y-4 border-t border-ecmp-border pt-4"
              onSubmit={onSubmit}
            >
              <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
                Escalation Request form — Branch to Head Office.
              </p>
              {submitError ? (
                <Alert
                  tone="danger"
                  title="Escalation request failed"
                  description={submitError}
                />
              ) : null}
              <Select
                label="Reason Code"
                name="reasonCode"
                required
                placeholder="Select reason"
                options={REASON_OPTIONS}
                value={reasonCode}
                error={fieldErrors.reasonCode}
                onChange={(event) =>
                  setReasonCode(event.target.value as EscalationReasonCode | "")
                }
              />
              <Textarea
                label="Reason Description"
                name="reasonDescription"
                required
                rows={2}
                value={reasonDescription}
                error={fieldErrors.reasonDescription}
                onChange={(event) => setReasonDescription(event.target.value)}
              />
              <Textarea
                label="Diagnosis"
                name="diagnosis"
                required
                rows={3}
                value={diagnosis}
                error={fieldErrors.diagnosis}
                onChange={(event) => setDiagnosis(event.target.value)}
              />
              <Textarea
                label="Notes"
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
                  Cancel
                </Button>
                <Button type="submit" variant="primary" disabled={submitting}>
                  {submitting ? "Submitting…" : "Submit Request"}
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
            ? "Approve escalation?"
            : "Reject escalation?"
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
              Cancel
            </Button>
            <Button
              type="button"
              variant={reviewAction === "reject" ? "outline" : "primary"}
              disabled={reviewing}
              onClick={() => void confirmReview()}
            >
              {reviewing
                ? "Saving…"
                : reviewAction === "approve"
                  ? "Confirm Approve"
                  : "Confirm Reject"}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
            {reviewAction === "approve"
              ? "Confirm approval for Head Office handling. Complaint status stays IN PROGRESS."
              : "Confirm rejection. The Branch retains ownership. Complaint status stays IN PROGRESS."}
          </p>
          {reviewError ? (
            <Alert
              tone="danger"
              title="Review failed"
              description={reviewError}
            />
          ) : null}
          <Textarea
            label="Review Notes"
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
