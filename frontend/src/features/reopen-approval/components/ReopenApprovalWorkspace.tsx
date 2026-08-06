"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import {
  Alert,
  Badge,
  Button,
  Card,
  CardBody,
  CardHeader,
  Empty,
  PageHeader,
  Textarea,
  Modal,
} from "@/shared/ui";
import { WorkspaceLayout } from "@/shared/layouts/shell";
import { getShellBatchOverlineKey } from "@/shared/config/uiBatch";
import { useAssignmentRepository } from "@/features/supervisor-assign/mock/useAssignmentRepository";
import {
  hasRequiredClosureHistory,
} from "@/features/supervisor-assign/mock/assignmentRepository";
import { ClosureHistoryPanel } from "./ClosureHistoryPanel";

export type ReopenDecisionMode = "approve" | "reject" | null;

export interface ReopenApprovalWorkspaceProps {
  complaintId: string;
}

/**
 * SCR-WS-12 — Reopen Approval (WF-001-17 / R2-B2).
 * Approve reopen → REOPENED · Reject reopen → remain CLOSED.
 * HX-02 closure portion embedded (wajib).
 */
export function ReopenApprovalWorkspace({
  complaintId,
}: ReopenApprovalWorkspaceProps) {
  const t = useTranslations("reopenApproval");
  const tShell = useTranslations("shell");
  const tAssign = useTranslations("supervisorAssign");
  const router = useRouter();
  const { getById, approveReopen, rejectReopen } = useAssignmentRepository();
  const complaint = getById(complaintId);

  const [mode, setMode] = useState<ReopenDecisionMode>(null);
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
    if (!complaint) return;
    if (!hasRequiredClosureHistory(complaint)) {
      setActionError(t("decisionError.HISTORY_REQUIRED"));
      return;
    }
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
    if (!complaint || !hasRequiredClosureHistory(complaint)) {
      setActionError(t("decisionError.HISTORY_REQUIRED"));
      return;
    }
    setReasonError(undefined);
    setRejectOpen(true);
  }

  function onConfirmApprove(): void {
    if (!complaint) return;
    setConfirming(true);
    const result = approveReopen(complaint.id);
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
    const result = rejectReopen(complaint.id, rejectReason);
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
          title={t("title")}
          breadcrumbs={[
            { label: tShell("homeCrumb"), href: "/queue" },
            { label: tAssign("queueTitle"), href: "/queue" },
            { label: t("title") },
          ]}
        />
        <Empty
          title={t("notFoundTitle")}
          description={t("notFoundDescription")}
          primaryAction={{ label: t("backToQueue"), onClick: backToQueue }}
        />
      </WorkspaceLayout>
    );
  }

  if (complaint.status !== "CLOSED" || !complaint.reopenPending) {
    return (
      <WorkspaceLayout>
        <PageHeader
          overline={tShell(getShellBatchOverlineKey())}
          title={t("title")}
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
          primaryAction={{ label: t("backToQueue"), onClick: backToQueue }}
        />
      </WorkspaceLayout>
    );
  }

  return (
    <WorkspaceLayout
      toolbar={
        <PageHeader
          overline={tShell(getShellBatchOverlineKey())}
          title={t("title")}
          description={t("description")}
          breadcrumbs={[
            { label: tShell("homeCrumb"), href: "/queue" },
            { label: tAssign("queueTitle"), href: "/queue" },
            { label: complaint.reference },
          ]}
          actions={
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone="warning" variant="soft">
                {t("pendingBadge")}
              </Badge>
              <Button type="button" variant="ghost" onClick={backToQueue}>
                {t("backToQueue")}
              </Button>
            </div>
          }
        />
      }
    >
      <div className="mx-auto flex max-w-5xl flex-col gap-6">
        {actionError ? <Alert tone="danger" title={actionError} /> : null}

        <Card>
          <CardHeader>
            <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
              {t("requestTitle")}
            </h2>
          </CardHeader>
          <CardBody className="space-y-3">
            <dl className="grid gap-3 sm:grid-cols-2">
              <div>
                <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
                  {t("fieldCustomer")}
                </dt>
                <dd className="text-ecmp-text-primary">
                  {complaint.customerName}
                </dd>
              </div>
              <div>
                <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
                  {t("fieldSubject")}
                </dt>
                <dd className="text-ecmp-text-primary">{complaint.subject}</dd>
              </div>
            </dl>
            <Alert tone="info" title={t("requestReasonTitle")} />
            <p className="text-ecmp-text-primary">
              {complaint.reopenReason ?? "—"}
            </p>
          </CardBody>
        </Card>

        <ClosureHistoryPanel complaint={complaint} />

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
                id="r2b2-reject-reopen-reason"
                name="rejectReopenReason"
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
                  {t("approve")}
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

      <Modal
        open={approveOpen}
        onClose={() => {
          if (!confirming) setApproveOpen(false);
        }}
        title={t("confirmApproveTitle")}
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-ecmp-text-primary">
            {t("confirmApproveBody", { reference: complaint.reference })}
          </p>
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              disabled={confirming}
              onClick={() => setApproveOpen(false)}
            >
              {t("cancel")}
            </Button>
            <Button
              type="button"
              variant="primary"
              loading={confirming}
              onClick={onConfirmApprove}
            >
              {t("confirmApprove")}
            </Button>
          </div>
        </div>
      </Modal>

      <Modal
        open={rejectOpen}
        onClose={() => {
          if (!confirming) setRejectOpen(false);
        }}
        title={t("confirmRejectTitle")}
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-ecmp-text-primary">
            {t("confirmRejectBody", { reference: complaint.reference })}
          </p>
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              disabled={confirming}
              onClick={() => setRejectOpen(false)}
            >
              {t("cancel")}
            </Button>
            <Button
              type="button"
              variant="danger"
              loading={confirming}
              onClick={onConfirmReject}
            >
              {t("confirmReject")}
            </Button>
          </div>
        </div>
      </Modal>
    </WorkspaceLayout>
  );
}
