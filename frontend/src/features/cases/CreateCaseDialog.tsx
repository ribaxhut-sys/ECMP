"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { ApiError, addCmCase, createCmCase, type CmCase } from "@/lib/api";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
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
  mergeCreateCaseForm,
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
  initialValues,
  onCreated,
}: {
  open: boolean;
  onClose: () => void;
  complaintId: string;
  mode?: "create" | "add";
  initialValues?: Partial<CreateCaseFormValues> | null;
  onCreated?: (caseData: CmCase) => void;
}) {
  const t = useTranslations("cases");
  const tValidation = useTranslations("validation");
  const tErrors = useTranslations("errors");
  const tCommon = useTranslations("common");
  const [values, setValues] = useState<CreateCaseFormValues>(emptyCreateCaseForm());
  const [fieldErrors, setFieldErrors] = useState<
    ReturnType<typeof validateCreateCaseForm>
  >({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!open) return;
    setValues(mergeCreateCaseForm(initialValues));
    setFieldErrors({});
    setSubmitError(null);
  }, [open, initialValues]);

  const branchUnitLocked = Boolean(values.destinationUnitId.trim());

  function handleClose() {
    if (submitting) return;
    setValues(emptyCreateCaseForm());
    setFieldErrors({});
    setSubmitError(null);
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
      setValues(emptyCreateCaseForm());
      onClose();
    } catch (err) {
      setSubmitError(
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : t("unableToLoad"),
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
          <Button variant="ghost" onClick={handleClose} disabled={submitting}>
            {t("back")}
          </Button>
          <Button onClick={submit} loading={submitting}>
            {mode === "add" ? t("add") : t("create")}
          </Button>
        </>
      }
    >
      <ModalSection className="space-y-[var(--ecmp-panel-gap)]">
        {mode === "create" ? (
          <Alert
            tone="info"
            title={t("branchWorkBannerTitle")}
            description={t("branchWorkBannerDescription")}
          />
        ) : null}
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
          error={
            fieldErrors.description
              ? tValidation(fieldErrors.description)
              : undefined
          }
          required
        />
        <Select
          name="priority"
          label={t("priority")}
          value={values.priority}
          onChange={(e) => setField("priority", e.target.value)}
          options={CASE_PRIORITY_OPTIONS.map((option) => ({
            ...option,
            label: t(option.label),
          }))}
          error={fieldErrors.priority ? tValidation(fieldErrors.priority) : undefined}
        />
        {branchUnitLocked ? (
          <Alert
            tone="success"
            title={t("branchUnitAssignedTitle")}
            description={t("branchUnitAssignedDescription")}
          />
        ) : (
          <Input
            name="destinationUnitId"
            label={t("destinationUnitOptional")}
            value={values.destinationUnitId}
            onChange={(e) => setField("destinationUnitId", e.target.value)}
            hint={t("destinationUnitHint")}
          />
        )}
      </ModalSection>
    </Modal>
  );
}
