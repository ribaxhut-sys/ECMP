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
import {
  hasRequiredRejectHistory,
  submitCompleteness,
} from "@/features/supervisor-assign/mock/assignmentRepository";
import { HandlingContext } from "@/features/officer-handle/components/HandlingContext";
import { ResolutionSummary } from "@/features/submit-review/components/ResolutionSummary";
import { EvidenceListMin } from "@/features/submit-review/components/EvidenceListMin";
import { EvidenceChecklist } from "@/features/submit-review/components/EvidenceChecklist";
import { SubmitConfirmDialog } from "@/features/submit-review/components/SubmitConfirmDialog";
import { DecisionHistoryPanel } from "./DecisionHistoryPanel";
import { RejectionContinuityBanner } from "./RejectionContinuityBanner";

export interface RejectedResubmissionWorkspaceProps {
  complaintId: string;
}

type PrimaryMode = "resubmit" | "save";

/**
 * SCR-WS-06 — Rejected Resubmission (WF-001-09 / R2-B1).
 * History (SCR-HX-01) wajib embedded → correct → Resubmit → PENDING_REVIEW → Queue.
 */
export function RejectedResubmissionWorkspace({
  complaintId,
}: RejectedResubmissionWorkspaceProps) {
  const t = useTranslations("rejectedResubmission");
  const tShell = useTranslations("shell");
  const tHandle = useTranslations("officerHandle");
  const tSubmit = useTranslations("submitReview");
  const router = useRouter();
  const {
    getById,
    submitForReview,
    addMinimalEvidence,
    saveCorrection,
  } = useAssignmentRepository();
  const complaint = getById(complaintId);

  const [resolution, setResolution] = useState(
    () => complaint?.resolutionSummary ?? "",
  );
  const [resolutionError, setResolutionError] = useState<string | undefined>();
  const [primaryMode, setPrimaryMode] = useState<PrimaryMode>("resubmit");
  // Reason already visible in banner + HX-01; soft-gate starts acknowledged.
  const [rejectAcknowledged, setRejectAcknowledged] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState(false);

  function backToQueue(): void {
    router.push("/queue");
  }

  function backToHandling(): void {
    router.push(`/queue/handle/${complaintId}?continuity=edit`);
  }

  function onRequestResubmit(): void {
    setActionError(null);
    setSaveSuccess(false);
    if (!complaint) return;

    if (!hasRequiredRejectHistory(complaint)) {
      setActionError(t("submitError.HISTORY_REQUIRED"));
      return;
    }
    if (!rejectAcknowledged) {
      setActionError(t("submitError.REJECT_NOT_ACKNOWLEDGED"));
      return;
    }

    const checks = submitCompleteness({
      resolutionSummary: resolution,
      evidenceItems: complaint.evidenceItems,
    });
    if (!checks.find((c) => c.key === "resolution")?.filled) {
      setResolutionError(tSubmit("submitError.RESOLUTION_REQUIRED"));
      setActionError(tSubmit("submitError.RESOLUTION_REQUIRED"));
      return;
    }
    if (!checks.find((c) => c.key === "evidence")?.filled) {
      setResolutionError(undefined);
      setActionError(tSubmit("submitError.EVIDENCE_REQUIRED"));
      return;
    }
    setResolutionError(undefined);
    setDialogOpen(true);
  }

  function onConfirmResubmit(): void {
    if (!complaint) return;
    setConfirming(true);
    const result = submitForReview(complaint.id, resolution);
    setConfirming(false);
    setDialogOpen(false);
    if (!result.ok) {
      setActionError(
        result.reason === "HISTORY_REQUIRED"
          ? t("submitError.HISTORY_REQUIRED")
          : tSubmit(`submitError.${result.reason}`),
      );
      return;
    }
    router.push("/queue");
  }

  function onSaveCorrection(): void {
    setActionError(null);
    setSaveSuccess(false);
    if (!complaint) return;
    const result = saveCorrection(complaint.id, resolution);
    if (!result.ok) {
      if (result.reason === "RESOLUTION_REQUIRED") {
        setResolutionError(tSubmit("submitError.RESOLUTION_REQUIRED"));
      }
      setActionError(t(`saveError.${result.reason}`));
      return;
    }
    setResolutionError(undefined);
    setSaveSuccess(true);
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

  if (complaint.status !== "IN_PROGRESS") {
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

  const historyOk = hasRequiredRejectHistory(complaint);

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
            { label: t("title") },
          ]}
          actions={
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone="danger" variant="soft">
                {t("rejectedBadge")}
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
      <div className="mx-auto flex max-w-5xl flex-col gap-6">
        {actionError ? <Alert tone="danger" title={actionError} /> : null}
        {saveSuccess ? (
          <Alert tone="success" title={t("saveSuccess")} />
        ) : null}

        <HandlingContext complaint={complaint} />
        <RejectionContinuityBanner complaint={complaint} />

        {/* History before Decision (WF-000 Continuity reading flow) */}
        <DecisionHistoryPanel
          complaint={complaint}
          rejectAcknowledged={rejectAcknowledged}
          onRejectAcknowledged={() => setRejectAcknowledged(true)}
        />

        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_18rem]">
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
                  {t("correctionTitle")}
                </h2>
                <p className="mt-1 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                  {t("correctionHint")}
                </p>
              </CardHeader>
              <CardBody>
                <ResolutionSummary
                  value={resolution}
                  error={resolutionError}
                  onChange={(value) => {
                    setResolution(value);
                    setResolutionError(undefined);
                    setActionError(null);
                    setSaveSuccess(false);
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

        <div className="space-y-3 border-t border-ecmp-border/70 pt-4">
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant={primaryMode === "resubmit" ? "primary" : "outline"}
              aria-pressed={primaryMode === "resubmit"}
              onClick={() => setPrimaryMode("resubmit")}
            >
              {t("modeResubmit")}
            </Button>
            <Button
              type="button"
              variant={primaryMode === "save" ? "primary" : "outline"}
              aria-pressed={primaryMode === "save"}
              onClick={() => setPrimaryMode("save")}
            >
              {t("modeSave")}
            </Button>
          </div>
          <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
            {t("onePrimaryHint")}
          </p>
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button type="button" variant="secondary" onClick={backToHandling}>
              {t("returnToHandling")}
            </Button>
            <Button type="button" variant="ghost" onClick={backToQueue}>
              {tHandle("backToQueue")}
            </Button>
            {primaryMode === "save" ? (
              <Button
                type="button"
                variant="primary"
                disabled={!historyOk}
                onClick={onSaveCorrection}
              >
                {t("saveCorrection")}
              </Button>
            ) : (
              <Button
                type="button"
                variant="primary"
                disabled={!historyOk}
                onClick={onRequestResubmit}
              >
                {t("resubmit")}
              </Button>
            )}
          </div>
        </div>
      </div>

      <SubmitConfirmDialog
        open={dialogOpen}
        reference={complaint.reference}
        confirming={confirming}
        onConfirm={onConfirmResubmit}
        onClose={() => {
          if (!confirming) setDialogOpen(false);
        }}
      />
    </WorkspaceLayout>
  );
}
