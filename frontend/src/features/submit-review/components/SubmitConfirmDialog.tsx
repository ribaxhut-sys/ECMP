"use client";

import { useTranslations } from "next-intl";
import { Button, Modal } from "@/shared/ui";

export interface SubmitConfirmDialogProps {
  open: boolean;
  reference: string;
  confirming?: boolean;
  onConfirm: () => void;
  onClose: () => void;
}

/** Confirm submit overlay (SCR-WS-05). */
export function SubmitConfirmDialog({
  open,
  reference,
  confirming = false,
  onConfirm,
  onClose,
}: SubmitConfirmDialogProps) {
  const t = useTranslations("submitReview");

  return (
    <Modal open={open} onClose={onClose} title={t("confirmTitle")} size="sm">
      <div className="space-y-4">
        <p className="text-ecmp-text-primary">
          {t("confirmBody", { reference })}
        </p>
        <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <Button
            type="button"
            variant="secondary"
            onClick={onClose}
            disabled={confirming}
          >
            {t("cancel")}
          </Button>
          <Button
            type="button"
            variant="primary"
            loading={confirming}
            onClick={onConfirm}
          >
            {t("confirmSubmit")}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
