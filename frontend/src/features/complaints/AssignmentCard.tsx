"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type FormEvent,
} from "react";
import { useLocale, useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  ApiError,
  assignComplaint,
  fetchComplaintAssignments,
  fetchUsers,
  type UserRef,
} from "@/lib/api";
import type { Assignment } from "@/lib/api/types";
import { formatDateTime } from "@/i18n/formatting";
import {
  Alert,
  Button,
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  ErrorState,
  Select,
  Skeleton,
} from "@/shared/ui";
import { useToast } from "@/shared/providers";

export function AssignmentCard({
  complaintId,
  onAssigned,
}: {
  complaintId: string;
  onAssigned?: () => void;
}) {
  const { hasPermission } = useAuth();
  const { pushSuccess } = useToast();
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  const locale = useLocale();
  const canAssign = hasPermission("complaints:assign");

  function roleLabel(user: UserRef): string {
    return user.roleName?.trim() || user.roleCode?.trim() || tCommon("emDash");
  }

  function userOptionLabel(user: UserRef): string {
    return `${user.fullName} — ${roleLabel(user)}`;
  }

  const [assignment, setAssignment] = useState<Assignment | null>(null);
  const [users, setUsers] = useState<UserRef[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [loading, setLoading] = useState(true);
  const [usersError, setUsersError] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    setUsersError(null);

    try {
      const assignmentsPromise = fetchComplaintAssignments(complaintId);
      const usersPromise = canAssign
        ? fetchUsers({ pageSize: 100, isActive: true }).catch((err) => {
            setUsersError(
              err instanceof ApiError ? err.message : t("unableToLoadUsers"),
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
            : t("unableToLoadAssignment"),
      );
      setAssignment(null);
    } finally {
      setLoading(false);
    }
  }, [canAssign, complaintId, t]);

  useEffect(() => {
    void load();
  }, [load]);

  const options = useMemo(
    () =>
      users.map((user) => ({
        value: user.id,
        label: userOptionLabel(user),
      })),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [users],
  );

  async function handleAssign(event: FormEvent) {
    event.preventDefault();
    setSubmitError(null);

    if (!selectedId) {
      setSubmitError(t("selectAssignee"));
      return;
    }

    setSubmitting(true);
    try {
      await assignComplaint(complaintId, { assigneeId: selectedId });
      pushSuccess(t("complaintAssigned"), t("assigneeSaved"));
      await load();
      onAssigned?.();
    } catch (err) {
      setSubmitError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : t("assignFailed"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  const showForm = canAssign && !assignment;
  const assigneeDisplay =
    assignment?.assigneeName?.trim() ||
    users.find((u) => u.id === assignment?.assigneeId)?.fullName ||
    tCommon("emDash");

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>{t("assignmentCard")}</CardTitle>
        </CardHeader>
        <CardBody className="space-y-[var(--ecmp-panel-gap)]">
          {loading ? (
            <Skeleton rows={2} />
          ) : loadError ? (
            <ErrorState
              title={t("couldNotLoadAssignment")}
              message={loadError}
              onRetry={() => void load()}
            />
          ) : assignment ? (
            <dl className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] sm:grid-cols-2">
              <div className="min-w-0 space-y-1">
                <dt className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                  {t("assignee")}
                </dt>
                <dd className="break-words text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                  {assigneeDisplay}
                </dd>
              </div>
              <div className="min-w-0 space-y-1">
                <dt className="text-[length:var(--ecmp-font-caption-size)] font-medium uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                  {t("assignedAt")}
                </dt>
                <dd className="break-words text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                  {formatDateTime(assignment.assignedAt, locale)}
                </dd>
              </div>
            </dl>
          ) : showForm ? (
            <form className="space-y-[var(--ecmp-panel-gap)]" onSubmit={(e) => void handleAssign(e)}>
              {usersError ? (
                <Alert
                  tone="danger"
                  title={t("couldNotLoadUsers")}
                  description={usersError}
                />
              ) : null}
              <Select
                label={t("assignee")}
                name="assigneeId"
                required
                placeholder={t("selectUser")}
                value={selectedId}
                options={options}
                disabled={submitting || options.length === 0}
                onChange={(e) => setSelectedId(e.target.value)}
                error={
                  !usersError && options.length === 0
                    ? t("noActiveUsersAvailable")
                    : undefined
                }
              />
              {submitError ? (
                <Alert
                  tone="danger"
                  title={t("assignFailed")}
                  description={submitError}
                />
              ) : null}
              <div className="flex justify-end">
                <Button
                  type="submit"
                  disabled={submitting || !selectedId || options.length === 0}
                >
                  {submitting ? t("assigning") : t("assign")}
                </Button>
              </div>
            </form>
          ) : (
            <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
              {t("unassigned")}
            </p>
          )}
        </CardBody>
      </Card>
    </>
  );
}
