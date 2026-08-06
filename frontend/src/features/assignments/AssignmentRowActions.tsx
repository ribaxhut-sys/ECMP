"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useTranslations } from "next-intl";
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
} from "@/shared/ui";
import { useToast } from "@/shared/providers";

export type AssignmentRowMeta = {
  id: string;
  complaintNumber: string;
  subject: string;
  status: ComplaintStatus;
  currentAssigneeId: string | null;
  currentAssigneeName: string | null;
};

type ActionKind = "assign" | "reassign" | "cancel" | null;

export function AssignmentRowActions({
  row,
  onChanged,
}: {
  row: AssignmentRowMeta;
  onChanged?: () => void;
}) {
  const { hasPermission, userId } = useAuth();
  const { pushSuccess } = useToast();
  const t = useTranslations("assignments");
  const tCommon = useTranslations("common");
  const tComplaints = useTranslations("complaints");
  const canAssign = hasPermission("complaints:assign");

  function roleLabel(user: UserRef): string {
    return user.roleName?.trim() || user.roleCode?.trim() || tCommon("emDash");
  }

  function userOptionLabel(user: UserRef): string {
    return `${user.fullName} — ${roleLabel(user)}`;
  }

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
            : tComplaints("unableToLoadUsers"),
      );
    } finally {
      setUsersLoading(false);
    }
  }, [tComplaints]);

  useEffect(() => {
    if (action === "assign" || action === "reassign") {
      void loadUsers();
    }
  }, [action, loadUsers]);

  const options = useMemo(
    () =>
      users
        .filter((u) => u.id !== row.currentAssigneeId)
        .map((user) => ({
          value: user.id,
          label: userOptionLabel(user),
        })),
    // userOptionLabel is stable per render via local helpers + tCommon
    // eslint-disable-next-line react-hooks/exhaustive-deps -- labels use tCommon only
    [row.currentAssigneeId, users, tCommon],
  );

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
      let successTitle = "";
      if (action === "assign") {
        if (!selectedId) {
          setError(tComplaints("selectAssignee"));
          setSubmitting(false);
          return;
        }
        await assignComplaintHandler(row.id, { assigneeId: selectedId });
        successTitle = tComplaints("complaintAssigned");
      } else if (action === "reassign") {
        if (!selectedId) {
          setError(tComplaints("selectAssignee"));
          setSubmitting(false);
          return;
        }
        const trimmedReason = reason.trim();
        if (!trimmedReason) {
          setError(t("reasonRequiredForReassign"));
          setSubmitting(false);
          return;
        }
        await reassignComplaintHandler(row.id, {
          assigneeId: selectedId,
          reason: trimmedReason,
        });
        successTitle = t("complaintReassigned");
      } else if (action === "cancel") {
        if (!userId) {
          setError(t("mustBeSignedInToCancel"));
          setSubmitting(false);
          return;
        }
        await cancelAssignment(row.id, {
          releasedBy: userId,
          reason: reason.trim() || null,
        });
        successTitle = t("assignmentCancelled");
      }
      setAction(null);
      if (successTitle) {
        pushSuccess(successTitle, t("listRefreshed"));
      }
      onChanged?.();
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : t("actionFailed"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  const modalTitle =
    action === "assign"
      ? t("assignConfirmTitle")
      : action === "reassign"
        ? t("reassignConfirmTitle")
        : action === "cancel"
          ? t("cancelConfirmTitle")
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
            {tComplaints("assign")}
          </Button>
        ) : null}
        {canReassign ? (
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={() => openAction("reassign")}
          >
            {tComplaints("reassign")}
          </Button>
        ) : null}
        {canCancel ? (
          <Button
            type="button"
            size="sm"
            variant="ghost"
            onClick={() => openAction("cancel")}
          >
            {tCommon("cancel")}
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
              {tCommon("cancel")}
            </Button>
            <Button
              type="button"
              disabled={submitting}
              onClick={() => void confirmAction()}
            >
              {submitting ? t("working") : tCommon("confirm")}
            </Button>
          </>
        }
      >
        <div className="space-y-[var(--ecmp-panel-gap)]">
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
            {action === "assign"
              ? t("assignHint", { number: row.complaintNumber })
              : action === "reassign"
                ? t("reassignHint", { number: row.complaintNumber })
                : t("cancelHint", { number: row.complaintNumber })}
          </p>

          {action === "assign" || action === "reassign" ? (
            <>
              {usersError ? (
                <Alert
                  tone="danger"
                  title={tComplaints("couldNotLoadUsers")}
                  description={usersError}
                  actionLabel={tCommon("retry")}
                  onAction={() => void loadUsers()}
                />
              ) : null}
              <Select
                label={t("assigneeLabel")}
                name="assigneeId"
                required
                placeholder={
                  usersLoading
                    ? tComplaints("loadingUsers")
                    : tComplaints("selectUser")
                }
                value={selectedId}
                options={options}
                disabled={submitting || usersLoading || options.length === 0}
                onChange={(e) => setSelectedId(e.target.value)}
                error={
                  !usersError && !usersLoading && options.length === 0
                    ? tComplaints("noActiveUsersAvailable")
                    : undefined
                }
              />
            </>
          ) : null}

          {action === "reassign" || action === "cancel" ? (
            <div className="space-y-1">
              <label
                htmlFor={`assignment-reason-${row.id}`}
                className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary"
              >
                {action === "reassign"
                  ? t("reasonRequiredLabel")
                  : t("reasonOptionalLabel")}
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
            <Alert tone="danger" title={t("actionFailed")} description={error} />
          ) : null}
        </div>
      </Modal>
    </>
  );
}
