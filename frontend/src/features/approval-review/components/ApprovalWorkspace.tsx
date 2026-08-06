"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import {
  Alert,
  Button,
  Card,
  CardBody,
  CardHeader,
  Empty,
  PageHeader,
  Textarea,
} from "@/shared/ui";
import { WorkspaceLayout } from "@/shared/layouts/shell";
import { getShellBatchOverlineKey } from "@/shared/config/uiBatch";
import { useAssignmentRepository } from "@/features/supervisor-assign/mock/useAssignmentRepository";
import { ApprovalContext } from "./ApprovalContext";
import {
  ApproveConfirmDialog,
  RejectConfirmDialog,
} from "./ApprovalDialogs";
import { ApprovalSummary } from "./ApprovalSummary";

export type DecisionMode = "approve" | "reject" | null;

export interface ApprovalWorkspaceProps {
  complaintId: string;
}

/**
 * SCR-WS-10 — Approval Review (Batch B5).
 * Approve & Close → CLOSED · Reject → IN_PROGRESS (+ Decision History for R2-B1).
 * One primary decision mode at a time.
 */
export function ApprovalWorkspace({ complaintId }: ApprovalWorkspaceProps) {
  const t = useTranslations("approvalReview");
  const tShell = useTranslations("shell");
  const tAssign = useTranslations("supervisorAssign");
  const router = useRouter();
  const { getById, approveAndClose, rejectReview } = useAssignmentRepository();
  const complaint = getById(complaintId);

  const [mode, setMode] = useState<DecisionMode>(null);
  const [rejectReason, setRejectReason] = useState("");
  const [reasonError, setReasonError] = useState<string | undefined>();
  const [approveOpen, setApproveOpen] = useState(false);
  const [rejectOpen, setRejectOpen] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  function backToQueue(): void {
    router.push("/queue");
  }

  function onRequestApprove(): void {
    setActionError(null);
    setMode("approve");
    setApproveOpen(true);
  }

  function onRequestReject(): void {
    setActionError(null);
    setMode("reject");
    if (!rejectReason.trim()) {
      setReasonError(t("decisionError.REASON_REQUIRED"));
      return;
    }
    setReasonError(undefined);
    setRejectOpen(true);
  }

  function onConfirmApprove(): void {
    if (!complaint) return;
    setConfirming(true);
    const result = approveAndClose(complaint.id);
    setConfirming(false);
    setApproveOpen(false);
    if (!result.ok) {
      setActionError(t(`decisionError.${result.reason}`));
      return;
    }
    router.push("/queue");
  }

  function onConfirmReject(): void {
    if (!complaint) return;
    setConfirming(true);
    const result = rejectReview(complaint.id, rejectReason);
    setConfirming(false);
    setRejectOpen(false);
    if (!result.ok) {
      setActionError(t(`decisionError.${result.reason}`));
      return;
    }
    router.push("/queue");
  }

  if (!complaint) {
    return (
      <WorkspaceLayout>
        <PageHeader
          overline={tShell(getShellBatchOverlineKey())}
          title={t("workspaceTitle")}
          breadcrumbs={[
            { label: tShell("homeCrumb"), href: "/queue" },
            { label: tAssign("queueTitle"), href: "/queue" },
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

  if (complaint.status !== "PENDING_REVIEW") {
    return (
      <WorkspaceLayout>
        <PageHeader
          overline={tShell(getShellBatchOverlineKey())}
          title={t("workspaceTitle")}
          breadcrumbs={[
            { label: tShell("homeCrumb"), href: "/queue" },
            { label: tAssign("queueTitle"), href: "/queue" },
            { label: complaint.reference },
          ]}
        />
        <Empty
          title={t("wrongStatusTitle")}
          description={t("wrongStatusDescription", {
            status: complaint.status,
          })}
          primaryAction={{
            label: t("backToQueue"),
            onClick: backToQueue,
          }}
        />
      </WorkspaceLayout>
    );
  }

  return (
    <WorkspaceLayout
      toolbar={
        <PageHeader
          overline={tShell(getShellBatchOverlineKey())}
          title={t("workspaceTitle")}
          description={t("workspaceDescription")}
          breadcrumbs={[
            { label: tShell("homeCrumb"), href: "/queue" },
            { label: tAssign("queueTitle"), href: "/queue" },
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
      <div className="mx-auto flex max-w-5xl flex-col gap-6">
        {actionError ? <Alert tone="danger" title={actionError} /> : null}

        <ApprovalContext complaint={complaint} />
        <ApprovalSummary complaint={complaint} />

        <Card>
          <CardHeader>
            <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
              {t("decisionTitle")}
            </h2>
            <p className="mt-1 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
              {t("decisionHint")}
            </p>
          </CardHeader>
          <CardBody className="space-y-4">
            <div className="flex flex-wrap gap-2">
              <Button
                type="button"
                variant={mode === "approve" ? "primary" : "outline"}
                aria-pressed={mode === "approve"}
                onClick={() => {
                  setMode("approve");
                  setReasonError(undefined);
                  setActionError(null);
                }}
              >
                {t("modeApprove")}
              </Button>
              <Button
                type="button"
                variant={mode === "reject" ? "danger" : "outline"}
                aria-pressed={mode === "reject"}
                onClick={() => {
                  setMode("reject");
                  setActionError(null);
                }}
              >
                {t("modeReject")}
              </Button>
            </div>

            {mode === "reject" ? (
              <Textarea
                id="b5-reject-reason"
                name="rejectReason"
                label={t("rejectReasonLabel")}
                description={t("rejectReasonHint")}
                required
                rows={3}
                value={rejectReason}
                error={reasonError}
                onChange={(event) => {
                  setRejectReason(event.target.value);
                  setReasonError(undefined);
                }}
              />
            ) : null}

            {mode === null ? (
              <Alert tone="info" title={t("selectModeHint")} />
            ) : null}

            <div className="flex flex-col-reverse gap-2 border-t border-ecmp-border/70 pt-4 sm:flex-row sm:justify-end">
              <Button type="button" variant="secondary" onClick={backToQueue}>
                {t("backToQueue")}
              </Button>
              {mode === "approve" ? (
                <Button
                  type="button"
                  variant="primary"
                  onClick={onRequestApprove}
                >
                  {t("approveClose")}
                </Button>
              ) : null}
              {mode === "reject" ? (
                <Button
                  type="button"
                  variant="danger"
                  onClick={onRequestReject}
                >
                  {t("reject")}
                </Button>
              ) : null}
            </div>
          </CardBody>
        </Card>
      </div>

      <ApproveConfirmDialog
        open={approveOpen}
        reference={complaint.reference}
        confirming={confirming}
        onConfirm={onConfirmApprove}
        onClose={() => {
          if (!confirming) setApproveOpen(false);
        }}
      />
      <RejectConfirmDialog
        open={rejectOpen}
        reference={complaint.reference}
        reason={rejectReason}
        confirming={confirming}
        onConfirm={onConfirmReject}
        onClose={() => {
          if (!confirming) setRejectOpen(false);
        }}
      />
    </WorkspaceLayout>
  );
}
