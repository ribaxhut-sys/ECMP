"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import {
  Alert,
  Button,
  Empty,
  PageHeader,
} from "@/shared/ui";
import { WorkspaceLayout } from "@/shared/layouts/shell";
import { getShellBatchOverlineKey } from "@/shared/config/uiBatch";
import {
  getUnitById,
} from "../mock/assignmentRepository";
import { useAssignmentRepository } from "../mock/useAssignmentRepository";
import { AssignmentDialog } from "./AssignmentDialog";
import { AssignmentSummary } from "./AssignmentSummary";
import { UnitSelector } from "./UnitSelector";

export interface AssignmentWorkspaceProps {
  complaintId: string;
}

/**
 * SCR-WS-09 — Assignment Workspace (B1 mock).
 * Flow: select unit → confirm → ASSIGNED → return to Supervisor Queue.
 */
export function AssignmentWorkspace({ complaintId }: AssignmentWorkspaceProps) {
  const t = useTranslations("supervisorAssign");
  const tShell = useTranslations("shell");
  const router = useRouter();
  const { getById, assign } = useAssignmentRepository();
  const complaint = getById(complaintId);

  const [unitId, setUnitId] = useState("");
  const [unitError, setUnitError] = useState<string | undefined>();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedUnit = useMemo(
    () => (unitId ? getUnitById(unitId) : undefined),
    [unitId],
  );

  function backToQueue(): void {
    router.push("/queue");
  }

  function onRequestAssign(): void {
    setError(null);
    if (!unitId) {
      setUnitError(t("unitRequired"));
      return;
    }
    setUnitError(undefined);
    setDialogOpen(true);
  }

  function onConfirmAssign(): void {
    if (!complaint || !unitId) return;
    setConfirming(true);
    const result = assign(complaint.id, unitId);
    setConfirming(false);
    setDialogOpen(false);

    if (!result.ok) {
      setError(t(`assignError.${result.reason}`));
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

  const alreadyAssigned = complaint.status === "ASSIGNED";

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
      <div className="mx-auto flex max-w-2xl flex-col gap-6">
        <AssignmentSummary
          complaint={complaint}
          selectedUnitName={selectedUnit?.name}
        />

        {error ? (
          <Alert tone="danger" title={error} />
        ) : null}

        {alreadyAssigned ? (
          <Alert tone="info" title={t("alreadyAssignedHint")} />
        ) : (
          <>
            <UnitSelector
              value={unitId}
              onChange={(next) => {
                setUnitId(next);
                setUnitError(undefined);
              }}
              error={unitError}
            />

            <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
              <Button type="button" variant="secondary" onClick={backToQueue}>
                {t("cancel")}
              </Button>
              <Button type="button" variant="primary" onClick={onRequestAssign}>
                {t("assign")}
              </Button>
            </div>
          </>
        )}
      </div>

      <AssignmentDialog
        open={dialogOpen}
        reference={complaint.reference}
        unitName={selectedUnit?.name ?? ""}
        confirming={confirming}
        onConfirm={onConfirmAssign}
        onClose={() => {
          if (!confirming) setDialogOpen(false);
        }}
      />
    </WorkspaceLayout>
  );
}
