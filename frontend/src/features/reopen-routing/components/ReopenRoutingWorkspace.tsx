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
} from "@/shared/ui";
import { WorkspaceLayout } from "@/shared/layouts/shell";
import { getShellBatchOverlineKey } from "@/shared/config/uiBatch";
import { useAssignmentRepository } from "@/features/supervisor-assign/mock/useAssignmentRepository";

export interface ReopenRoutingWorkspaceProps {
  complaintId: string;
}

/**
 * SCR-WS-03 — Reopen Routing (WF-001-06 / R2-B2).
 * Route reopen request for CLOSED case → stay on intake (not Queue).
 */
export function ReopenRoutingWorkspace({
  complaintId,
}: ReopenRoutingWorkspaceProps) {
  const t = useTranslations("reopenRouting");
  const tShell = useTranslations("shell");
  const tIntake = useTranslations("intake");
  const router = useRouter();
  const { getById, requestReopen } = useAssignmentRepository();
  const complaint = getById(complaintId);

  const [reason, setReason] = useState("");
  const [reasonError, setReasonError] = useState<string | undefined>();
  const [confirming, setConfirming] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [successRef, setSuccessRef] = useState<string | null>(null);

  function backToIntake(): void {
    router.push("/workspace");
  }

  function onRoute(): void {
    setActionError(null);
    if (!complaint) return;
    if (!reason.trim()) {
      setReasonError(t("routeError.REASON_REQUIRED"));
      return;
    }
    setReasonError(undefined);
    setConfirming(true);
    const result = requestReopen(complaint.id, reason);
    setConfirming(false);
    if (!result.ok) {
      setActionError(t(`routeError.${result.reason}`));
      return;
    }
    setSuccessRef(result.complaint.reference);
    setReason("");
  }

  if (!complaint) {
    return (
      <WorkspaceLayout>
        <PageHeader
          overline={tShell(getShellBatchOverlineKey())}
          title={t("title")}
          breadcrumbs={[
            { label: tShell("homeCrumb"), href: "/workspace" },
            { label: tIntake("newIntakeTitle"), href: "/workspace" },
            { label: t("title") },
          ]}
        />
        <Empty
          title={t("notFoundTitle")}
          description={t("notFoundDescription")}
          primaryAction={{ label: t("backToIntake"), onClick: backToIntake }}
        />
      </WorkspaceLayout>
    );
  }

  if (complaint.status !== "CLOSED") {
    return (
      <WorkspaceLayout>
        <PageHeader
          overline={tShell(getShellBatchOverlineKey())}
          title={t("title")}
          breadcrumbs={[
            { label: tShell("homeCrumb"), href: "/workspace" },
            { label: tIntake("newIntakeTitle"), href: "/workspace" },
            { label: complaint.reference },
          ]}
        />
        <Empty
          title={t("wrongStatusTitle")}
          description={t("wrongStatusDescription", {
            status: complaint.status,
          })}
          primaryAction={{ label: t("backToIntake"), onClick: backToIntake }}
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
              { label: tShell("homeCrumb"), href: "/workspace" },
              { label: tIntake("newIntakeTitle"), href: "/workspace" },
              { label: t("title") },
            ]}
          />
        }
      >
        <div className="mx-auto flex max-w-3xl flex-col gap-4">
          <Alert
            tone="success"
            title={t("routeSuccess", { reference: successRef })}
          />
          <Button type="button" variant="primary" onClick={backToIntake}>
            {t("readyNextContact")}
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
            { label: tShell("homeCrumb"), href: "/workspace" },
            { label: tIntake("newIntakeTitle"), href: "/workspace" },
            { label: complaint.reference },
          ]}
          actions={
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone="neutral" variant="outline">
                CLOSED
              </Badge>
              <Button type="button" variant="ghost" onClick={backToIntake}>
                {t("cancel")}
              </Button>
            </div>
          }
        />
      }
    >
      <div className="mx-auto flex max-w-3xl flex-col gap-6">
        {actionError ? <Alert tone="danger" title={actionError} /> : null}
        {complaint.reopenPending ? (
          <Alert tone="warning" title={t("alreadyPending")} />
        ) : null}

        <Card>
          <CardHeader>
            <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
              {t("contextTitle")}
            </h2>
          </CardHeader>
          <CardBody>
            <dl className="grid gap-3 sm:grid-cols-2">
              <div>
                <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
                  {t("fieldReference")}
                </dt>
                <dd className="text-ecmp-text-primary">{complaint.reference}</dd>
              </div>
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
                  {t("fieldClosedAt")}
                </dt>
                <dd className="text-ecmp-text-primary">
                  {complaint.closedAt ?? "—"}
                </dd>
              </div>
              <div>
                <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
                  {t("fieldSubject")}
                </dt>
                <dd className="text-ecmp-text-primary">{complaint.subject}</dd>
              </div>
            </dl>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
              {t("closureSummaryTitle")}
            </h2>
          </CardHeader>
          <CardBody>
            <p className="text-ecmp-text-primary">
              {complaint.resolutionSummary ?? t("closureSummaryEmpty")}
            </p>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
              {t("reasonTitle")}
            </h2>
          </CardHeader>
          <CardBody>
            <Textarea
              id="r2b2-reopen-reason"
              name="reopenReason"
              label={t("reasonLabel")}
              description={t("reasonHint")}
              required
              rows={4}
              value={reason}
              error={reasonError}
              disabled={complaint.reopenPending}
              onChange={(event) => {
                setReason(event.target.value);
                setReasonError(undefined);
              }}
            />
          </CardBody>
        </Card>

        <div className="flex flex-col-reverse gap-2 border-t border-ecmp-border/70 pt-4 sm:flex-row sm:justify-end">
          <Button type="button" variant="secondary" onClick={backToIntake}>
            {t("cancel")}
          </Button>
          <Button
            type="button"
            variant="primary"
            loading={confirming}
            disabled={complaint.reopenPending}
            onClick={onRoute}
          >
            {t("route")}
          </Button>
        </div>
      </div>
    </WorkspaceLayout>
  );
}
