"use client";

import { useCallback, useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  closeEscalation,
  fetchComplaintEscalations,
} from "@/lib/api";
import type { ComplaintStatus, Escalation } from "@/lib/api/types";
import { formatDateTime } from "@/i18n/formatting";
import {
  Alert,
  Button,
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  Modal,
  Textarea,
} from "@/shared/ui";
import { useToast } from "@/shared/providers";

function DetailField({ label, value }: { label: string; value: string }) {
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

function pickEscalation(rows: Escalation[]): Escalation | null {
  if (rows.length === 0) return null;
  return (
    rows.find((row) => row.status === "CLOSED") ??
    rows.find((row) => row.status === "APPROVED") ??
    rows.find((row) => row.status === "REQUESTED") ??
    rows[0] ??
    null
  );
}

export function CloseEscalationCard({
  complaintId,
  complaintStatus,
  refreshKey = 0,
  onClosed,
}: {
  complaintId: string;
  complaintStatus: ComplaintStatus;
  refreshKey?: number;
  onClosed?: () => void;
}) {
  const { hasPermission } = useAuth();
  const { pushSuccess } = useToast();
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  const tStatus = useTranslations("status");
  const locale = useLocale();
  const canClose = hasPermission("escalations:close");
  const canRead = hasPermission("escalations:read");

  const [escalation, setEscalation] = useState<Escalation | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [dialogOpen, setDialogOpen] = useState(false);
  const [notes, setNotes] = useState("");
  const [notesError, setNotesError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const { data } = await fetchComplaintEscalations(complaintId);
      setEscalation(pickEscalation(data));
    } catch (err) {
      setEscalation(null);
      setLoadError(
        err instanceof ApiError ? err.message : t("unableToLoadEscalation"),
      );
    } finally {
      setLoading(false);
    }
  }, [complaintId, t]);

  useEffect(() => {
    void load();
  }, [load, refreshKey]);

  const isClosed =
    escalation?.status === "CLOSED" || Boolean(escalation?.closedAt);
  const complaintClosed = complaintStatus === "CLOSED";
  const canAttemptClose =
    canClose && Boolean(escalation) && !isClosed && complaintClosed;

  function openDialog() {
    setNotes("");
    setNotesError(null);
    setSubmitError(null);
    setDialogOpen(true);
  }

  function closeDialog() {
    if (submitting) return;
    setDialogOpen(false);
  }

  async function confirmClose() {
    if (!canAttemptClose || !escalation) return;
    const trimmed = notes.trim();
    if (!trimmed) {
      setNotesError(t("closureNotesRequired"));
      return;
    }
    setNotesError(null);
    setSubmitting(true);
    setSubmitError(null);
    try {
      await closeEscalation(escalation.id, { notes: trimmed });
      setDialogOpen(false);
      pushSuccess(t("escalationClosed"), t("escalationClosedHint"));
      onClosed?.();
      await load();
    } catch (err) {
      setSubmitError(
        err instanceof ApiError ? err.message : t("unableToCloseEscalation"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  if (!canRead) {
    return null;
  }

  if (!loading && !loadError && !escalation) {
    return null;
  }

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>{t("closeEscalationCard")}</CardTitle>
        </CardHeader>
        <CardBody className="space-y-[var(--ecmp-panel-gap)]">
          {loading ? (
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              {t("loadingEscalation")}
            </p>
          ) : loadError ? (
            <Alert
              tone="danger"
              title={t("couldNotLoadEscalation")}
              description={loadError}
              actionLabel={tCommon("retry")}
              onAction={() => void load()}
            />
          ) : isClosed && escalation ? (
            <dl className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] sm:grid-cols-2">
              <DetailField label={t("status")} value={tStatus("CLOSED")} />
              <DetailField
                label={t("closedAt")}
                value={formatDateTime(escalation.closedAt, locale)}
              />
              <DetailField
                label={t("closureNotes")}
                value={escalation.closureNotes?.trim() || tCommon("emDash")}
              />
              <DetailField
                label={t("closedBy")}
                value={escalation.closedBy?.trim() || tCommon("emDash")}
              />
            </dl>
          ) : canAttemptClose ? (
            <>
              <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                {t("closeEscalationHint")}
              </p>
              <div className="flex justify-end">
                <Button type="button" onClick={openDialog}>
                  {t("closeEscalationCard")}
                </Button>
              </div>
            </>
          ) : (
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              {!complaintClosed
                ? t("closeComplaintFirstHint")
                : t("notClosedEscalationPermissionHint")}
            </p>
          )}
        </CardBody>
      </Card>

      <Modal
        open={dialogOpen}
        onClose={closeDialog}
        title={t("closeEscalationConfirm")}
        size="sm"
        footer={
          <>
            <Button
              type="button"
              variant="outline"
              disabled={submitting}
              onClick={closeDialog}
            >
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              variant="primary"
              disabled={submitting}
              onClick={() => void confirmClose()}
            >
              {submitting ? t("closing") : t("confirmClose")}
            </Button>
          </>
        }
      >
        <div className="space-y-[var(--ecmp-panel-gap)]">
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
            {t("confirmEscalationClosureHint")}
          </p>
          {submitError ? (
            <Alert tone="danger" title={t("closeFailed")}>
              {submitError}
            </Alert>
          ) : null}
          <div className="space-y-1">
            <label
              htmlFor="escalation-closure-notes"
              className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary"
            >
              {t("closureNotes")}
            </label>
            <Textarea
              id="escalation-closure-notes"
              name="notes"
              rows={4}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              aria-invalid={Boolean(notesError)}
            />
            {notesError ? (
              <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-danger">
                {notesError}
              </p>
            ) : null}
          </div>
        </div>
      </Modal>
    </>
  );
}
