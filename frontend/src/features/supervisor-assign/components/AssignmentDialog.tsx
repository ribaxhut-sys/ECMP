"use client";

import { useTranslations } from "next-intl";
import { Modal } from "@/shared/ui";
import { AssignmentConfirmation } from "./AssignmentConfirmation";

export interface AssignmentDialogProps {
  open: boolean;
  reference: string;
  unitName: string;
  confirming?: boolean;
  onConfirm: () => void;
  onClose: () => void;
}

/** Confirm-assign overlay for SCR-WS-09. */
export function AssignmentDialog({
  open,
  reference,
  unitName,
  confirming,
  onConfirm,
  onClose,
}: AssignmentDialogProps) {
  const t = useTranslations("supervisorAssign");

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={t("confirmAssignTitle")}
      size="sm"
    >
      <AssignmentConfirmation
        reference={reference}
        unitName={unitName}
        confirming={confirming}
        onConfirm={onConfirm}
        onCancel={onClose}
      />
    </Modal>
  );
}
