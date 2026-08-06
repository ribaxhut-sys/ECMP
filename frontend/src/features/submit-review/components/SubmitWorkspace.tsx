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
} from "@/shared/ui";
import { WorkspaceLayout } from "@/shared/layouts/shell";
import { getShellBatchOverlineKey } from "@/shared/config/uiBatch";
import { useAssignmentRepository } from "@/features/supervisor-assign/mock/useAssignmentRepository";
import { submitCompleteness } from "@/features/supervisor-assign/mock/assignmentRepository";
import { EvidenceChecklist } from "./EvidenceChecklist";
import { EvidenceListMin } from "./EvidenceListMin";
import { ResolutionSummary } from "./ResolutionSummary";
import { SubmitConfirmDialog } from "./SubmitConfirmDialog";

export interface SubmitWorkspaceProps {
  complaintId: string;
}

/**
 * SCR-WS-05 — Submit for Review (Batch B4).
 * IN_PROGRESS → PENDING_REVIEW → Return Q-01.
 * Cancel → SCR-WS-04.
 */
export function SubmitWorkspace({ complaintId }: SubmitWorkspaceProps) {
  const t = useTranslations("submitReview");
  const tShell = useTranslations("shell");
  const tHandle = useTranslations("officerHandle");
  const router = useRouter();
  const { getById, submitForReview, addMinimalEvidence } =
    useAssignmentRepository();
  const complaint = getById(complaintId);

  const [resolution, setResolution] = useState(
    () => complaint?.resolutionSummary ?? "",
  );
  const [resolutionError, setResolutionError] = useState<string | undefined>();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  function backToHandling(): void {
    router.push(`/queue/handle/${complaintId}`);
  }

  function backToQueue(): void {
    router.push("/queue");
  }

  function onRequestSubmit(): void {
    setActionError(null);
    if (!complaint) return;

    const checks = submitCompleteness({
      resolutionSummary: resolution,
      evidenceItems: complaint.evidenceItems,
    });
    if (!checks.find((c) => c.key === "resolution")?.filled) {
      setResolutionError(t("submitError.RESOLUTION_REQUIRED"));
      setActionError(t("submitError.RESOLUTION_REQUIRED"));
      return;
    }
    if (!checks.find((c) => c.key === "evidence")?.filled) {
      setResolutionError(undefined);
      setActionError(t("submitError.EVIDENCE_REQUIRED"));
      return;
    }
    setResolutionError(undefined);
    setDialogOpen(true);
  }

  function onConfirmSubmit(): void {
    if (!complaint) return;
    setConfirming(true);
    const result = submitForReview(complaint.id, resolution);
    setConfirming(false);
    setDialogOpen(false);
    if (!result.ok) {
      setActionError(t(`submitError.${result.reason}`));
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

  if (complaint.status !== "IN_PROGRESS" && complaint.status !== "REOPENED") {
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
            label: t("backToHandling"),
            onClick: backToHandling,
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
          title={t("title")}
          description={t("description")}
          breadcrumbs={[
            { label: tShell("homeCrumb"), href: "/queue" },
            { label: tHandle("queueTitle"), href: "/queue" },
            { label: complaint.reference, href: `/queue/handle/${complaint.id}` },
            { label: t("title") },
          ]}
          actions={
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone="primary" variant="outline">
                {complaint.status}
              </Badge>
              <Button type="button" variant="ghost" onClick={backToHandling}>
                {t("cancel")}
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
              {t("contextTitle")}
            </h2>
          </CardHeader>
          <CardBody>
            <dl className="grid gap-3 sm:grid-cols-2">
              <div>
                <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
                  {t("fieldSubject")}
                </dt>
                <dd className="text-ecmp-text-primary">{complaint.subject}</dd>
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
                  {t("fieldUnit")}
                </dt>
                <dd className="text-ecmp-text-primary">
                  {complaint.assignedUnitName ?? "—"}
                </dd>
              </div>
              <div>
                <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
                  {t("fieldPriority")}
                </dt>
                <dd className="text-ecmp-text-primary">{complaint.priority}</dd>
              </div>
            </dl>
          </CardBody>
        </Card>

        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_18rem]">
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
                  {t("resolutionTitle")}
                </h2>
              </CardHeader>
              <CardBody>
                <ResolutionSummary
                  value={resolution}
                  error={resolutionError}
                  onChange={(value) => {
                    setResolution(value);
                    setResolutionError(undefined);
                    setActionError(null);
                  }}
                />
              </CardBody>
            </Card>

            <EvidenceListMin
              items={complaint.evidenceItems}
              canAdd
              onAdd={(fileName) => {
                const result = addMinimalEvidence(complaint.id, fileName);
                if (!result.ok) {
                  return {
                    ok: false,
                    errorKey: `evidenceError.${result.reason}`,
                  };
                }
                setActionError(null);
                return { ok: true };
              }}
            />
          </div>

          <aside className="lg:sticky lg:top-4 lg:self-start">
            <EvidenceChecklist
              resolutionSummary={resolution}
              evidenceItems={complaint.evidenceItems}
            />
          </aside>
        </div>

        <div className="flex flex-col-reverse gap-2 border-t border-ecmp-border/70 pt-4 sm:flex-row sm:justify-end">
          <Button type="button" variant="secondary" onClick={backToHandling}>
            {t("cancel")}
          </Button>
          <Button type="button" variant="primary" onClick={onRequestSubmit}>
            {t("submit")}
          </Button>
        </div>
      </div>

      <SubmitConfirmDialog
        open={dialogOpen}
        reference={complaint.reference}
        confirming={confirming}
        onConfirm={onConfirmSubmit}
        onClose={() => {
          if (!confirming) setDialogOpen(false);
        }}
      />
    </WorkspaceLayout>
  );
}
