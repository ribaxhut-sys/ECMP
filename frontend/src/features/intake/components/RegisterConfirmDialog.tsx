"use client";

import { useTranslations } from "next-intl";
import { Button, Modal } from "@/shared/ui";

export interface RegisterConfirmDialogProps {
  open: boolean;
  customerName: string;
  subject: string;
  confirming?: boolean;
  onConfirm: () => void;
  onClose: () => void;
}

/** Confirm Forward / Register when complete (SCR-WS-01). */
export function RegisterConfirmDialog({
  open,
  customerName,
  subject,
  confirming = false,
  onConfirm,
  onClose,
}: RegisterConfirmDialogProps) {
  const t = useTranslations("intake");

  return (
    <Modal open={open} onClose={onClose} title={t("confirmRegisterTitle")} size="sm">
      <div className="space-y-4">
        <p className="text-ecmp-text-primary">
          {t("confirmRegisterBody", { customer: customerName, subject })}
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
            {t("confirmRegister")}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
