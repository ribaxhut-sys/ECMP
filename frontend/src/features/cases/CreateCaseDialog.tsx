"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
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
  const t = useTranslations("cases");
  const tValidation = useTranslations("validation");
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
        err instanceof ApiError ? err.message : t("unableToLoad"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title={mode === "add" ? t("add") : t("create")}
      size="lg"
      footer={
        <>
          <Button variant="ghost" onClick={handleClose} disabled={submitting}>{t("back")}          </Button>
          <Button onClick={submit} loading={submitting}>
            {mode === "add" ? t("add") : t("create")}
          </Button>
        </>
      }
    >
      <ModalSection className="space-y-[var(--ecmp-panel-gap)]">
        {submitError ? (
          <Alert tone="danger" title={t("unableToLoad")} description={submitError} />
        ) : null}
        <Input
          name="caseType"
          label={t("caseType")}
          value={values.caseType}
          onChange={(e) => setField("caseType", e.target.value)}
          error={fieldErrors.caseType ? tValidation(fieldErrors.caseType) : undefined}
          required
        />
        <Input
          name="category"
          label={t("category")}
          value={values.category}
          onChange={(e) => setField("category", e.target.value)}
        />
        <Input
          name="subject"
          label={t("subject")}
          value={values.subject}
          onChange={(e) => setField("subject", e.target.value)}
          error={fieldErrors.subject ? tValidation(fieldErrors.subject) : undefined}
          required
        />
        <Textarea
          name="description"
          label={t("description")}
          value={values.description}
          onChange={(e) => setField("description", e.target.value)}
          error={fieldErrors.description ? tValidation(fieldErrors.description) : undefined}
          required
        />
        <Select
          name="priority"
          label={t("priority")}
          value={values.priority}
          onChange={(e) => setField("priority", e.target.value)}
          options={CASE_PRIORITY_OPTIONS.map((option) => ({ ...option, label: t(option.label) }))}
          error={fieldErrors.priority ? tValidation(fieldErrors.priority) : undefined}
        />
        <Input
          name="destinationUnitId"
          label={t("destinationUnitOptional")}
          value={values.destinationUnitId}
          onChange={(e) => setField("destinationUnitId", e.target.value)}
          hint={t("destinationUnitHint")}
        />
      </ModalSection>
    </Modal>
  );
}
