"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  closeEscalation,
  fetchComplaintEscalations,
} from "@/lib/api";
import type { ComplaintStatus, Escalation } from "@/lib/api/types";
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

function DetailField({ label, value }: { label: string; value: string }) {
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
  const [toastOpen, setToastOpen] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const { data } = await fetchComplaintEscalations(complaintId);
      setEscalation(pickEscalation(data));
    } catch (err) {
      setEscalation(null);
      setLoadError(
        err instanceof ApiError
          ? err.message
          : "Unable to load escalation.",
      );
    } finally {
      setLoading(false);
    }
  }, [complaintId]);

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
      setNotesError("Closure notes are required.");
      return;
    }
    setNotesError(null);
    setSubmitting(true);
    setSubmitError(null);
    try {
      await closeEscalation(escalation.id, { notes: trimmed });
      setDialogOpen(false);
      setToastOpen(true);
      onClosed?.();
      await load();
    } catch (err) {
      setSubmitError(
        err instanceof ApiError
          ? err.message
          : "Unable to close escalation.",
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
          <CardTitle>Close Escalation</CardTitle>
        </CardHeader>
        <CardBody className="space-y-4">
          {loading ? (
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              Loading escalation…
            </p>
          ) : loadError ? (
            <Alert
              tone="danger"
              title="Could not load escalation"
              description={loadError}
              actionLabel="Retry"
              onAction={() => void load()}
            />
          ) : isClosed && escalation ? (
            <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <DetailField label="Status" value="CLOSED" />
              <DetailField
                label="Closed at"
                value={formatWhen(escalation.closedAt)}
              />
              <DetailField
                label="Closure notes"
                value={escalation.closureNotes?.trim() || "—"}
              />
              <DetailField
                label="Closed by"
                value={escalation.closedBy?.trim() || "—"}
              />
            </dl>
          ) : canAttemptClose ? (
            <>
              <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                Officially close this escalation after Complaint Closure.
                Complaint remains CLOSED.
              </p>
              <div className="flex justify-end">
                <Button type="button" onClick={openDialog}>
                  Close Escalation
                </Button>
              </div>
            </>
          ) : (
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              {!complaintClosed
                ? "Close the complaint first. Escalation closure requires a CLOSED complaint."
                : "Escalation is not closed. Only Head Office Admin can close."}
            </p>
          )}
        </CardBody>
      </Card>

      <Modal
        open={dialogOpen}
        onClose={closeDialog}
        title="Close escalation?"
        size="sm"
        footer={
          <>
            <Button
              type="button"
              variant="outline"
              disabled={submitting}
              onClick={closeDialog}
            >
              Cancel
            </Button>
            <Button
              type="button"
              variant="primary"
              disabled={submitting}
              onClick={() => void confirmClose()}
            >
              {submitting ? "Closing…" : "Confirm Close"}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
            Confirm official closure. Escalation status becomes CLOSED.
            Complaint remains CLOSED.
          </p>
          {submitError ? (
            <Alert tone="danger" title="Close failed">
              {submitError}
            </Alert>
          ) : null}
          <div className="space-y-1">
            <label
              htmlFor="escalation-closure-notes"
              className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary"
            >
              Closure notes
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

      <Toast
        open={toastOpen}
        onClose={() => setToastOpen(false)}
        tone="success"
        title="Escalation closed"
        description="Status is CLOSED. Complaint remains CLOSED."
      />
    </>
  );
}
