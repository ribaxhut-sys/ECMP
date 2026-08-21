"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import {
  ApiError,
  closeCmCase,
  recordCmCaseAcceptance,
  resolveCmCase,
  type CmCase,
} from "@/lib/api";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import {
  Alert,
  Button,
  Modal,
  ModalSection,
  ReasonPresetTags,
  Select,
} from "@/shared/ui";
import { useReasonPresets } from "@/shared/hooks";
import { KnowledgeMentionTextarea } from "@/features/complaints/KnowledgeMentionTextarea";
import {
  emptyResolveCaseForm,
  toResolveCaseRequest,
  validateResolveCaseForm,
  type ResolveCaseFormValues,
} from "./caseForms";

/** Quick-fill presets for the resolve dialog (PUBLIC settings, JSON arrays). */
const RESOLUTION_COMMENT_PRESET_KEY = "case.resolution_comment_presets";
const REJECTION_REASON_PRESET_KEY = "case.rejection_reason_presets";
const PRESET_KEYS = [
  RESOLUTION_COMMENT_PRESET_KEY,
  REJECTION_REASON_PRESET_KEY,
];

const INTENT_OPTIONS: {
  value: ResolveCaseFormValues["intent"];
  label: string;
}[] = [
  { value: "CLOSE", label: "actionClose" },
  { value: "ESCALATE", label: "actionEscalate" },
  { value: "REJECT", label: "actionReject" },
];

/**
 * DEC-021 Mode A resolve dialog:
 * - Tutup → ACCEPT (comment only) + Owner ACCEPT if needed + close when allowed
 * - Eskalasi → parent callback (Aggregate), no Case resolve API
 * - Tolak → REJECT + rejectionReason
 */
export function ResolveCaseDialog({
  open,
  onClose,
  caseId,
  onResolved,
  onEscalate,
}: {
  open: boolean;
  onClose: () => void;
  caseId: string;
  onResolved?: (caseData: CmCase) => void;
  onEscalate?: () => void;
}) {
  const t = useTranslations("cases");
  const tValidation = useTranslations("validation");
  const tErrors = useTranslations("errors");
  const tCommon = useTranslations("common");
  const [values, setValues] = useState(emptyResolveCaseForm());
  const presets = useReasonPresets(PRESET_KEYS);
  const [fieldErrors, setFieldErrors] = useState<
    ReturnType<typeof validateResolveCaseForm>
  >({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function handleClose() {
    if (submitting) return;
    setValues(emptyResolveCaseForm());
    setFieldErrors({});
    setSubmitError(null);
    onClose();
  }

  function setField<K extends keyof ResolveCaseFormValues>(
    key: K,
    value: ResolveCaseFormValues[K],
  ) {
    setValues((prev) => ({ ...prev, [key]: value }));
  }

  async function finishCloseWithComment(comment: string): Promise<CmCase> {
    const resolved = await resolveCmCase(caseId, {
      action: "ACCEPT",
      comment,
    });
    let current = resolved.data;
    if (current.status === "CLOSED") {
      return current;
    }
    if (current.status === "RESOLVED" && !current.ownerAcceptance) {
      try {
        const owned = await recordCmCaseAcceptance(caseId, {
          party: "OWNER",
          decision: "ACCEPT",
          note: comment,
        });
        current = owned.data;
      } catch {
        // Owner acceptance may be forbidden (SoD / role); still try close.
      }
    }
    if (current.status === "CLOSED") {
      return current;
    }
    try {
      const closed = await closeCmCase(caseId, { note: comment });
      return closed.data;
    } catch {
      return current;
    }
  }

  async function submit() {
    const errors = validateResolveCaseForm(values);
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) return;

    if (values.intent === "ESCALATE") {
      handleClose();
      onEscalate?.();
      return;
    }

    setSubmitting(true);
    setSubmitError(null);
    try {
      if (values.intent === "CLOSE") {
        const next = await finishCloseWithComment(values.comment.trim());
        onResolved?.(next);
      } else {
        const res = await resolveCmCase(caseId, toResolveCaseRequest(values));
        onResolved?.(res.data);
      }
      setValues(emptyResolveCaseForm());
      setFieldErrors({});
      setSubmitError(null);
      onClose();
    } catch (err) {
      setSubmitError(
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : t("resolveFailed"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title={t("resolveTitle")}
      size="lg"
      footer={
        <>
          <Button variant="ghost" onClick={handleClose} disabled={submitting}>
            {t("back")}
          </Button>
          <Button onClick={() => void submit()} loading={submitting}>
            {values.intent === "ESCALATE"
              ? t("continueEscalate")
              : t("submitResolution")}
          </Button>
        </>
      }
    >
      <ModalSection className="space-y-[var(--ecmp-panel-gap)]">
        {submitError ? (
          <Alert
            tone="danger"
            title={t("resolveFailed")}
            description={submitError}
          />
        ) : null}
        <Select
          name="intent"
          label={t("action")}
          value={values.intent}
          onChange={(e) =>
            setField(
              "intent",
              e.target.value as ResolveCaseFormValues["intent"],
            )
          }
          options={INTENT_OPTIONS.map((option) => ({
            ...option,
            label: t(option.label),
          }))}
        />
        {values.intent === "ESCALATE" ? (
          <Alert
            tone="info"
            title={t("escalateViaParentTitle")}
            description={t("escalateViaParentBody")}
          />
        ) : null}
        {values.intent === "CLOSE" ? (
          <Alert
            tone="info"
            title={t("closeCommentOnlyTitle")}
            description={t("closeCommentOnlyBody")}
          />
        ) : null}
        {values.intent !== "ESCALATE" ? (
          <>
            <ReasonPresetTags
              presets={presets[RESOLUTION_COMMENT_PRESET_KEY] ?? []}
              onSelect={(preset) => setField("comment", preset)}
            />
            <KnowledgeMentionTextarea
              name="comment"
              label={t("commentRequired")}
              value={values.comment}
              onChange={(next) => setField("comment", next)}
              error={
                fieldErrors.comment
                  ? tValidation(fieldErrors.comment)
                  : undefined
              }
              required
            />
          </>
        ) : null}
        {values.intent === "REJECT" ? (
          <>
            <ReasonPresetTags
              presets={presets[REJECTION_REASON_PRESET_KEY] ?? []}
              onSelect={(preset) => setField("rejectionReason", preset)}
            />
            <KnowledgeMentionTextarea
              name="rejectionReason"
              label={t("rejectionReason")}
              value={values.rejectionReason}
              onChange={(next) => setField("rejectionReason", next)}
              error={
                fieldErrors.rejectionReason
                  ? tValidation(fieldErrors.rejectionReason)
                  : undefined
              }
              required
            />
          </>
        ) : null}
      </ModalSection>
    </Modal>
  );
}
