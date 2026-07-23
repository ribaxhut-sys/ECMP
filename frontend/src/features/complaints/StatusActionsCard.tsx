"use client";

import { useState } from "react";
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
          <CardTitle>Status</CardTitle>
        </CardHeader>
        <CardBody>
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
            Assign this complaint to start the lifecycle. Status changes after
            assignment use the actions below.
          </p>
        </CardBody>
      </Card>
    );
  }

  if (actions.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Status</CardTitle>
        </CardHeader>
        <CardBody>
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
            {status === "CLOSED"
              ? "No further status actions. This complaint is closed."
              : "No status actions available."}
          </p>
        </CardBody>
      </Card>
    );
  }

  async function runTransition(target: ComplaintStatus, label: string) {
    setError(null);
    setSubmitting(label);
    try {
      const res = await changeComplaintStatus(complaintId, { status: target });
      onStatusChanged?.(res.data.status);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Status change failed.",
      );
    } finally {
      setSubmitting(null);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Status</CardTitle>
      </CardHeader>
      <CardBody className="space-y-4">
        <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
          Available actions for{" "}
          <span className="font-medium text-ecmp-text-primary">
            {status.replaceAll("_", " ")}
          </span>
        </p>
        {error ? (
          <Alert tone="danger" title="Status change failed" description={error} />
        ) : null}
        <div className="flex flex-wrap gap-2">
          {actions.map((action) => (
            <Button
              key={action.target}
              type="button"
              variant={
                action.target === "RESOLVED" || action.target === "CLOSED"
                  ? "primary"
                  : "outline"
              }
              disabled={submitting !== null}
              onClick={() => void runTransition(action.target, action.label)}
            >
              {submitting === action.label ? "Updating…" : action.label}
            </Button>
          ))}
        </div>
      </CardBody>
    </Card>
  );
}
