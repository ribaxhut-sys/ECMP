"use client";

import { useMemo, useState } from "react";
import { useTranslations } from "next-intl";
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
  const t = useTranslations("queue");
  const tCommon = useTranslations("common");
  const tComplaints = useTranslations("complaints");
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
      setError(t("mustBeSignedIn"));
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      if (action === "take") {
        await takeQueue(row.id, { assigneeId: userId });
        setToastTitle(t("queueItemTaken"));
      } else if (action === "release") {
        await releaseQueue(row.id, { releasedBy: userId });
        setToastTitle(t("queueItemReleased"));
      } else if (action === "status") {
        if (!statusTarget) {
          setError(t("selectStatusError"));
          setSubmitting(false);
          return;
        }
        await updateQueueStatus(row.id, {
          status: statusTarget as ComplaintStatus,
        });
        setToastTitle(t("statusUpdatedToast"));
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
            : t("actionFailed"),
      );
    } finally {
      setSubmitting(false);
    }
  }

  const modalTitle =
    action === "take"
      ? t("takeConfirmTitle")
      : action === "release"
        ? t("releaseConfirmTitle")
        : action === "status"
          ? t("statusConfirmTitle")
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
            {t("take")}
          </Button>
        ) : null}
        {canRelease ? (
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={() => openAction("release")}
          >
            {t("release")}
          </Button>
        ) : null}
        {canChangeStatus ? (
          <Button
            type="button"
            size="sm"
            variant="ghost"
            onClick={() => openAction("status")}
          >
            {tCommon("status")}
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
              disabled={submitting || (action === "status" && !statusTarget)}
              onClick={() => void confirmAction()}
            >
              {submitting ? t("working") : tCommon("confirm")}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
            {action === "take"
              ? t("assignToYouHint", { number: row.complaintNumber })
              : action === "release"
                ? t("releaseAssigneeHint", { number: row.complaintNumber })
                : t("changeStatusHint", { number: row.complaintNumber })}
          </p>
          {action === "status" ? (
            <Select
              label={t("newStatusLabel")}
              name="status"
              value={statusTarget}
              options={statusActions.map((a) => ({
                value: a.target,
                label: tComplaints(a.labelKey),
              }))}
              onChange={(e) => setStatusTarget(e.target.value)}
              disabled={submitting}
            />
          ) : null}
          {error ? (
            <Alert tone="danger" title={t("actionFailed")} description={error} />
          ) : null}
        </div>
      </Modal>

      <Toast
        open={toastOpen}
        title={toastTitle}
        description={t("queueRefreshedDescription")}
        onClose={() => setToastOpen(false)}
      />
    </>
  );
}
