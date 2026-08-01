"use client";

import { useState } from "react";
import { ApiError, addCmCase, createCmCase, type CmCase } from "@/lib/api";
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
  CASE_PRIORITY_OPTIONS,
  emptyCreateCaseForm,
  toAddCaseRequest,
  toCreateCaseRequest,
  validateCreateCaseForm,
  type CreateCaseFormValues,
} from "./caseForms";
import { rememberCaseId } from "./caseSessionRegistry";

export function CreateCaseDialog({
  open,
  onClose,
  complaintId,
  mode = "create",
  onCreated,
}: {
  open: boolean;
  onClose: () => void;
  complaintId: string;
  mode?: "create" | "add";
  onCreated?: (caseData: CmCase) => void;
}) {
  const [values, setValues] = useState<CreateCaseFormValues>(emptyCreateCaseForm());
  const [fieldErrors, setFieldErrors] = useState<
    ReturnType<typeof validateCreateCaseForm>
  >({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function reset() {
    setValues(emptyCreateCaseForm());
    setFieldErrors({});
    setSubmitError(null);
  }

  function handleClose() {
    if (submitting) return;
    reset();
    onClose();
  }

  function setField<K extends keyof CreateCaseFormValues>(
    key: K,
    value: CreateCaseFormValues[K],
  ) {
    setValues((prev) => ({ ...prev, [key]: value }));
  }

  async function submit() {
    const errors = validateCreateCaseForm(values);
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) return;

    setSubmitting(true);
    setSubmitError(null);
    try {
      const res =
        mode === "add"
          ? await addCmCase(complaintId, toAddCaseRequest(values), {
              idempotencyKey:
                typeof crypto !== "undefined" && crypto.randomUUID
                  ? crypto.randomUUID()
                  : undefined,
            })
          : await createCmCase(toCreateCaseRequest(complaintId, values), {
              idempotencyKey:
                typeof crypto !== "undefined" && crypto.randomUUID
                  ? crypto.randomUUID()
                  : undefined,
            });
      rememberCaseId(complaintId, res.data.caseId);
      onCreated?.(res.data);
      reset();
      onClose();
    } catch (err) {
      setSubmitError(
        err instanceof ApiError ? err.message : "Unable to create case.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title={mode === "add" ? "Add Case" : "Create Case"}
      size="lg"
      footer={
        <>
          <Button variant="ghost" onClick={handleClose} disabled={submitting}>
            Cancel
          </Button>
          <Button onClick={submit} loading={submitting}>
            {mode === "add" ? "Add Case" : "Create Case"}
          </Button>
        </>
      }
    >
      <ModalSection className="space-y-4">
        {submitError ? (
          <Alert tone="danger" title="Create failed" description={submitError} />
        ) : null}
        <Input
          name="caseType"
          label="Case type"
          value={values.caseType}
          onChange={(e) => setField("caseType", e.target.value)}
          error={fieldErrors.caseType}
          required
        />
        <Input
          name="category"
          label="Category"
          value={values.category}
          onChange={(e) => setField("category", e.target.value)}
        />
        <Input
          name="subject"
          label="Subject"
          value={values.subject}
          onChange={(e) => setField("subject", e.target.value)}
          error={fieldErrors.subject}
          required
        />
        <Textarea
          name="description"
          label="Description"
          value={values.description}
          onChange={(e) => setField("description", e.target.value)}
          error={fieldErrors.description}
          required
        />
        <Select
          name="priority"
          label="Priority"
          value={values.priority}
          onChange={(e) => setField("priority", e.target.value)}
          options={[...CASE_PRIORITY_OPTIONS]}
          error={fieldErrors.priority}
        />
        <Input
          name="destinationUnitId"
          label="Destination unit (optional → ASSIGNED)"
          value={values.destinationUnitId}
          onChange={(e) => setField("destinationUnitId", e.target.value)}
          hint="Leave empty for CREATED. Unit assignment only (BQ-006)."
        />
      </ModalSection>
    </Modal>
  );
}
