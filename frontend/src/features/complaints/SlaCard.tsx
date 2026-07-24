"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/auth/AuthProvider";
import { ApiError, fetchComplaintSla } from "@/lib/api";
import type { SlaRecord, SlaStatus } from "@/lib/api/types";
import {
  Alert,
  Badge,
  Card,
  CardBody,
  CardHeader,
  CardTitle,
} from "@/shared/ui";
import type { BadgeTone } from "@/shared/ui";

function formatWhen(value: string | null | undefined): string {
  if (!value) return "—";
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

function statusTone(status: SlaStatus | undefined): BadgeTone {
  if (status === "COMPLETED") return "success";
  if (status === "BREACHED") return "danger";
  return "neutral";
}

function StatusBadge({ status }: { status: SlaStatus | undefined }) {
  const value = status ?? "PENDING";
  return <Badge tone={statusTone(status)}>{value}</Badge>;
}

function DetailField({
  label,
  value,
}: {
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div className="min-w-0 space-y-1">
      <dt className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary">
        {label}
      </dt>
      <dd className="whitespace-pre-wrap break-words text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
        {value}
      </dd>
    </div>
  );
}

export function SlaCard({
  complaintId,
  refreshKey = 0,
}: {
  complaintId: string;
  refreshKey?: number;
}) {
  const { hasPermission } = useAuth();
  const canRead = hasPermission("complaints:read");

  const [sla, setSla] = useState<SlaRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!canRead) {
      setLoading(false);
      setSla(null);
      setLoadError(null);
      return;
    }
    setLoading(true);
    setLoadError(null);
    try {
      const res = await fetchComplaintSla(complaintId);
      setSla(res.data);
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setSla(null);
      } else {
        setSla(null);
        setLoadError(
          err instanceof ApiError
            ? err.message
            : "Unable to load SLA.",
        );
      }
    } finally {
      setLoading(false);
    }
  }, [canRead, complaintId]);

  useEffect(() => {
    void load();
  }, [load, refreshKey]);

  if (!canRead) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>SLA</CardTitle>
      </CardHeader>
      <CardBody className="space-y-4">
        {loading ? (
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
            Loading SLA…
          </p>
        ) : loadError ? (
          <Alert
            tone="danger"
            title="Could not load SLA"
            description={loadError}
            actionLabel="Retry"
            onAction={() => void load()}
          />
        ) : !sla ? (
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
            No SLA record for this complaint.
          </p>
        ) : (
          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <DetailField
              label="Assignment Due"
              value={formatWhen(sla.assignmentDueAt)}
            />
            <DetailField
              label="Assignment Status"
              value={<StatusBadge status={sla.assignmentStatus} />}
            />
            <DetailField
              label="Appointment Due"
              value={formatWhen(sla.appointmentDueAt)}
            />
            <DetailField
              label="Appointment Status"
              value={<StatusBadge status={sla.appointmentStatus} />}
            />
            <DetailField
              label="Resolution Due"
              value={formatWhen(sla.resolutionDueAt)}
            />
            <DetailField
              label="Resolution Status"
              value={<StatusBadge status={sla.resolutionStatus} />}
            />
            <DetailField
              label="Escalation Due"
              value={formatWhen(sla.escalationDueAt)}
            />
            <DetailField
              label="Escalation Status"
              value={<StatusBadge status={sla.escalationStatus} />}
            />
            <DetailField
              label="Overall Due"
              value={formatWhen(sla.overallDueAt)}
            />
            <DetailField
              label="Overall Status"
              value={<StatusBadge status={sla.overallStatus} />}
            />
          </dl>
        )}
      </CardBody>
    </Card>
  );
}
