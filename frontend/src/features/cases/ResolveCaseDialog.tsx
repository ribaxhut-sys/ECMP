"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import {
  ApiError,
  resolveCmCase,
  type CmCase,
  type CmCaseResolveAction,
} from "@/lib/api";
import {
  Alert,
  Button,
  Input,
  Modal,
  ModalSection,
  Select,
  Textarea,
} from "@/shared/ui";
import {
  emptyResolveCaseForm,
  toResolveCaseRequest,
  validateResolveCaseForm,
  type ResolveCaseFormValues,
} from "./caseForms";

const ACTION_OPTIONS: { value: CmCaseResolveAction; label: string }[] = [
  { value: "ACCEPT", label: "actionAccept" },
  { value: "PROPOSE", label: "actionPropose" },
  { value: "REJECT", label: "actionReject" },
];

export function ResolveCaseDialog({
  open,
  onClose,
  caseId,
  onResolved,
}: {
  open: boolean;
  onClose: () => void;
  caseId: string;
  onResolved?: (caseData: CmCase) => void;
}) {
  const t = useTranslations("cases");
  const tValidation = useTranslations("validation");
  const [values, setValues] = useState(emptyResolveCaseForm());
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

  async function submit() {
    const errors = validateResolveCaseForm(values);
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) return;
    setSubmitting(true);
    setSubmitError(null);
    try {
      const res = await resolveCmCase(caseId, toResolveCaseRequest(values));
      onResolved?.(res.data);
      setValues(emptyResolveCaseForm());
      setFieldErrors({});
      setSubmitError(null);
      onClose();
    } catch (err) {
      setSubmitError(
        err instanceof ApiError ? err.message : t("resolveFailed"),
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
          <Button variant="ghost" onClick={handleClose} disabled={submitting}>{t("back")}          </Button>
          <Button onClick={submit} loading={submitting}>{t("submitResolution")}          </Button>
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
          name="action"
          label={t("action")}
          value={values.action}
          onChange={(e) =>
            setField("action", e.target.value as CmCaseResolveAction)
          }
          options={ACTION_OPTIONS.map((option) => ({ ...option, label: t(option.label) }))}
        />
        <Textarea
          name="comment"
          label={t("commentRequired")}
          value={values.comment}
          onChange={(e) => setField("comment", e.target.value)}
          error={fieldErrors.comment ? tValidation(fieldErrors.comment) : undefined}
          required
        />
        {values.action !== "REJECT" ? (
          <>
            <Input
              name="resolutionCode"
              label={t("resolutionCode")}
              value={values.resolutionCode}
              onChange={(e) => setField("resolutionCode", e.target.value)}
              error={fieldErrors.resolutionCode ? tValidation(fieldErrors.resolutionCode) : undefined}
              required
            />
            <Input
              name="summary"
              label={t("summary")}
              value={values.summary}
              onChange={(e) => setField("summary", e.target.value)}
              error={fieldErrors.summary ? tValidation(fieldErrors.summary) : undefined}
              required
            />
            <Textarea
              name="detail"
              label={t("detailLabel")}
              value={values.detail}
              onChange={(e) => setField("detail", e.target.value)}
            />
          </>
        ) : (
          <Textarea
            name="rejectionReason"
            label={t("rejectionReason")}
            value={values.rejectionReason}
            onChange={(e) => setField("rejectionReason", e.target.value)}
            error={fieldErrors.rejectionReason ? tValidation(fieldErrors.rejectionReason) : undefined}
            required
          />
        )}
      </ModalSection>
    </Modal>
  );
}
