"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import {
  Alert,
  Badge,
  Button,
  Empty,
  PageHeader,
} from "@/shared/ui";
import { WorkspaceLayout } from "@/shared/layouts/shell";
import { getShellBatchOverlineKey, isBatchAtLeast } from "@/shared/config/uiBatch";
import { useAssignmentRepository } from "@/features/supervisor-assign/mock/useAssignmentRepository";
import { HandlingContext } from "@/features/officer-handle/components/HandlingContext";
import { ProgressNotesPanel } from "@/features/officer-handle/components/ProgressNotesPanel";
import { DecisionHistoryPanel } from "@/features/rejected-resubmission/components/DecisionHistoryPanel";

export interface ReopenedContinuationWorkspaceProps {
  complaintId: string;
}

/**
 * SCR-WS-07 — Reopened Continuation (WF-001-10 / R2-B2).
 * History (SCR-HX-01) wajib → Continue → Submit (reuse SCR-WS-05).
 */
export function ReopenedContinuationWorkspace({
  complaintId,
}: ReopenedContinuationWorkspaceProps) {
  const t = useTranslations("reopenedContinuation");
  const tShell = useTranslations("shell");
  const tHandle = useTranslations("officerHandle");
  const router = useRouter();
  const { getById, continueReopened, recordProgress } =
    useAssignmentRepository();
  const complaint = getById(complaintId);
  const submitEnabled = isBatchAtLeast("B4");

  const [actionError, setActionError] = useState<string | null>(null);
  const [continuing, setContinuing] = useState(false);

  function backToQueue(): void {
    router.push("/queue");
  }

  function onContinue(): void {
    if (!complaint) return;
    setActionError(null);
    setContinuing(true);
    const result = continueReopened(complaint.id);
    setContinuing(false);
    if (!result.ok) {
      setActionError(t(`continueError.${result.reason}`));
    }
  }

  if (!complaint) {
    return (
      <WorkspaceLayout>
        <PageHeader
          overline={tShell(getShellBatchOverlineKey())}
          title={t("title")}
          breadcrumbs={[
            { label: tShell("homeCrumb"), href: "/queue" },
            { label: tHandle("queueTitle"), href: "/queue" },
            { label: t("title") },
          ]}
        />
        <Empty
          title={t("notFoundTitle")}
          description={t("notFoundDescription")}
          primaryAction={{
            label: tHandle("backToQueue"),
            onClick: backToQueue,
          }}
        />
      </WorkspaceLayout>
    );
  }

  if (complaint.status !== "REOPENED" && complaint.status !== "IN_PROGRESS") {
    return (
      <WorkspaceLayout>
        <PageHeader
          overline={tShell(getShellBatchOverlineKey())}
          title={t("title")}
          breadcrumbs={[
            { label: tShell("homeCrumb"), href: "/queue" },
            { label: tHandle("queueTitle"), href: "/queue" },
            { label: complaint.reference },
          ]}
        />
        <Empty
          title={t("wrongStatusTitle")}
          description={t("wrongStatusDescription", {
            status: complaint.status,
          })}
          primaryAction={{
            label: tHandle("backToQueue"),
            onClick: backToQueue,
          }}
        />
      </WorkspaceLayout>
    );
  }

  const isReopened = complaint.status === "REOPENED";
  const isInProgress = complaint.status === "IN_PROGRESS";

  return (
    <WorkspaceLayout
      toolbar={
        <PageHeader
          overline={tShell(getShellBatchOverlineKey())}
          title={t("title")}
          description={t("description")}
          breadcrumbs={[
            { label: tShell("homeCrumb"), href: "/queue" },
            { label: tHandle("queueTitle"), href: "/queue" },
            { label: complaint.reference },
          ]}
          actions={
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone="warning" variant="soft">
                {t("reopenedBadge")}
              </Badge>
              <Badge tone="primary" variant="outline">
                {complaint.status}
              </Badge>
              <Button type="button" variant="ghost" onClick={backToQueue}>
                {tHandle("backToQueue")}
              </Button>
            </div>
          }
        />
      }
    >
      <div className="mx-auto flex max-w-3xl flex-col gap-6">
        {actionError ? <Alert tone="danger" title={actionError} /> : null}
        {complaint.reopenReason ? (
          <Alert tone="info" title={t("reopenContextTitle")} />
        ) : null}
        {complaint.reopenReason ? (
          <p className="-mt-4 text-ecmp-text-primary">{complaint.reopenReason}</p>
        ) : null}

        <HandlingContext complaint={complaint} />

        <DecisionHistoryPanel complaint={complaint} variant="reopen" />

        <ProgressNotesPanel
          notes={complaint.progressNotes}
          canRecord={isReopened || isInProgress}
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
            {isInProgress ? t("submitReadyHint") : t("continueHint")}
          </p>
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button type="button" variant="secondary" onClick={backToQueue}>
              {tHandle("backToQueue")}
            </Button>
            {isReopened ? (
              <Button
                type="button"
                variant="primary"
                loading={continuing}
                onClick={onContinue}
              >
                {t("continue")}
              </Button>
            ) : null}
            {isInProgress && submitEnabled ? (
              <Button
                type="button"
                variant="primary"
                onClick={() =>
                  router.push(`/queue/submit/${complaint.id}`)
                }
              >
                {tHandle("submitForReview")}
              </Button>
            ) : null}
          </div>
        </div>
      </div>
    </WorkspaceLayout>
  );
}
