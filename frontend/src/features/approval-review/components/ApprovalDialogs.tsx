"use client";

import { useTranslations } from "next-intl";
import { Button, Modal } from "@/shared/ui";

export interface ApproveConfirmDialogProps {
  open: boolean;
  reference: string;
  confirming?: boolean;
  onConfirm: () => void;
  onClose: () => void;
}

export function ApproveConfirmDialog({
  open,
  reference,
  confirming = false,
  onConfirm,
  onClose,
}: ApproveConfirmDialogProps) {
  const t = useTranslations("approvalReview");

  return (
    <Modal open={open} onClose={onClose} title={t("confirmApproveTitle")} size="sm">
      <div className="space-y-4">
        <p className="text-ecmp-text-primary">
          {t("confirmApproveBody", { reference })}
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
            {t("confirmApprove")}
          </Button>
        </div>
      </div>
    </Modal>
  );
}

export interface RejectConfirmDialogProps {
  open: boolean;
  reference: string;
  reason: string;
  confirming?: boolean;
  onConfirm: () => void;
  onClose: () => void;
}

export function RejectConfirmDialog({
  open,
  reference,
  reason,
  confirming = false,
  onConfirm,
  onClose,
}: RejectConfirmDialogProps) {
  const t = useTranslations("approvalReview");

  return (
    <Modal open={open} onClose={onClose} title={t("confirmRejectTitle")} size="sm">
      <div className="space-y-4">
        <p className="text-ecmp-text-primary">
          {t("confirmRejectBody", { reference })}
        </p>
        <p className="rounded-[var(--ecmp-radius-md)] border border-ecmp-border/70 bg-ecmp-surface-sunken/40 p-3 text-ecmp-text-primary">
          {reason}
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
            variant="danger"
            loading={confirming}
            onClick={onConfirm}
          >
            {t("confirmReject")}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
