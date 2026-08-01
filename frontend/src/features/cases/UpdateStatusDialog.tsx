"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import {
  ApiError,
  updateCmCaseStatus,
  type CmCase,
  type CmCaseStatus,
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
  CANCEL_REASON_OPTIONS,
  emptyUpdateStatusForm,
  toUpdateStatusRequest,
  validateUpdateStatusForm,
  type UpdateStatusFormValues,
} from "./caseForms";
import { allowedStatusTargets } from "./caseStatus";

export function UpdateStatusDialog({
  open,
  onClose,
  caseData,
  onUpdated,
}: {
  open: boolean;
  onClose: () => void;
  caseData: CmCase;
  onUpdated?: (caseData: CmCase) => void;
}) {
  const t = useTranslations("cases");
  const tValidation = useTranslations("validation");
  const targets = allowedStatusTargets(caseData.status);
  const [values, setValues] = useState(
    emptyUpdateStatusForm({
      destinationUnitId: caseData.owningUnitId ?? "",
    }),
  );
  const [fieldErrors, setFieldErrors] = useState<
    ReturnType<typeof validateUpdateStatusForm>
  >({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function handleClose() {
    if (submitting) return;
    setValues(
      emptyUpdateStatusForm({
        destinationUnitId: caseData.owningUnitId ?? "",
      }),
    );
    setFieldErrors({});
    setSubmitError(null);
    onClose();
  }

  function setField<K extends keyof UpdateStatusFormValues>(
    key: K,
    value: UpdateStatusFormValues[K],
  ) {
    setValues((prev) => ({ ...prev, [key]: value }));
  }

  async function submit() {
    const errors = validateUpdateStatusForm(values);
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) return;
    setSubmitting(true);
    setSubmitError(null);
    try {
      const res = await updateCmCaseStatus(
        caseData.caseId,
        toUpdateStatusRequest(values),
      );
      onUpdated?.(res.data);
      setValues(
        emptyUpdateStatusForm({
          destinationUnitId: caseData.owningUnitId ?? "",
        }),
      );
      setFieldErrors({});
      setSubmitError(null);
      onClose();
    } catch (err) {
      setSubmitError(
        err instanceof ApiError ? err.message : t("updateFailed"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title={t("updateStatusTitle")}
      footer={
        <>
          <Button variant="ghost" onClick={handleClose} disabled={submitting}>{t("back")}          </Button>
          <Button
            onClick={submit}
            loading={submitting}
            disabled={targets.length === 0}
          >{t("updateStatus")}          </Button>
        </>
      }
    >
      <ModalSection className="space-y-4">
        {submitError ? (
          <Alert
            tone="danger"
            title={t("updateFailed")}
            description={submitError}
          />
        ) : null}
        {targets.length === 0 ? (
          <Alert
            tone="warning"
            title={t("noTransitions")}
            description={t("noTransitionsDescription", { status: caseData.status })}
          />
        ) : (
          <>
            <Select
              name="toStatus"
              label={t("targetStatus")}
              value={values.toStatus}
              onChange={(e) =>
                setField("toStatus", e.target.value as CmCaseStatus | "")
              }
              options={targets.map((t) => ({ value: t, label: t }))}
              placeholder={t("selectStatus")}
              error={fieldErrors.toStatus ? tValidation(fieldErrors.toStatus) : undefined}
            />
            {(values.toStatus === "ASSIGNED" ||
              caseData.status === "CREATED") && (
              <Input
                name="destinationUnitId"
                label={t("destinationUnit")}
                value={values.destinationUnitId}
                onChange={(e) => setField("destinationUnitId", e.target.value)}
                error={fieldErrors.destinationUnitId ? tValidation(fieldErrors.destinationUnitId) : undefined}
              />
            )}
            {values.toStatus === "CANCELLED" ? (
              <>
                <Select
                  name="cancelReason"
                  label={t("cancelReason")}
                  value={values.cancelReason}
                  onChange={(e) =>
                    setField(
                      "cancelReason",
                      e.target.value as UpdateStatusFormValues["cancelReason"],
                    )
                  }
                  options={CANCEL_REASON_OPTIONS.map((option) => ({ ...option, label: t(option.label) }))}
                  error={fieldErrors.cancelReason ? tValidation(fieldErrors.cancelReason) : undefined}
                />
                <Textarea
                  name="reason"
                  label={t("reason")}
                  value={values.reason}
                  onChange={(e) => setField("reason", e.target.value)}
                  error={fieldErrors.reason ? tValidation(fieldErrors.reason) : undefined}
                />
              </>
            ) : null}
          </>
        )}
      </ModalSection>
    </Modal>
  );
}
