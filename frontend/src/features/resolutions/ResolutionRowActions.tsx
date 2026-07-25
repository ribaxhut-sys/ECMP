"use client";

import { useState } from "react";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  closeComplaintFromResolution,
  closeEscalationForComplaint,
  requestEscalationForComplaint,
  submitFinalResolutionForComplaint,
  submitResolution,
} from "@/lib/api";
import type {
  ComplaintStatus,
  Escalation,
  EscalationReasonCode,
  FinalResolutionDetail,
  Resolution,
  ResolutionCategory,
} from "@/lib/api/types";
import {
  Alert,
  Button,
  Input,
  Modal,
  Select,
  Textarea,
  Toast,
} from "@/shared/ui";

const CATEGORY_OPTIONS: ReadonlyArray<{
  value: ResolutionCategory;
  label: string;
}> = [
  { value: "SOLVED", label: "Solved" },
  { value: "WORKAROUND", label: "Workaround" },
  { value: "DUPLICATE", label: "Duplicate" },
  { value: "INVALID_REQUEST", label: "Invalid Request" },
  { value: "USER_ERROR", label: "User Error" },
  { value: "THIRD_PARTY", label: "Third Party" },
];

const REASON_CODE_OPTIONS: ReadonlyArray<{
  value: EscalationReasonCode;
  label: string;
}> = [
  { value: "SPECIALIST_REQUIRED", label: "Specialist required" },
  { value: "COMPLEX_CASE", label: "Complex case" },
  { value: "POLICY_EXCEPTION", label: "Policy exception" },
  { value: "CUSTOMER_REQUEST", label: "Customer request" },
  { value: "OTHER", label: "Other" },
];

export type ResolutionRowMeta = {
  id: string;
  complaintNumber: string;
  subject: string;
  status: ComplaintStatus;
  closedAt: string | null;
  resolution: Resolution | null;
  finalResolution: FinalResolutionDetail | null;
  escalation: Escalation | null;
};

type ActionKind =
  | "resolve"
  | "final"
  | "escalate"
  | "closeEscalation"
  | "closeComplaint"
  | null;

function blocksNewEscalation(row: Escalation | null): boolean {
  if (!row) return false;
  const status = row.status.toUpperCase();
  return (
    status === "REQUESTED" ||
    status === "OPEN" ||
    status === "APPROVED" ||
    status === "IN_PROGRESS"
  );
}

