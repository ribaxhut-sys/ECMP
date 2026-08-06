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
import { hasRequiredEscalationHistory } from "@/features/supervisor-assign/mock/assignmentRepository";
import { EscalationHistoryPanel } from "./EscalationHistoryPanel";

export type EscalationDecisionMode = "handle" | "forward" | null;

export interface EscalationHandlingWorkspaceProps {
  complaintId: string;
}

/**
 * SCR-WS-11 — Escalation Handling (WF-001-16 / R2-B3).
 * Handle or Forward (mutual exclusive). Optional Request officer context → WS-08.
 * HX-02 escalation portion embedded (wajib).
 */
export function EscalationHandlingWorkspace({
  complaintId,
}: EscalationHandlingWorkspaceProps) {
  const t = useTranslations("escalationHandling");
  const tShell = useTranslations("shell");
  const tAssign = useTranslations("supervisorAssign");
  const router = useRouter();
  const {
    getById,
    handleEscalation,
    forwardEscalation,
    requestEscalationContext,
  } = useAssignmentRepository();
  const complaint = getById(complaintId);

  const [mode, setMode] = useState<EscalationDecisionMode>(null);
  const [forwardReason, setForwardReason] = useState("");
  const [reasonError, setReasonError] = useState<string | undefined>();
  const [handleOpen, setHandleOpen] = useState(false);
  const [forwardOpen, setForwardOpen] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [contextNotice, setContextNotice] = useState<string | null>(null);

  function backToQueue(): void {
    router.push("/queue");
  }

  function onRequestHandle(): void {
    setActionError(null);
    if (!complaint) return;
    if (!hasRequiredEscalationHistory(complaint)) {
      setActionError(t("decisionError.HISTORY_REQUIRED"));
      return;
    }
    setMode("handle");
    setHandleOpen(true);
  }

  function onRequestForward(): void {
    setActionError(null);
    setMode("forward");
    if (!forwardReason.trim()) {
      setReasonError(t("decisionError.REASON_REQUIRED"));
      return;
    }
    if (!complaint || !hasRequiredEscalationHistory(complaint)) {
      setActionError(t("decisionError.HISTORY_REQUIRED"));
      return;
    }
    setReasonError(undefined);
    setForwardOpen(true);
  }

  function onConfirmHandle(): void {
    if (!complaint) return;
    setConfirming(true);
    const result = handleEscalation(complaint.id);
    setConfirming(false);
    setHandleOpen(false);
    if (!result.ok) {
      setActionError(t(`decisionError.${result.reason}`));
      return;
    }
    router.push("/queue");
  }

  function onConfirmForward(): void {
    if (!complaint) return;
    setConfirming(true);
    const result = forwardEscalation(complaint.id, forwardReason);
    setConfirming(false);
    setForwardOpen(false);
    if (!result.ok) {
      setActionError(t(`decisionError.${result.reason}`));
      return;
    }
    router.push("/queue");
  }

  function onRequestContext(): void {
    if (!complaint) return;
    setActionError(null);
    setContextNotice(null);
    const result = requestEscalationContext(complaint.id);
    if (!result.ok) {
      setActionError(t(`contextError.${result.reason}`));
      return;
    }
    setContextNotice(t("contextRequestedNotice"));
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

  if (!complaint.escalationNew || complaint.status === "CLOSED") {
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
              <Badge tone="danger" variant="soft">
                {t("escalationBadge")}
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
        {contextNotice ? <Alert tone="success" title={contextNotice} /> : null}

        <Card>
          <CardHeader>
            <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
              {t("contextTitle")}
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
              <div>
                <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
                  {t("fieldSla")}
                </dt>
                <dd className="text-ecmp-text-primary">
                  {complaint.slaDueAt
                    ? new Intl.DateTimeFormat(undefined, {
                        dateStyle: "medium",
                        timeStyle: "short",
                      }).format(new Date(complaint.slaDueAt))
                    : "—"}
                </dd>
              </div>
              <div>
                <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
                  {t("fieldUnit")}
                </dt>
                <dd className="text-ecmp-text-primary">
                  {complaint.assignedUnitName ?? "—"}
                </dd>
              </div>
            </dl>
            {complaint.escalationContextRequested ? (
              <Alert tone="warning" title={t("waitingContextBanner")} />
            ) : null}
          </CardBody>
        </Card>

        <EscalationHistoryPanel complaint={complaint} />

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
                variant={mode === "handle" ? "primary" : "outline"}
                aria-pressed={mode === "handle"}
                onClick={() => {
                  setMode("handle");
                  setReasonError(undefined);
                  setActionError(null);
                }}
              >
                {t("modeHandle")}
              </Button>
              <Button
                type="button"
                variant={mode === "forward" ? "danger" : "outline"}
                aria-pressed={mode === "forward"}
                onClick={() => {
                  setMode("forward");
                  setActionError(null);
                }}
              >
                {t("modeForward")}
              </Button>
            </div>

            {mode === "forward" ? (
              <Textarea
                id="r2b3-forward-reason"
                name="forwardEscalationReason"
                label={t("forwardReasonLabel")}
                description={t("forwardReasonHint")}
                required
                rows={3}
                value={forwardReason}
                error={reasonError}
                onChange={(event) => {
                  setForwardReason(event.target.value);
                  setReasonError(undefined);
                }}
              />
            ) : null}

            {mode === null ? (
              <Alert tone="info" title={t("selectModeHint")} />
            ) : null}

            <div className="flex flex-col-reverse gap-2 border-t border-ecmp-border/70 pt-4 sm:flex-row sm:justify-between">
              <Button
                type="button"
                variant="secondary"
                disabled={complaint.escalationContextRequested}
                onClick={onRequestContext}
              >
                {t("requestContext")}
              </Button>
              <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
                <Button type="button" variant="ghost" onClick={backToQueue}>
                  {t("backToQueue")}
                </Button>
                {mode === "handle" ? (
                  <Button
                    type="button"
                    variant="primary"
                    onClick={onRequestHandle}
                  >
                    {t("handle")}
                  </Button>
                ) : null}
                {mode === "forward" ? (
                  <Button
                    type="button"
                    variant="danger"
                    onClick={onRequestForward}
                  >
                    {t("forward")}
                  </Button>
                ) : null}
              </div>
            </div>
          </CardBody>
        </Card>
      </div>

      <Modal
        open={handleOpen}
        onClose={() => {
          if (!confirming) setHandleOpen(false);
        }}
        title={t("confirmHandleTitle")}
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-ecmp-text-primary">
            {t("confirmHandleBody", { reference: complaint.reference })}
          </p>
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              disabled={confirming}
              onClick={() => setHandleOpen(false)}
            >
              {t("cancel")}
            </Button>
            <Button
              type="button"
              variant="primary"
              loading={confirming}
              onClick={onConfirmHandle}
            >
              {t("confirmHandle")}
            </Button>
          </div>
        </div>
      </Modal>

      <Modal
        open={forwardOpen}
        onClose={() => {
          if (!confirming) setForwardOpen(false);
        }}
        title={t("confirmForwardTitle")}
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-ecmp-text-primary">
            {t("confirmForwardBody", { reference: complaint.reference })}
          </p>
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              disabled={confirming}
              onClick={() => setForwardOpen(false)}
            >
              {t("cancel")}
            </Button>
            <Button
              type="button"
              variant="danger"
              loading={confirming}
              onClick={onConfirmForward}
            >
              {t("confirmForward")}
            </Button>
          </div>
        </div>
      </Modal>
    </WorkspaceLayout>
  );
}
