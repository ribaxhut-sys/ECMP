"use client";

import { useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { ApiError, closeComplaint } from "@/lib/api";
import type { Complaint } from "@/lib/api/types";
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
  Toast,
} from "@/shared/ui";

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

export function CloseComplaintCard({
  complaint,
  onClosed,
}: {
  complaint: Complaint;
  onClosed?: () => void;
}) {
  const { hasPermission } = useAuth();
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  const tStatus = useTranslations("status");
  const locale = useLocale();
  const canClose = hasPermission("complaints:close");
  const canRead = hasPermission("complaints:read");

  const isClosed = complaint.status === "CLOSED" || Boolean(complaint.closedAt);

  const [dialogOpen, setDialogOpen] = useState(false);
  const [notes, setNotes] = useState("");
  const [notesError, setNotesError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [toastOpen, setToastOpen] = useState(false);

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
    if (!canClose || isClosed) return;
    const trimmed = notes.trim();
    if (!trimmed) {
      setNotesError(t("closureNotesRequired"));
      return;
    }
    setNotesError(null);
    setSubmitting(true);
    setSubmitError(null);
    try {
      await closeComplaint(complaint.id, { notes: trimmed });
      setDialogOpen(false);
      setToastOpen(true);
      onClosed?.();
    } catch (err) {
      setSubmitError(
        err instanceof ApiError ? err.message : t("unableToCloseComplaint"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  if (!canRead) {
    return null;
  }

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>{t("closeCard")}</CardTitle>
        </CardHeader>
        <CardBody className="space-y-[var(--ecmp-panel-gap)]">
          {isClosed ? (
            <dl className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] sm:grid-cols-2">
              <DetailField label={t("status")} value={tStatus("CLOSED")} />
              <DetailField
                label={t("closedAt")}
                value={formatDateTime(complaint.closedAt, locale)}
              />
              <DetailField
                label={t("closureNotes")}
                value={complaint.closureNotes?.trim() || tCommon("emDash")}
              />
              <DetailField
                label={t("closedBy")}
                value={complaint.closedBy?.trim() || tCommon("emDash")}
              />
            </dl>
          ) : canClose ? (
            <>
              <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                {t("closeComplaintHint")}
              </p>
              <div className="flex justify-end">
                <Button type="button" onClick={openDialog}>
                  {t("closeCard")}
                </Button>
              </div>
            </>
          ) : (
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              {t("notClosedPermissionHint")}
            </p>
          )}
        </CardBody>
      </Card>

      <Modal
        open={dialogOpen}
        onClose={closeDialog}
        title={t("closeComplaintConfirm")}
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
            {t("confirmClosureHint")}
          </p>
          {submitError ? (
            <Alert tone="danger" title={t("closeFailed")}>
              {submitError}
            </Alert>
          ) : null}
          <div className="space-y-1">
            <label
              htmlFor="closure-notes"
              className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary"
            >
              {t("closureNotes")}
            </label>
            <Textarea
              id="closure-notes"
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

      <Toast
        open={toastOpen}
        onClose={() => setToastOpen(false)}
        tone="success"
        title={t("complaintClosed")}
        description={t("complaintClosedHint")}
      />
    </>
  );
}
