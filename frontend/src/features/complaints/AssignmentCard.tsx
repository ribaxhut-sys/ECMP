"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type FormEvent,
} from "react";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  assignComplaint,
  fetchComplaintAssignments,
  fetchUsers,
  type UserRef,
} from "@/lib/api";
import type { Assignment } from "@/lib/api/types";
import {
  Alert,
  Button,
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  Select,
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

function roleLabel(user: UserRef): string {
  return user.roleName?.trim() || user.roleCode?.trim() || "—";
}

function userOptionLabel(user: UserRef): string {
  return `${user.fullName} — ${roleLabel(user)}`;
}

export function AssignmentCard({
  complaintId,
  onAssigned,
}: {
  complaintId: string;
  onAssigned?: () => void;
}) {
  const { hasPermission } = useAuth();
  const canAssign = hasPermission("complaints:assign");

  const [assignment, setAssignment] = useState<Assignment | null>(null);
  const [users, setUsers] = useState<UserRef[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [loading, setLoading] = useState(true);
  const [usersError, setUsersError] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [toastOpen, setToastOpen] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    setUsersError(null);

    try {
      const assignmentsPromise = fetchComplaintAssignments(complaintId);
      const usersPromise = canAssign
        ? fetchUsers({ pageSize: 100, isActive: true }).catch((err) => {
            setUsersError(
              err instanceof ApiError
                ? err.message
                : "Unable to load users.",
            );
            return null;
          })
        : Promise.resolve(null);

      const [assignmentsRes, usersRes] = await Promise.all([
        assignmentsPromise,
        usersPromise,
      ]);

      const current =
        assignmentsRes.data.find((row) => row.isCurrent) ?? null;
      setAssignment(current);

      const activeUsers = (usersRes?.data ?? []).filter((u) => u.isActive);
      setUsers(activeUsers);
      if (!current) setSelectedId("");
    } catch (err) {
      setLoadError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Unable to load assignment.",
      );
      setAssignment(null);
    } finally {
      setLoading(false);
    }
  }, [canAssign, complaintId]);

  useEffect(() => {
    void load();
  }, [load]);

  const options = useMemo(
    () =>
      users.map((user) => ({
        value: user.id,
        label: userOptionLabel(user),
      })),
    [users],
  );

  async function handleAssign(event: FormEvent) {
    event.preventDefault();
    setSubmitError(null);

    if (!selectedId) {
      setSubmitError("Select an assignee.");
      return;
    }

    setSubmitting(true);
    try {
      await assignComplaint(complaintId, { assigneeId: selectedId });
      setToastOpen(true);
      await load();
      onAssigned?.();
    } catch (err) {
      setSubmitError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Assign failed.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  const showForm = canAssign && !assignment;
  const assigneeDisplay =
    assignment?.assigneeName?.trim() ||
    users.find((u) => u.id === assignment?.assigneeId)?.fullName ||
    "—";

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>Assignment</CardTitle>
        </CardHeader>
        <CardBody className="space-y-4">
          {loading ? (
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              Loading assignment…
            </p>
          ) : loadError ? (
            <Alert
              tone="danger"
              title="Could not load assignment"
              description={loadError}
              actionLabel="Retry"
              onAction={() => void load()}
            />
          ) : assignment ? (
            <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="min-w-0 space-y-1">
                <dt className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary">
                  Assignee
                </dt>
                <dd className="break-words text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                  {assigneeDisplay}
                </dd>
              </div>
              <div className="min-w-0 space-y-1">
                <dt className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-wide text-ecmp-text-secondary">
                  Assigned At
                </dt>
                <dd className="break-words text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                  {formatWhen(assignment.assignedAt)}
                </dd>
              </div>
            </dl>
          ) : showForm ? (
            <form className="space-y-4" onSubmit={(e) => void handleAssign(e)}>
              {usersError ? (
                <Alert
                  tone="danger"
                  title="Could not load users"
                  description={usersError}
                />
              ) : null}
              <Select
                label="Assignee"
                name="assigneeId"
                required
                placeholder="Select User"
                value={selectedId}
                options={options}
                disabled={submitting || options.length === 0}
                onChange={(e) => setSelectedId(e.target.value)}
                error={
                  !usersError && options.length === 0
                    ? "No active users available."
                    : undefined
                }
              />
              {submitError ? (
                <Alert
                  tone="danger"
                  title="Assign failed"
                  description={submitError}
                />
              ) : null}
              <div className="flex justify-end">
                <Button
                  type="submit"
                  disabled={submitting || !selectedId || options.length === 0}
                >
                  {submitting ? "Assigning…" : "Assign"}
                </Button>
              </div>
            </form>
          ) : (
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              Unassigned
            </p>
          )}
        </CardBody>
      </Card>

      <Toast
        open={toastOpen}
        title="Complaint assigned"
        description="Assignee saved successfully."
        onClose={() => setToastOpen(false)}
      />
    </>
  );
}
