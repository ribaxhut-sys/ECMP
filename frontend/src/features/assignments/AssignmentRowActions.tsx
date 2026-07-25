"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  assignComplaintHandler,
  cancelAssignment,
  fetchUsers,
  reassignComplaintHandler,
  type UserRef,
} from "@/lib/api";
import type { ComplaintStatus } from "@/lib/api/types";
import {
  Alert,
  Button,
  Modal,
  Select,
  Textarea,
  Toast,
} from "@/shared/ui";

export type AssignmentRowMeta = {
  id: string;
  complaintNumber: string;
  subject: string;
  status: ComplaintStatus;
  currentAssigneeId: string | null;
  currentAssigneeName: string | null;
};

type ActionKind = "assign" | "reassign" | "cancel" | null;

function roleLabel(user: UserRef): string {
  return user.roleName?.trim() || user.roleCode?.trim() || "—";
}

function userOptionLabel(user: UserRef): string {
  return `${user.fullName} — ${roleLabel(user)}`;
}

export function AssignmentRowActions({
  row,
  onChanged,
}: {
  row: AssignmentRowMeta;
  onChanged?: () => void;
}) {
  const { hasPermission, userId } = useAuth();
  const canAssign = hasPermission("complaints:assign");

  const canDoAssign = canAssign && !row.currentAssigneeId;
  const canReassign = canAssign && Boolean(row.currentAssigneeId);
  const canCancel = canAssign && Boolean(userId) && Boolean(row.currentAssigneeId);

  const [action, setAction] = useState<ActionKind>(null);
  const [users, setUsers] = useState<UserRef[]>([]);
  const [usersError, setUsersError] = useState<string | null>(null);
  const [usersLoading, setUsersLoading] = useState(false);
  const [selectedId, setSelectedId] = useState("");
  const [reason, setReason] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toastOpen, setToastOpen] = useState(false);
  const [toastTitle, setToastTitle] = useState("");

  const loadUsers = useCallback(async () => {
    setUsersLoading(true);
    setUsersError(null);
    try {
      const res = await fetchUsers({ pageSize: 100, isActive: true });
      setUsers(res.data.filter((u) => u.isActive));
    } catch (err) {
      setUsers([]);
      setUsersError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Unable to load users.",
      );
    } finally {
      setUsersLoading(false);
    }
  }, []);

  useEffect(() => {
    if (action === "assign" || action === "reassign") {
      void loadUsers();
    }
  }, [action, loadUsers]);

  if (!canDoAssign && !canReassign && !canCancel) {
    return null;
  }

  function openAction(next: ActionKind) {
    setError(null);
    setSelectedId("");
    setReason("");
    setAction(next);
  }

  function closeAction() {
    if (submitting) return;
    setAction(null);
    setError(null);
  }

  async function confirmAction() {
    setSubmitting(true);
    setError(null);
    try {
      if (action === "assign") {
        if (!selectedId) {
          setError("Select an assignee.");
          setSubmitting(false);
          return;
        }
        await assignComplaintHandler(row.id, { assigneeId: selectedId });
        setToastTitle("Complaint assigned");
      } else if (action === "reassign") {
        if (!selectedId) {
          setError("Select an assignee.");
          setSubmitting(false);
          return;
        }
        const trimmedReason = reason.trim();
        if (!trimmedReason) {
          setError("Reason is required for reassignment.");
          setSubmitting(false);
          return;
        }
        await reassignComplaintHandler(row.id, {
          assigneeId: selectedId,
          reason: trimmedReason,
        });
        setToastTitle("Complaint reassigned");
      } else if (action === "cancel") {
        if (!userId) {
          setError("You must be signed in to cancel an assignment.");
          setSubmitting(false);
          return;
        }
        await cancelAssignment(row.id, {
          releasedBy: userId,
          reason: reason.trim() || null,
        });
        setToastTitle("Assignment cancelled");
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

  const options = useMemo(
    () =>
      users
        .filter((u) => u.id !== row.currentAssigneeId)
        .map((user) => ({
          value: user.id,
          label: userOptionLabel(user),
        })),
    [row.currentAssigneeId, users],
  );

  const modalTitle =
    action === "assign"
      ? "Assign complaint?"
      : action === "reassign"
        ? "Reassign complaint?"
        : action === "cancel"
          ? "Cancel assignment?"
          : "";

  return (
    <>
      <div className="flex flex-wrap gap-2">
        {canDoAssign ? (
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={() => openAction("assign")}
          >
            Assign
          </Button>
        ) : null}
        {canReassign ? (
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={() => openAction("reassign")}
          >
            Reassign
          </Button>
        ) : null}
        {canCancel ? (
          <Button
            type="button"
            size="sm"
            variant="ghost"
            onClick={() => openAction("cancel")}
          >
            Cancel
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
              disabled={submitting}
              onClick={() => void confirmAction()}
            >
              {submitting ? "Working…" : "Confirm"}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
            {action === "assign"
              ? `Assign ${row.complaintNumber} to a handler.`
              : action === "reassign"
                ? `Reassign ${row.complaintNumber}. A reason is required.`
                : `Release the active assignee from ${row.complaintNumber}.`}
          </p>

          {action === "assign" || action === "reassign" ? (
            <>
              {usersError ? (
                <Alert
                  tone="danger"
                  title="Could not load users"
                  description={usersError}
                  actionLabel="Retry"
                  onAction={() => void loadUsers()}
                />
              ) : null}
              <Select
                label="Assignee"
                name="assigneeId"
                required
                placeholder={usersLoading ? "Loading users…" : "Select user"}
                value={selectedId}
                options={options}
                disabled={submitting || usersLoading || options.length === 0}
                onChange={(e) => setSelectedId(e.target.value)}
                error={
                  !usersError && !usersLoading && options.length === 0
                    ? "No active users available."
                    : undefined
                }
              />
            </>
          ) : null}

          {action === "reassign" || action === "cancel" ? (
            <div className="space-y-1">
              <label
                htmlFor={`assignment-reason-${row.id}`}
                className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary"
              >
                {action === "reassign" ? "Reason (required)" : "Reason (optional)"}
              </label>
              <Textarea
                id={`assignment-reason-${row.id}`}
                name="reason"
                rows={3}
                maxLength={2000}
                value={reason}
                disabled={submitting}
                onChange={(e) => setReason(e.target.value)}
              />
            </div>
          ) : null}

          {error ? (
            <Alert tone="danger" title="Action failed" description={error} />
          ) : null}
        </div>
      </Modal>

      <Toast
        open={toastOpen}
        title={toastTitle}
        description="Assignment list refreshed."
        onClose={() => setToastOpen(false)}
      />
    </>
  );
}
