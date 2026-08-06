"use client";

import { useTranslations } from "next-intl";
import { Button, Modal } from "@/shared/ui";

export interface StartHandlingDialogProps {
  open: boolean;
  reference: string;
  confirming?: boolean;
  onConfirm: () => void;
  onClose: () => void;
}

/** Confirm Start handling (ASSIGNED → IN_PROGRESS). */
export function StartHandlingDialog({
  open,
  reference,
  confirming,
  onConfirm,
  onClose,
}: StartHandlingDialogProps) {
  const t = useTranslations("officerHandle");

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={t("startConfirmTitle")}
      size="sm"
      footer={
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
            {t("startConfirm")}
          </Button>
        </div>
      }
    >
      <p className="text-ecmp-text-primary">
        {t("startConfirmBody", { reference })}
      </p>
    </Modal>
  );
}
