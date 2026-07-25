"use client";

import { useMemo, useState } from "react";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  releaseQueue,
  takeQueue,
  updateQueueStatus,
} from "@/lib/api";
import type { ComplaintStatus } from "@/lib/api/types";
import {
  Alert,
  Button,
  Modal,
  Select,
  Toast,
} from "@/shared/ui";
import { statusActionsFor } from "@/features/complaints/statusTransitions";

export type QueueRowMeta = {
  id: string;
  complaintNumber: string;
  status: ComplaintStatus;
  assigneeId: string | null;
  assigneeName: string | null;
};

type ActionKind = "take" | "release" | "status" | null;

export function QueueRowActions({
  row,
  onChanged,
}: {
  row: QueueRowMeta;
  onChanged?: () => void;
}) {
  const { hasPermission, userId } = useAuth();
  const canAssign = hasPermission("complaints:assign");
  const canUpdate = hasPermission("complaints:update");
  const statusActions = useMemo(
    () => statusActionsFor(row.status),
    [row.status],
  );

  const canTake = canAssign && Boolean(userId) && !row.assigneeId;
  const canRelease = canAssign && Boolean(userId) && Boolean(row.assigneeId);
  const canChangeStatus = canUpdate && statusActions.length > 0;

  const [action, setAction] = useState<ActionKind>(null);
  const [statusTarget, setStatusTarget] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toastOpen, setToastOpen] = useState(false);
  const [toastTitle, setToastTitle] = useState("");

  if (!canTake && !canRelease && !canChangeStatus) {
    return null;
  }

  function openAction(next: ActionKind) {
    setError(null);
    setStatusTarget(statusActions[0]?.target ?? "");
    setAction(next);
  }

  function closeAction() {
    if (submitting) return;
    setAction(null);
    setError(null);
  }

  async function confirmAction() {
    if (!userId) {
      setError("You must be signed in to perform this action.");
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      if (action === "take") {
        await takeQueue(row.id, { assigneeId: userId });
        setToastTitle("Queue item taken");
      } else if (action === "release") {
        await releaseQueue(row.id, { releasedBy: userId });
        setToastTitle("Queue item released");
      } else if (action === "status") {
        if (!statusTarget) {
          setError("Select a status.");
          setSubmitting(false);
          return;
        }
        await updateQueueStatus(row.id, {
          status: statusTarget as ComplaintStatus,
        });
        setToastTitle("Status updated");
      }
      setAction(null);
      setToastOpen(true);
      onChanged?.();
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Action failed.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  const modalTitle =
    action === "take"
      ? "Take queue item?"
      : action === "release"
        ? "Release queue item?"
        : action === "status"
          ? "Update queue status?"
          : "";

  return (
    <>
      <div className="flex flex-wrap gap-2">
        {canTake ? (
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={() => openAction("take")}
          >
            Take
          </Button>
        ) : null}
        {canRelease ? (
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={() => openAction("release")}
          >
            Release
          </Button>
        ) : null}
        {canChangeStatus ? (
          <Button
            type="button"
            size="sm"
            variant="ghost"
            onClick={() => openAction("status")}
          >
            Status
          </Button>
        ) : null}
      </div>

      <Modal
        open={action !== null}
        onClose={closeAction}
        title={modalTitle}
        size="sm"
        footer={
          <>
            <Button
              type="button"
              variant="outline"
              disabled={submitting}
              onClick={closeAction}
            >
              Cancel
            </Button>
            <Button
              type="button"
              disabled={submitting || (action === "status" && !statusTarget)}
              onClick={() => void confirmAction()}
            >
              {submitting ? "Working…" : "Confirm"}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
            {action === "take"
              ? `Assign ${row.complaintNumber} to you and start handling it.`
              : action === "release"
                ? `Release the active assignee from ${row.complaintNumber}.`
                : `Change status for ${row.complaintNumber}.`}
          </p>
          {action === "status" ? (
            <Select
              label="New status"
              name="status"
              value={statusTarget}
              options={statusActions.map((a) => ({
                value: a.target,
                label: a.label,
              }))}
              onChange={(e) => setStatusTarget(e.target.value)}
              disabled={submitting}
            />
          ) : null}
          {error ? (
            <Alert tone="danger" title="Action failed" description={error} />
          ) : null}
        </div>
      </Modal>

      <Toast
        open={toastOpen}
        title={toastTitle}
        description="Queue refreshed after the action."
        onClose={() => setToastOpen(false)}
      />
    </>
  );
}
