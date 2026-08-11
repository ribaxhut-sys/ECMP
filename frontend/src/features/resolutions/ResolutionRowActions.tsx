"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
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
  Checkbox,
  Input,
  Modal,
  Select,
  Textarea,
} from "@/shared/ui";
import { useToast } from "@/shared/providers";
import { KnowledgeMentionTextarea } from "@/features/complaints/KnowledgeMentionTextarea";

const CATEGORY_VALUES: readonly ResolutionCategory[] = [
  "SOLVED",
  "WORKAROUND",
  "DUPLICATE",
  "INVALID_REQUEST",
  "USER_ERROR",
  "THIRD_PARTY",
];

const REASON_CODE_VALUES: readonly EscalationReasonCode[] = [
  "SPECIALIST_REQUIRED",
  "COMPLEX_CASE",
  "POLICY_EXCEPTION",
  "CUSTOMER_REQUEST",
  "OTHER",
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
  const { pushSuccess } = useToast();
  const t = useTranslations("resolutions");
  const tCommon = useTranslations("common");
  const tComplaints = useTranslations("complaints");
  const tCategory = useTranslations("resolutionCategory");
  const tReason = useTranslations("escalationReason");
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
      let successTitle = "";
      if (action === "resolve") {
        if (!category) {
          setError(tComplaints("categoryRequired"));
          setSubmitting(false);
          return;
        }
        if (!rootCause.trim() || !resolutionNotes.trim()) {
          setError(t("rootCauseAndNotesRequired"));
          setSubmitting(false);
          return;
        }
        await submitResolution(row.id, {
          resolutionCategory: category,
          rootCause: rootCause.trim(),
          resolutionNotes: resolutionNotes.trim(),
          resolvedBy: userId ?? undefined,
        });
        successTitle = t("resolutionSubmitted");
      } else if (action === "final") {
        if (!finalSummary.trim() || !finalNotes.trim()) {
          setError(t("summaryAndNotesRequired"));
          setSubmitting(false);
          return;
        }
        await submitFinalResolutionForComplaint(row.id, {
          summary: finalSummary.trim(),
          notes: finalNotes.trim(),
          followUpRequired,
        });
        successTitle = tComplaints("finalResolutionSubmitted");
      } else if (action === "escalate") {
        if (!reasonCode) {
          setError(tComplaints("reasonCodeRequired"));
          setSubmitting(false);
          return;
        }
        if (!reasonDescription.trim() || !diagnosis.trim()) {
          setError(t("reasonDescriptionAndDiagnosisRequired"));
          setSubmitting(false);
          return;
        }
        await requestEscalationForComplaint(row.id, {
          reasonCode,
          reasonDescription: reasonDescription.trim(),
          diagnosis: diagnosis.trim(),
          notes: escalateNotes.trim() || null,
        });
        successTitle = tComplaints("escalationRequested");
      } else if (action === "closeEscalation") {
        if (!row.escalation?.id) {
          setError(t("noEscalationToClose"));
          setSubmitting(false);
          return;
        }
        if (!closeNotes.trim()) {
          setError(tComplaints("closureNotesRequired"));
          setSubmitting(false);
          return;
        }
        await closeEscalationForComplaint(row.escalation.id, {
          notes: closeNotes.trim(),
        });
        successTitle = tComplaints("escalationClosed");
      } else if (action === "closeComplaint") {
        if (!closeNotes.trim()) {
          setError(tComplaints("closureNotesRequired"));
          setSubmitting(false);
          return;
        }
        await closeComplaintFromResolution(row.id, {
          notes: closeNotes.trim(),
        });
        successTitle = tComplaints("complaintClosed");
      }
      setAction(null);
      if (successTitle) {
        pushSuccess(successTitle, t("listRefreshed"));
      }
      onChanged?.();
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : t("actionFailed"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  const modalTitle =
    action === "resolve"
      ? t("submitResolutionConfirm")
      : action === "final"
        ? t("submitFinalResolutionConfirm")
        : action === "escalate"
          ? t("requestEscalationConfirm")
          : action === "closeEscalation"
            ? tComplaints("closeEscalationConfirm")
            : action === "closeComplaint"
              ? tComplaints("closeComplaintConfirm")
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
            {t("resolveButton")}
          </Button>
        ) : null}
        {showFinal ? (
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={() => openAction("final")}
          >
            {t("finalButton")}
          </Button>
        ) : null}
        {showEscalate ? (
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={() => openAction("escalate")}
          >
            {tComplaints("escalate")}
          </Button>
        ) : null}
        {showCloseEscalation ? (
          <Button
            type="button"
            size="sm"
            variant="ghost"
            onClick={() => openAction("closeEscalation")}
          >
            {t("closeEscButton")}
          </Button>
        ) : null}
        {showCloseComplaint ? (
          <Button
            type="button"
            size="sm"
            variant="ghost"
            onClick={() => openAction("closeComplaint")}
          >
            {tCommon("close")}
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
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              disabled={submitting}
              onClick={() => void confirmAction()}
            >
              {submitting ? t("working") : tCommon("confirm")}
            </Button>
          </>
        }
      >
        <div className="space-y-[var(--ecmp-panel-gap)]">
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
            {row.complaintNumber} — {row.subject}
          </p>

          {action === "resolve" ? (
            <>
              <Select
                label={tComplaints("category")}
                name="resolutionCategory"
                required
                placeholder={tComplaints("selectCategoryPlaceholder")}
                value={category}
                options={CATEGORY_VALUES.map((value) => ({
                  value,
                  label: tCategory(value),
                }))}
                disabled={submitting}
                onChange={(e) =>
                  setCategory(e.target.value as ResolutionCategory | "")
                }
              />
              <Input
                label={tComplaints("rootCause")}
                name="rootCause"
                required
                value={rootCause}
                maxLength={2000}
                disabled={submitting}
                onChange={(e) => setRootCause(e.target.value)}
              />
              <KnowledgeMentionTextarea
                label={tComplaints("resolutionNotes")}
                name="resolutionNotes"
                required
                rows={4}
                maxLength={5000}
                value={resolutionNotes}
                disabled={submitting}
                onChange={setResolutionNotes}
              />
            </>
          ) : null}

          {action === "final" ? (
            <>
              <Textarea
                label={tComplaints("summary")}
                name="summary"
                required
                rows={3}
                maxLength={5000}
                value={finalSummary}
                disabled={submitting}
                onChange={(e) => setFinalSummary(e.target.value)}
              />
              <Textarea
                label={tComplaints("notes")}
                name="notes"
                required
                rows={3}
                maxLength={5000}
                value={finalNotes}
                disabled={submitting}
                onChange={(e) => setFinalNotes(e.target.value)}
              />
              <Checkbox
                name="followUpRequired"
                label={tComplaints("followUpRequired")}
                checked={followUpRequired}
                disabled={submitting}
                onChange={(e) => setFollowUpRequired(e.target.checked)}
              />
            </>
          ) : null}

          {action === "escalate" ? (
            <>
              <Select
                label={tComplaints("reasonCode")}
                name="reasonCode"
                required
                placeholder={tComplaints("selectReasonPlaceholder")}
                value={reasonCode}
                options={REASON_CODE_VALUES.map((value) => ({
                  value,
                  label: tReason(value),
                }))}
                disabled={submitting}
                onChange={(e) =>
                  setReasonCode(e.target.value as EscalationReasonCode | "")
                }
              />
              <Textarea
                label={tComplaints("reasonDescription")}
                name="reasonDescription"
                required
                rows={3}
                maxLength={2000}
                value={reasonDescription}
                disabled={submitting}
                onChange={(e) => setReasonDescription(e.target.value)}
              />
              <Textarea
                label={tComplaints("diagnosis")}
                name="diagnosis"
                required
                rows={3}
                maxLength={5000}
                value={diagnosis}
                disabled={submitting}
                onChange={(e) => setDiagnosis(e.target.value)}
              />
              <Textarea
                label={t("notesOptionalLabel")}
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
              label={tComplaints("closureNotes")}
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
            <Alert tone="danger" title={t("actionFailed")} description={error} />
          ) : null}
        </div>
      </Modal>
    </>
  );
}
