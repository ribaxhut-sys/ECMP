"use client";

import { useState } from "react";
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
  { value: "ACCEPT", label: "Accept (→ RESOLVED)" },
  { value: "PROPOSE", label: "Propose (pending approval)" },
  { value: "REJECT", label: "Reject proposal" },
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
        err instanceof ApiError ? err.message : "Unable to resolve case.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title="Resolve Case"
      size="lg"
      footer={
        <>
          <Button variant="ghost" onClick={handleClose} disabled={submitting}>
            Cancel
          </Button>
          <Button onClick={submit} loading={submitting}>
            Submit resolution
          </Button>
        </>
      }
    >
      <ModalSection className="space-y-4">
        {submitError ? (
          <Alert
            tone="danger"
            title="Resolve failed"
            description={submitError}
          />
        ) : null}
        <Select
          name="action"
          label="Action"
          value={values.action}
          onChange={(e) =>
            setField("action", e.target.value as CmCaseResolveAction)
          }
          options={ACTION_OPTIONS}
        />
        <Textarea
          name="comment"
          label="Comment (required)"
          value={values.comment}
          onChange={(e) => setField("comment", e.target.value)}
          error={fieldErrors.comment}
          required
        />
        {values.action !== "REJECT" ? (
          <>
            <Input
              name="resolutionCode"
              label="Resolution code"
              value={values.resolutionCode}
              onChange={(e) => setField("resolutionCode", e.target.value)}
              error={fieldErrors.resolutionCode}
              required
            />
            <Input
              name="summary"
              label="Summary"
              value={values.summary}
              onChange={(e) => setField("summary", e.target.value)}
              error={fieldErrors.summary}
              required
            />
            <Textarea
              name="detail"
              label="Detail"
              value={values.detail}
              onChange={(e) => setField("detail", e.target.value)}
            />
          </>
        ) : (
          <Textarea
            name="rejectionReason"
            label="Rejection reason"
            value={values.rejectionReason}
            onChange={(e) => setField("rejectionReason", e.target.value)}
            error={fieldErrors.rejectionReason}
            required
          />
        )}
      </ModalSection>
    </Modal>
  );
}
