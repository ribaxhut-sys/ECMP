"use client";

import { useCallback, useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { ApiError, fetchComplaintSla } from "@/lib/api";
import type { SlaRecord, SlaStatus } from "@/lib/api/types";
import { formatDateTime } from "@/i18n/formatting";
import {
  Alert,
  Badge,
  Card,
  CardBody,
  CardHeader,
  CardTitle,
} from "@/shared/ui";
import type { BadgeTone } from "@/shared/ui";

function statusTone(status: SlaStatus | undefined): BadgeTone {
  if (status === "COMPLETED") return "success";
  if (status === "BREACHED") return "danger";
  return "neutral";
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
      <dt className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
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
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  const tStatus = useTranslations("status");
  const locale = useLocale();
  const canRead = hasPermission("complaints:read");

  function StatusBadge({ status }: { status: SlaStatus | undefined }) {
    const value = status ?? "PENDING";
    return <Badge tone={statusTone(status)}>{tStatus(value)}</Badge>;
  }

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
          err instanceof ApiError ? err.message : t("unableToLoadSla"),
        );
      }
    } finally {
      setLoading(false);
    }
  }, [canRead, complaintId, t]);

  useEffect(() => {
    void load();
  }, [load, refreshKey]);

  if (!canRead) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("slaCard")}</CardTitle>
      </CardHeader>
      <CardBody className="space-y-[var(--ecmp-panel-gap)]">
        {loading ? (
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
            {t("loadingSla")}
          </p>
        ) : loadError ? (
          <Alert
            tone="danger"
            title={t("couldNotLoadSla")}
            description={loadError}
            actionLabel={tCommon("retry")}
            onAction={() => void load()}
          />
        ) : !sla ? (
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
            {t("noSlaRecord")}
          </p>
        ) : (
          <dl className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] sm:grid-cols-2">
            <DetailField
              label={t("assignmentDue")}
              value={formatDateTime(sla.assignmentDueAt, locale)}
            />
            <DetailField
              label={t("assignmentStatus")}
              value={<StatusBadge status={sla.assignmentStatus} />}
            />
            <DetailField
              label={t("appointmentDue")}
              value={formatDateTime(sla.appointmentDueAt, locale)}
            />
            <DetailField
              label={t("appointmentStatus")}
              value={<StatusBadge status={sla.appointmentStatus} />}
            />
            <DetailField
              label={t("resolutionDue")}
              value={formatDateTime(sla.resolutionDueAt, locale)}
            />
            <DetailField
              label={t("resolutionStatus")}
              value={<StatusBadge status={sla.resolutionStatus} />}
            />
            <DetailField
              label={t("escalationDue")}
              value={formatDateTime(sla.escalationDueAt, locale)}
            />
            <DetailField
              label={t("escalationStatus")}
              value={<StatusBadge status={sla.escalationStatus} />}
            />
            <DetailField
              label={t("overallDue")}
              value={formatDateTime(sla.overallDueAt, locale)}
            />
            <DetailField
              label={t("overallStatus")}
              value={<StatusBadge status={sla.overallStatus} />}
            />
          </dl>
        )}
      </CardBody>
    </Card>
  );
}
