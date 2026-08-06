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
import { FollowUpContext } from "./FollowUpContext";

export interface FollowUpWorkspaceProps {
  complaintId: string;
}

/**
 * SCR-WS-02 — Workspace — Follow-up (Batch B3).
 * Save follow-up note on active case. No create-new-case primary.
 */
export function FollowUpWorkspace({ complaintId }: FollowUpWorkspaceProps) {
  const t = useTranslations("intake");
  const tShell = useTranslations("shell");
  const router = useRouter();
  const { getById, saveFollowUp } = useAssignmentRepository();
  const complaint = getById(complaintId);

  const [note, setNote] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  function backToIntake(): void {
    router.push("/workspace");
  }

  function onSave(): void {
    if (!complaint) return;
    setSaving(true);
    setSaved(false);
    const result = saveFollowUp(complaint.id, note);
    setSaving(false);
    if (!result.ok) {
      setError(t(`followUpError.${result.reason}`));
      return;
    }
    setError(null);
    setNote("");
    setSaved(true);
  }

  if (!complaint) {
    return (
      <WorkspaceLayout>
        <PageHeader
          overline={tShell(getShellBatchOverlineKey())}
          title={t("followUpTitle")}
          breadcrumbs={[
            { label: tShell("homeCrumb"), href: "/workspace" },
            { label: t("newIntakeTitle"), href: "/workspace" },
            { label: t("followUpTitle") },
          ]}
        />
        <Empty
          title={t("followUpNotFoundTitle")}
          description={t("followUpNotFoundDescription")}
          primaryAction={{
            label: t("backToIntake"),
            onClick: backToIntake,
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
          title={t("followUpTitle")}
          description={t("followUpDescription")}
          breadcrumbs={[
            { label: tShell("homeCrumb"), href: "/workspace" },
            { label: t("newIntakeTitle"), href: "/workspace" },
            { label: complaint.reference },
          ]}
          actions={
            <Button type="button" variant="ghost" onClick={backToIntake}>
              {t("backToIntake")}
            </Button>
          }
        />
      }
    >
      <div className="mx-auto flex max-w-5xl flex-col gap-6">
        <FollowUpContext complaint={complaint} />

        <Card>
          <CardHeader>
            <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
              {t("followUpNotesTitle")}
            </h2>
          </CardHeader>
          <CardBody className="space-y-4">
            {complaint.followUpNotes.length === 0 ? (
              <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                {t("followUpNotesEmpty")}
              </p>
            ) : (
              <ul className="space-y-3">
                {complaint.followUpNotes.map((item) => (
                  <li
                    key={item.id}
                    className="rounded-[var(--ecmp-radius-md)] border border-ecmp-border/70 bg-ecmp-surface-sunken/40 p-3"
                  >
                    <p className="text-ecmp-text-primary">{item.text}</p>
                    <p className="mt-1 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                      {new Date(item.recordedAt).toLocaleString()}
                    </p>
                  </li>
                ))}
              </ul>
            )}

            <Textarea
              id="b3-follow-up-note"
              name="followUpNote"
              label={t("followUpInputLabel")}
              description={t("followUpInputHint")}
              rows={4}
              value={note}
              onChange={(event) => {
                setNote(event.target.value);
                setError(null);
                setSaved(false);
              }}
            />

            {error ? <Alert tone="danger" title={error} /> : null}
            {saved ? <Alert tone="info" title={t("followUpSaved")} /> : null}

            <div className="flex flex-col-reverse gap-2 border-t border-ecmp-border/70 pt-4 sm:flex-row sm:justify-between">
              <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                {t("noDuplicateHint")}
              </p>
              <div className="flex flex-col-reverse gap-2 sm:flex-row">
                <Button type="button" variant="secondary" onClick={backToIntake}>
                  {t("backToIntake")}
                </Button>
                <Button
                  type="button"
                  variant="primary"
                  loading={saving}
                  onClick={onSave}
                >
                  {t("saveFollowUp")}
                </Button>
              </div>
            </div>
          </CardBody>
        </Card>
      </div>
    </WorkspaceLayout>
  );
}
