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
import { hasEscalationContextRequest } from "@/features/supervisor-assign/mock/assignmentRepository";

export interface EscalationHandoverWorkspaceProps {
  complaintId: string;
}

/**
 * SCR-WS-08 — Escalation Context Handover (WF-001-11 / R2-B3).
 * Provide context requested by Supervisor without resetting officer progress.
 */
export function EscalationHandoverWorkspace({
  complaintId,
}: EscalationHandoverWorkspaceProps) {
  const t = useTranslations("escalationHandover");
  const tShell = useTranslations("shell");
  const tHandle = useTranslations("officerHandle");
  const router = useRouter();
  const { getById, submitEscalationContext } = useAssignmentRepository();
  const complaint = getById(complaintId);

  const [contextPackage, setContextPackage] = useState("");
  const [contextError, setContextError] = useState<string | undefined>();
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [successRef, setSuccessRef] = useState<string | null>(null);
  const progressSnapshot = complaint?.progressNotes.length ?? 0;

  function backToQueue(): void {
    router.push("/queue");
  }

  function backToHandling(): void {
    if (!complaint) {
      backToQueue();
      return;
    }
    router.push(`/queue/handle/${complaint.id}`);
  }

  function onSubmitRequest(): void {
    setActionError(null);
    if (!contextPackage.trim()) {
      setContextError(t("submitError.CONTEXT_REQUIRED"));
      return;
    }
    setContextError(undefined);
    setConfirmOpen(true);
  }

  function onConfirmSubmit(): void {
    if (!complaint) return;
    setConfirming(true);
    const result = submitEscalationContext(complaint.id, contextPackage);
    setConfirming(false);
    setConfirmOpen(false);
    if (!result.ok) {
      setActionError(t(`submitError.${result.reason}`));
      return;
    }
    setSuccessRef(result.complaint.reference);
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
          primaryAction={{ label: t("backToQueue"), onClick: backToQueue }}
        />
      </WorkspaceLayout>
    );
  }

  if (!hasEscalationContextRequest(complaint)) {
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
          title={t("noRequestTitle")}
          description={t("noRequestDescription")}
          primaryAction={{
            label: t("backToHandling"),
            onClick: backToHandling,
          }}
        />
      </WorkspaceLayout>
    );
  }

  if (successRef) {
    return (
      <WorkspaceLayout
        toolbar={
          <PageHeader
            overline={tShell(getShellBatchOverlineKey())}
            title={t("title")}
            breadcrumbs={[
              { label: tShell("homeCrumb"), href: "/queue" },
              { label: tHandle("queueTitle"), href: "/queue" },
              { label: successRef },
            ]}
          />
        }
      >
        <div className="mx-auto max-w-3xl space-y-4">
          <Alert tone="success" title={t("successTitle")} />
          <p className="text-ecmp-text-primary">
            {t("successBody", { reference: successRef, count: progressSnapshot })}
          </p>
          <Button type="button" variant="primary" onClick={backToQueue}>
            {t("backToQueue")}
          </Button>
        </div>
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
            { label: tHandle("queueTitle"), href: "/queue" },
            { label: complaint.reference },
          ]}
          actions={
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone="warning" variant="soft">
                {t("contextRequestedBadge")}
              </Badge>
              <Button type="button" variant="ghost" onClick={backToHandling}>
                {t("backToHandling")}
              </Button>
            </div>
          }
        />
      }
    >
      <div className="mx-auto flex max-w-3xl flex-col gap-6">
        {actionError ? <Alert tone="danger" title={actionError} /> : null}

        <Card>
          <CardHeader>
            <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
              {t("requestSummaryTitle")}
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
            <Alert tone="info" title={t("escalationReasonTitle")} />
            <p className="text-ecmp-text-primary">
              {complaint.escalationNote ?? "—"}
            </p>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
              {t("progressTitle")}
            </h2>
            <p className="mt-1 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
              {t("progressHint")}
            </p>
          </CardHeader>
          <CardBody>
            {complaint.progressNotes.length === 0 ? (
              <p className="text-ecmp-text-secondary">{t("progressEmpty")}</p>
            ) : (
              <ul className="space-y-2">
                {complaint.progressNotes.map((note) => (
                  <li
                    key={note.id}
                    className="rounded-md border border-ecmp-border/60 px-3 py-2 text-ecmp-text-primary"
                  >
                    {note.text}
                  </li>
                ))}
              </ul>
            )}
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
              {t("packageTitle")}
            </h2>
            <p className="mt-1 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
              {t("packageHint")}
            </p>
          </CardHeader>
          <CardBody className="space-y-4">
            <Textarea
              id="r2b3-escalation-context"
              name="escalationContextPackage"
              label={t("packageLabel")}
              description={t("packageDescription")}
              required
              rows={5}
              value={contextPackage}
              error={contextError}
              onChange={(event) => {
                setContextPackage(event.target.value);
                setContextError(undefined);
              }}
            />
            <div className="flex flex-col-reverse gap-2 border-t border-ecmp-border/70 pt-4 sm:flex-row sm:justify-end">
              <Button type="button" variant="secondary" onClick={backToHandling}>
                {t("cancel")}
              </Button>
              <Button type="button" variant="primary" onClick={onSubmitRequest}>
                {t("submitContext")}
              </Button>
            </div>
          </CardBody>
        </Card>
      </div>

      <Modal
        open={confirmOpen}
        onClose={() => {
          if (!confirming) setConfirmOpen(false);
        }}
        title={t("confirmTitle")}
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-ecmp-text-primary">
            {t("confirmBody", { reference: complaint.reference })}
          </p>
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              disabled={confirming}
              onClick={() => setConfirmOpen(false)}
            >
              {t("cancel")}
            </Button>
            <Button
              type="button"
              variant="primary"
              loading={confirming}
              onClick={onConfirmSubmit}
            >
              {t("confirmSubmit")}
            </Button>
          </div>
        </div>
      </Modal>
    </WorkspaceLayout>
  );
}
