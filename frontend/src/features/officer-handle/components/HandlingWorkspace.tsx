"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import {
  Alert,
  Button,
  Empty,
  PageHeader,
} from "@/shared/ui";
import { WorkspaceLayout } from "@/shared/layouts/shell";
import { getShellBatchOverlineKey, isBatchAtLeast } from "@/shared/config/uiBatch";
import { useAssignmentRepository } from "@/features/supervisor-assign/mock/useAssignmentRepository";
import {
  hasEscalationContextRequest,
  hasRejectContinuity,
  hasReopenContinuity,
} from "@/features/supervisor-assign/mock/assignmentRepository";
import { HandlingContext } from "./HandlingContext";
import { ProgressNotesPanel } from "./ProgressNotesPanel";
import { StartHandlingDialog } from "./StartHandlingDialog";

export interface HandlingWorkspaceProps {
  complaintId: string;
}

/**
 * SCR-WS-04 — Active Handling (Batch B2).
 * R2-B1: rejected continuity redirects to SCR-WS-06 unless `?continuity=edit`.
 * R2-B2: reopened continuity redirects to SCR-WS-07.
 * R2-B3: escalation context request redirects to SCR-WS-08.
 */
export function HandlingWorkspace({ complaintId }: HandlingWorkspaceProps) {
  const t = useTranslations("officerHandle");
  const tShell = useTranslations("shell");
  const router = useRouter();
  const searchParams = useSearchParams();
  const allowContinuityEdit = searchParams.get("continuity") === "edit";
  const { getById, startHandling, recordProgress } = useAssignmentRepository();
  const complaint = getById(complaintId);
  const submitEnabled = isBatchAtLeast("B4");
  const continuityEnabled = isBatchAtLeast("R2B1");
  const reopenEnabled = isBatchAtLeast("R2B2");
  const escalationEnabled = isBatchAtLeast("R2B3");
  const isRejectedContinuity =
    continuityEnabled && complaint != null && hasRejectContinuity(complaint);
  const isReopenedContinuity =
    reopenEnabled && complaint != null && hasReopenContinuity(complaint);
  const isEscalationContextRequest =
    escalationEnabled &&
    complaint != null &&
    hasEscalationContextRequest(complaint);

  const [dialogOpen, setDialogOpen] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  useEffect(() => {
    if (isReopenedContinuity) {
      router.replace(`/queue/reopened/${complaintId}`);
      return;
    }
    if (isRejectedContinuity && !allowContinuityEdit) {
      router.replace(`/queue/resubmit/${complaintId}`);
      return;
    }
    if (isEscalationContextRequest) {
      router.replace(`/queue/escalation-context/${complaintId}`);
    }
  }, [
    isReopenedContinuity,
    isRejectedContinuity,
    isEscalationContextRequest,
    allowContinuityEdit,
    complaintId,
    router,
  ]);

  function backToQueue(): void {
    router.push("/queue");
  }

  function onConfirmStart(): void {
    if (!complaint) return;
    setConfirming(true);
    const result = startHandling(complaint.id);
    setConfirming(false);
    setDialogOpen(false);
    if (!result.ok) {
      setActionError(t(`startError.${result.reason}`));
    } else {
      setActionError(null);
    }
  }

  if (!complaint) {
    return (
      <WorkspaceLayout>
        <PageHeader
          overline={tShell(getShellBatchOverlineKey())}
          title={t("workspaceTitle")}
          breadcrumbs={[
            { label: tShell("homeCrumb"), href: "/queue" },
            { label: t("queueTitle"), href: "/queue" },
            { label: t("workspaceTitle") },
          ]}
        />
        <Empty
          title={t("notFoundTitle")}
          description={t("notFoundDescription")}
          primaryAction={{
            label: t("backToQueue"),
            onClick: backToQueue,
          }}
        />
      </WorkspaceLayout>
    );
  }

  const isAssigned = complaint.status === "ASSIGNED";
  const isInProgress = complaint.status === "IN_PROGRESS";
  const isNearSla =
    complaint.slaDueAt != null &&
    new Date(complaint.slaDueAt).getTime() - Date.now() < 8 * 3600_000;

  return (
    <WorkspaceLayout
      toolbar={
        <PageHeader
          overline={tShell(getShellBatchOverlineKey())}
          title={t("workspaceTitle")}
          description={t("workspaceDescription")}
          breadcrumbs={[
            { label: tShell("homeCrumb"), href: "/queue" },
            { label: t("queueTitle"), href: "/queue" },
            { label: complaint.reference },
          ]}
          actions={
            <Button type="button" variant="ghost" onClick={backToQueue}>
              {t("backToQueue")}
            </Button>
          }
        />
      }
    >
      <div className="mx-auto flex max-w-3xl flex-col gap-6">
        <HandlingContext complaint={complaint} />

        {isNearSla ? (
          <Alert tone="warning" title={t("slaWarning")} />
        ) : null}

        {actionError ? (
          <Alert tone="danger" title={actionError} />
        ) : null}

        <ProgressNotesPanel
          notes={complaint.progressNotes}
          canRecord={isInProgress}
          onRecord={(text) => {
            const result = recordProgress(complaint.id, text);
            if (!result.ok) {
              return {
                ok: false,
                errorKey: `progressError.${result.reason}`,
              };
            }
            return { ok: true };
          }}
        />

        <div className="flex flex-col gap-3 border-t border-ecmp-border/70 pt-4 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
            {isInProgress
              ? submitEnabled
                ? t("submitReadyHint")
                : t("submitDeferredHint")
              : null}
          </p>
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button type="button" variant="secondary" onClick={backToQueue}>
              {t("backToQueue")}
            </Button>
            {isAssigned ? (
              <Button
                type="button"
                variant="primary"
                onClick={() => {
                  setActionError(null);
                  setDialogOpen(true);
                }}
              >
                {t("startHandling")}
              </Button>
            ) : null}
            {isInProgress ? (
              submitEnabled ? (
                <Button
                  type="button"
                  variant="primary"
                  onClick={() =>
                    router.push(
                      isRejectedContinuity
                        ? `/queue/resubmit/${complaint.id}`
                        : `/queue/submit/${complaint.id}`,
                    )
                  }
                >
                  {isRejectedContinuity
                    ? t("continueResubmit")
                    : t("submitForReview")}
                </Button>
              ) : (
                <Button
                  type="button"
                  variant="outline"
                  disabled
                  title={t("submitDeferredTitle")}
                >
                  {t("submitDeferred")}
                </Button>
              )
            ) : null}
          </div>
        </div>
      </div>

      <StartHandlingDialog
        open={dialogOpen}
        reference={complaint.reference}
        confirming={confirming}
        onConfirm={onConfirmStart}
        onClose={() => {
          if (!confirming) setDialogOpen(false);
        }}
      />
    </WorkspaceLayout>
  );
}
