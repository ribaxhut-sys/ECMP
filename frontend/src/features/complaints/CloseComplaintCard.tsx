"use client";

import { useState } from "react";
import { useAuth } from "@/auth/AuthProvider";
import { ApiError, closeComplaint } from "@/lib/api";
import type { Complaint } from "@/lib/api/types";
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

export function CloseComplaintCard({
  complaint,
  onClosed,
}: {
  complaint: Complaint;
  onClosed?: () => void;
}) {
  const { hasPermission } = useAuth();
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
      setNotesError("Closure notes are required.");
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
        err instanceof ApiError
          ? err.message
          : "Unable to close complaint.",
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
          <CardTitle>Close Complaint</CardTitle>
        </CardHeader>
        <CardBody className="space-y-4">
          {isClosed ? (
            <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <DetailField label="Status" value="CLOSED" />
              <DetailField
                label="Closed at"
                value={formatWhen(complaint.closedAt)}
              />
              <DetailField
                label="Closure notes"
                value={complaint.closureNotes?.trim() || "—"}
              />
              <DetailField
                label="Closed by"
                value={complaint.closedBy?.trim() || "—"}
              />
            </dl>
          ) : canClose ? (
            <>
              <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
                Officially close this complaint after Final Resolution.
                Escalation remains open; this does not auto-close escalation.
              </p>
              <div className="flex justify-end">
                <Button type="button" onClick={openDialog}>
                  Close Complaint
                </Button>
              </div>
            </>
          ) : (
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              Complaint is not closed. Only Branch Supervisor or Head Office
              Admin can close.
            </p>
          )}
        </CardBody>
      </Card>

      <Modal
        open={dialogOpen}
        onClose={closeDialog}
        title="Close complaint?"
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
            Confirm official closure. Complaint status becomes CLOSED.
            Escalation is not closed.
          </p>
          {submitError ? (
            <Alert tone="danger" title="Close failed">
              {submitError}
            </Alert>
          ) : null}
          <div className="space-y-1">
            <label
              htmlFor="closure-notes"
              className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary"
            >
              Closure notes
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
        title="Complaint closed"
        description="Status is CLOSED. Escalation was not closed."
      />
    </>
  );
}
