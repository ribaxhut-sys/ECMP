"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { ApiError, closeCmCase, type CmCase } from "@/lib/api";
import { resolveApiErrorMessage } from "@/shared/i18n/resolveApiErrorMessage";
import {
  Alert,
  Button,
  Modal,
  ModalSection,
} from "@/shared/ui";
import { useReasonPresets } from "@/shared/hooks";
import { PresetTextField } from "@/features/complaints/PresetTextField";
import { emptyCloseCaseForm, toCloseCaseRequest } from "./caseForms";

/** Quick-fill note presets for closing a case (PUBLIC setting, JSON array). */
const CLOSE_NOTE_PRESET_KEY = "case.close_note_presets";
const PRESET_KEYS = [CLOSE_NOTE_PRESET_KEY];

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
  const tErrors = useTranslations("errors");
  const tCommon = useTranslations("common");
  const [note, setNote] = useState("");
  const presets = useReasonPresets(PRESET_KEYS);
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
        err instanceof ApiError
          ? resolveApiErrorMessage(err, tErrors, tCommon)
          : t("closeFailed"),
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
      <ModalSection className="space-y-[var(--ecmp-panel-gap)]">
        {submitError ? (
          <Alert tone="danger" title={t("closeFailed")} description={submitError} />
        ) : null}
        <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
          {t("closeChecklist")}
        </p>
        <PresetTextField
          presets={presets[CLOSE_NOTE_PRESET_KEY] ?? []}
          name="note"
          label={t("noteOptional")}
          value={note}
          onChange={setNote}
          hint={t("closeHint")}
        />
      </ModalSection>
    </Modal>
  );
}
