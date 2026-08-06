"use client";

import { useTranslations } from "next-intl";
import { Button } from "@/shared/ui";

export interface AssignmentConfirmationProps {
  reference: string;
  unitName: string;
  onConfirm: () => void;
  onCancel: () => void;
  confirming?: boolean;
}

/** Confirm assign body + actions (used inside AssignmentDialog). */
export function AssignmentConfirmation({
  reference,
  unitName,
  onConfirm,
  onCancel,
  confirming = false,
}: AssignmentConfirmationProps) {
  const t = useTranslations("supervisorAssign");

  return (
    <div className="space-y-4">
      <p className="text-ecmp-text-primary">
        {t("confirmAssignBody", { reference, unit: unitName })}
      </p>
      <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <Button
          type="button"
          variant="secondary"
          onClick={onCancel}
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
          {t("confirmAssign")}
        </Button>
      </div>
    </div>
  );
}