export function ResolutionRowActions({
  row,
  onChanged,
}: {
  row: ResolutionRowMeta;
  onChanged?: () => void;
}) {
  const { hasPermission, userId } = useAuth();
  const canResolve = hasPermission("complaints:update");
  const canFinal = hasPermission("appointments:complete");
  const canEscalate = hasPermission("complaints:update");
  const canCloseEscalation = hasPermission("escalations:close");
  const canCloseComplaint = hasPermission("complaints:close");

  const isClosed = row.status === "CLOSED" || Boolean(row.closedAt);
  const hasResolution = Boolean(row.resolution);
  const hasFinal = Boolean(row.finalResolution);
  const escalationOpen =
    row.escalation != null &&
    row.escalation.status.toUpperCase() !== "CLOSED";

  const showResolve = canResolve && !hasResolution && !isClosed;
  const showFinal = canFinal && !hasFinal && !isClosed;
  const showEscalate =
    canEscalate &&
    !hasResolution &&
    !blocksNewEscalation(row.escalation) &&
    !isClosed;
  const showCloseEscalation =
    canCloseEscalation && escalationOpen && Boolean(row.escalation?.id);
  const showCloseComplaint = canCloseComplaint && !isClosed;

  const [action, setAction] = useState<ActionKind>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toastOpen, setToastOpen] = useState(false);
  const [toastTitle, setToastTitle] = useState("");

  // Resolve form
  const [category, setCategory] = useState<ResolutionCategory | "">("");
  const [rootCause, setRootCause] = useState("");
  const [resolutionNotes, setResolutionNotes] = useState("");

  // Final form
  const [finalSummary, setFinalSummary] = useState("");
  const [finalNotes, setFinalNotes] = useState("");
  const [followUpRequired, setFollowUpRequired] = useState(false);

  // Escalate form
  const [reasonCode, setReasonCode] = useState<EscalationReasonCode | "">("");
  const [reasonDescription, setReasonDescription] = useState("");
  const [diagnosis, setDiagnosis] = useState("");
  const [escalateNotes, setEscalateNotes] = useState("");

  // Close forms
  const [closeNotes, setCloseNotes] = useState("");

  if (
    !showResolve &&
    !showFinal &&
    !showEscalate &&
    !showCloseEscalation &&
    !showCloseComplaint
  ) {
    return null;
  }

  function openAction(next: ActionKind) {
    setError(null);
    setCategory("");
    setRootCause("");
    setResolutionNotes("");
    setFinalSummary("");
    setFinalNotes("");
    setFollowUpRequired(false);
    setReasonCode("");
    setReasonDescription("");
    setDiagnosis("");
    setEscalateNotes("");
    setCloseNotes("");
    setAction(next);
  }

  function closeAction() {
    if (submitting) return;
    setAction(null);
    setError(null);
  }

  async function confirmAction() {
    setSubmitting(true);
    setError(null);
    try {
      if (action === "resolve") {
        if (!category) {
          setError("Category is required.");
          setSubmitting(false);
          return;
        }
        if (!rootCause.trim() || !resolutionNotes.trim()) {
          setError("Root cause and resolution notes are required.");
          setSubmitting(false);
          return;
        }
        await submitResolution(row.id, {
          resolutionCategory: category,
          rootCause: rootCause.trim(),
          resolutionNotes: resolutionNotes.trim(),
          resolvedBy: userId ?? undefined,
        });
        setToastTitle("Resolution submitted");
      } else if (action === "final") {
        if (!finalSummary.trim() || !finalNotes.trim()) {
          setError("Summary and notes are required.");
          setSubmitting(false);
          return;
        }
        await submitFinalResolutionForComplaint(row.id, {
          summary: finalSummary.trim(),
          notes: finalNotes.trim(),
          followUpRequired,
        });
        setToastTitle("Final resolution submitted");
      } else if (action === "escalate") {
        if (!reasonCode) {
          setError("Reason code is required.");
          setSubmitting(false);
          return;
        }
        if (!reasonDescription.trim() || !diagnosis.trim()) {
          setError("Reason description and diagnosis are required.");
          setSubmitting(false);
          return;
        }
        await requestEscalationForComplaint(row.id, {
          reasonCode,
          reasonDescription: reasonDescription.trim(),
          diagnosis: diagnosis.trim(),
          notes: escalateNotes.trim() || null,
        });
        setToastTitle("Escalation requested");
      } else if (action === "closeEscalation") {
        if (!row.escalation?.id) {
          setError("No escalation to close.");
          setSubmitting(false);
          return;
        }
        if (!closeNotes.trim()) {
          setError("Closure notes are required.");
          setSubmitting(false);
          return;
        }
        await closeEscalationForComplaint(row.escalation.id, {
          notes: closeNotes.trim(),
        });
        setToastTitle("Escalation closed");
      } else if (action === "closeComplaint") {
        if (!closeNotes.trim()) {
          setError("Closure notes are required.");
          setSubmitting(false);
          return;
        }
        await closeComplaintFromResolution(row.id, {
          notes: closeNotes.trim(),
        });
        setToastTitle("Complaint closed");
      }
      setAction(null);
      setToastOpen(true);
      onChanged?.();
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Action failed.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  const modalTitle =
    action === "resolve"
      ? "Submit resolution?"
      : action === "final"
        ? "Submit final resolution?"
        : action === "escalate"
          ? "Request escalation?"
          : action === "closeEscalation"
            ? "Close escalation?"
            : action === "closeComplaint"
              ? "Close complaint?"
              : "";

  return (
    <>
      <div className="flex flex-wrap gap-2">
        {showResolve ? (
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={() => openAction("resolve")}
          >
            Resolve
          </Button>
        ) : null}
        {showFinal ? (
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={() => openAction("final")}
          >
            Final
          </Button>
        ) : null}
        {showEscalate ? (
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={() => openAction("escalate")}
          >
            Escalate
          </Button>
        ) : null}
        {showCloseEscalation ? (
          <Button
            type="button"
            size="sm"
            variant="ghost"
            onClick={() => openAction("closeEscalation")}
          >
            Close esc.
          </Button>
        ) : null}
        {showCloseComplaint ? (
          <Button
            type="button"
            size="sm"
            variant="ghost"
            onClick={() => openAction("closeComplaint")}
          >
            Close
          </Button>
        ) : null}
      </div>

      <Modal
        open={action !== null}
        onClose={closeAction}
        title={modalTitle}
        size="md"
        footer={
          <>
            <Button
              type="button"
              variant="outline"
              disabled={submitting}
              onClick={closeAction}
            >
              Cancel
            </Button>
            <Button
              type="button"
              disabled={submitting}
              onClick={() => void confirmAction()}
            >
              {submitting ? "Working…" : "Confirm"}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
            {row.complaintNumber} — {row.subject}
          </p>

          {action === "resolve" ? (
            <>
              <Select
                label="Category"
                name="resolutionCategory"
                required
                placeholder="Select category"
                value={category}
                options={CATEGORY_OPTIONS.map((o) => ({
                  value: o.value,
                  label: o.label,
                }))}
                disabled={submitting}
                onChange={(e) =>
                  setCategory(e.target.value as ResolutionCategory | "")
                }
              />
              <Input
                label="Root cause"
                name="rootCause"
                required
                value={rootCause}
                maxLength={2000}
                disabled={submitting}
                onChange={(e) => setRootCause(e.target.value)}
              />
              <Textarea
                label="Resolution notes"
                name="resolutionNotes"
                required
                rows={4}
                maxLength={5000}
                value={resolutionNotes}
                disabled={submitting}
                onChange={(e) => setResolutionNotes(e.target.value)}
              />
            </>
          ) : null}

          {action === "final" ? (
            <>
              <Textarea
                label="Summary"
                name="summary"
                required
                rows={3}
                maxLength={5000}
                value={finalSummary}
                disabled={submitting}
                onChange={(e) => setFinalSummary(e.target.value)}
              />
              <Textarea
                label="Notes"
                name="notes"
                required
                rows={3}
                maxLength={5000}
                value={finalNotes}
                disabled={submitting}
                onChange={(e) => setFinalNotes(e.target.value)}
              />
              <label className="flex items-center gap-2 text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                <input
                  type="checkbox"
                  className="size-4 rounded border-ecmp-border"
                  checked={followUpRequired}
                  disabled={submitting}
                  onChange={(e) => setFollowUpRequired(e.target.checked)}
                />
                Follow-up required
              </label>
            </>
          ) : null}

          {action === "escalate" ? (
            <>
              <Select
                label="Reason code"
                name="reasonCode"
                required
                placeholder="Select reason"
                value={reasonCode}
                options={REASON_CODE_OPTIONS.map((o) => ({
                  value: o.value,
                  label: o.label,
                }))}
                disabled={submitting}
                onChange={(e) =>
                  setReasonCode(e.target.value as EscalationReasonCode | "")
                }
              />
              <Textarea
                label="Reason description"
                name="reasonDescription"
                required
                rows={3}
                maxLength={2000}
                value={reasonDescription}
                disabled={submitting}
                onChange={(e) => setReasonDescription(e.target.value)}
              />
              <Textarea
                label="Diagnosis"
                name="diagnosis"
                required
                rows={3}
                maxLength={5000}
                value={diagnosis}
                disabled={submitting}
                onChange={(e) => setDiagnosis(e.target.value)}
              />
              <Textarea
                label="Notes (optional)"
                name="notes"
                rows={2}
                maxLength={5000}
                value={escalateNotes}
                disabled={submitting}
                onChange={(e) => setEscalateNotes(e.target.value)}
              />
            </>
          ) : null}

          {action === "closeEscalation" || action === "closeComplaint" ? (
            <Textarea
              label="Closure notes"
              name="notes"
              required
              rows={4}
              maxLength={5000}
              value={closeNotes}
              disabled={submitting}
              onChange={(e) => setCloseNotes(e.target.value)}
            />
          ) : null}

          {error ? (
            <Alert tone="danger" title="Action failed" description={error} />
          ) : null}
        </div>
      </Modal>

      <Toast
        open={toastOpen}
        title={toastTitle}
        description="Resolution list refreshed."
        onClose={() => setToastOpen(false)}
      />
    </>
  );
}
