"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { ApiError, closeCmCase, type CmCase } from "@/lib/api";
import { Alert, Button, Modal, ModalSection, Textarea } from "@/shared/ui";
import { emptyCloseCaseForm, toCloseCaseRequest } from "./caseForms";

export function CloseCaseDialog({
  open,
  onClose,
  caseId,
  onClosed,
}: {
  open: boolean;
  onClose: () => void;
  caseId: string;
  onClosed?: (caseData: CmCase) => void;
}) {
  const t = useTranslations("cases");
  const [note, setNote] = useState("");
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function handleClose() {
    if (submitting) return;
    setNote("");
    setSubmitError(null);
    onClose();
  }

  async function submit() {
    setSubmitting(true);
    setSubmitError(null);
    try {
      const res = await closeCmCase(
        caseId,
        toCloseCaseRequest({ ...emptyCloseCaseForm(), note }),
      );
      onClosed?.(res.data);
      setNote("");
      setSubmitError(null);
      onClose();
    } catch (err) {
      setSubmitError(
        err instanceof ApiError ? err.message : t("closeFailed"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title={t("closeTitle")}
      footer={
        <>
          <Button variant="ghost" onClick={handleClose} disabled={submitting}>{t("back")}          </Button>
          <Button onClick={submit} loading={submitting}>{t("close")}          </Button>
        </>
      }
    >
      <ModalSection className="space-y-4">
        {submitError ? (
          <Alert tone="danger" title={t("closeFailed")} description={submitError} />
        ) : null}
        <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
          {t("closeChecklist")}
        </p>
        <Textarea
          name="note"
          label={t("noteOptional")}
          value={note}
          onChange={(e) => setNote(e.target.value)}
          hint={t("closeHint")}
        />
      </ModalSection>
    </Modal>
  );
}
