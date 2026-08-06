"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { ApiError, changeComplaintStatus } from "@/lib/api";
import type { ComplaintStatus } from "@/lib/api/types";
import {
  Alert,
  Button,
  Card,
  CardBody,
  CardHeader,
  CardTitle,
} from "@/shared/ui";
import { statusActionsFor } from "./statusTransitions";

export function StatusActionsCard({
  complaintId,
  status,
  onStatusChanged,
}: {
  complaintId: string;
  status: ComplaintStatus;
  onStatusChanged?: (next: ComplaintStatus) => void;
}) {
  const { hasPermission } = useAuth();
  const t = useTranslations("complaints");
  const tStatus = useTranslations("status");
  const canUpdate = hasPermission("complaints:update");
  const actions = statusActionsFor(status);

  const [submitting, setSubmitting] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!canUpdate) {
    return null;
  }

  if (status === "NEW") {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{t("statusCard")}</CardTitle>
        </CardHeader>
        <CardBody>
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
            {t("assignToStartLifecycle")}
          </p>
        </CardBody>
      </Card>
    );
  }

  if (actions.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{t("statusCard")}</CardTitle>
        </CardHeader>
        <CardBody>
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
            {status === "CLOSED"
              ? t("noFurtherStatusActions")
              : t("noStatusActionsAvailable")}
          </p>
        </CardBody>
      </Card>
    );
  }

  async function runTransition(target: ComplaintStatus, labelKey: string) {
    setError(null);
    setSubmitting(labelKey);
    try {
      const res = await changeComplaintStatus(complaintId, { status: target });
      onStatusChanged?.(res.data.status);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : t("statusChangeFailed"),
      );
    } finally {
      setSubmitting(null);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("statusCard")}</CardTitle>
      </CardHeader>
      <CardBody className="space-y-[var(--ecmp-panel-gap)]">
        <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
          {t("availableActionsFor")}{" "}
          <span className="font-medium text-ecmp-text-primary">
            {tStatus(status)}
          </span>
        </p>
        {error ? (
          <Alert tone="danger" title={t("statusChangeFailed")} description={error} />
        ) : null}
        <div className="flex flex-wrap gap-2">
          {actions.map((action) => (
            <Button
              key={action.target}
              type="button"
              variant={action.target === "CLOSED" ? "primary" : "outline"}
              disabled={submitting !== null}
              onClick={() => void runTransition(action.target, action.labelKey)}
            >
              {submitting === action.labelKey ? t("updating") : t(action.labelKey)}
            </Button>
          ))}
        </div>
      </CardBody>
    </Card>
  );
}
