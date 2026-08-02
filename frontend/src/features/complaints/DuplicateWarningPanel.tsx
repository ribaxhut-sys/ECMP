"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import type {
  CmBatch1DuplicateCheckResponse,
  CmBatch1DuplicateDecision,
} from "@/lib/api";
import { Alert, Button, Empty, Input, Modal, Textarea } from "@/shared/ui";

export interface DuplicateWarningPanelProps {
  open: boolean;
  result: CmBatch1DuplicateCheckResponse | null;
  busy?: boolean;
  onClose: () => void;
  onDecide: (payload: {
    decision: CmBatch1DuplicateDecision;
    survivingComplaintId?: string;
    justification?: string;
  }) => void | Promise<void>;
}

/**
 * SCR-CM-003 — Duplicate warning dialog (detect/warn/link/override/recommend).
 * Batch-1: no Add Case.
 */
export function DuplicateWarningPanel({
  open,
  result,
  busy = false,
  onClose,
  onDecide,
}: DuplicateWarningPanelProps) {
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  const [survivingId, setSurvivingId] = useState("");
  const [justification, setJustification] = useState("");
  const [localError, setLocalError] = useState<string | null>(null);

  const candidates = result?.candidates ?? [];
  const firstId =
    typeof candidates[0]?.complaintId === "string"
      ? candidates[0].complaintId
      : typeof candidates[0]?.id === "string"
        ? candidates[0].id
        : "";

  const effectiveSurviving = survivingId.trim() || firstId;

  async function decide(
    decision: CmBatch1DuplicateDecision,
  ): Promise<void> {
    setLocalError(null);
    if (decision === "link_existing" && !effectiveSurviving) {
      setLocalError(t("selectSurvivingToLink"));
      return;
    }
    if (decision === "override") {
      if (justification.trim().length < 20) {
        setLocalError(t("overrideJustificationMin"));
        return;
      }
    }
    await onDecide({
      decision,
      survivingComplaintId:
        decision === "link_existing" ? effectiveSurviving : undefined,
      justification:
        decision === "override" ? justification.trim() : undefined,
    });
  }

  return (
    <Modal
      open={open}
      onClose={busy ? () => undefined : onClose}
      title={t("duplicateModalTitle")}
      size="lg"
      footer={
        <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:justify-end">
          <Button
            type="button"
            variant="outline"
            disabled={busy}
            onClick={onClose}
          >
            {tCommon("cancel")}
          </Button>
          <Button
            type="button"
            variant="outline"
            disabled={busy}
            loading={busy}
            onClick={() => void decide("recommend_only")}
          >
            {t("recommendExistingOnly")}
          </Button>
          <Button
            type="button"
            variant="outline"
            disabled={busy || !effectiveSurviving}
            loading={busy}
            onClick={() => void decide("link_existing")}
          >
            {t("linkToExisting")}
          </Button>
          <Button
            type="button"
            disabled={busy}
            loading={busy}
            onClick={() => void decide("override")}
          >
            {t("overrideAndCreate")}
          </Button>
        </div>
      }
    >
      <div className="space-y-[var(--ecmp-panel-gap)] text-[length:var(--ecmp-font-body-small-size)]">
        <Alert
          tone="warning"
          title={t("duplicateWarningTitle")}
          description={t("duplicateWarningDescription")}
        />

        {result?.degraded ? (
          <Alert
            tone="info"
            title={t("degradedCheckTitle")}
            description={
              result.laterReviewWorkItemId
                ? t("degradedCheckWithWorkItem", {
                    id: result.laterReviewWorkItemId,
                  })
                : t("degradedCheckGeneric")
            }
          />
        ) : null}

        {localError ? (
          <Alert
            tone="danger"
            title={t("decisionBlocked")}
            description={localError}
          />
        ) : null}

        {candidates.length === 0 ? (
          <Empty
            title={t("noCandidateDetails")}
            description={t("duplicateWarningDescription")}
          />
        ) : (
          <ul className="max-h-48 space-y-2 overflow-auto">
            {candidates.map((c, index) => {
              const id =
                typeof c.complaintId === "string"
                  ? c.complaintId
                  : typeof c.id === "string"
                    ? c.id
                    : `candidate-${index}`;
              const number =
                typeof c.complaintNumber === "string"
                  ? c.complaintNumber
                  : undefined;
              const score =
                typeof c.score === "number" ? c.score : undefined;
              const subject =
                typeof c.subject === "string" ? c.subject : undefined;
              return (
                <li
                  key={id}
                  className="rounded-[var(--ecmp-radius-md)] border border-ecmp-border p-2 font-mono text-[length:var(--ecmp-font-helper-size)]"
                >
                  <button
                    type="button"
                    className="w-full text-left hover:underline"
                    onClick={() => setSurvivingId(id)}
                    disabled={busy}
                  >
                    {number ?? id}
                    {score != null
                      ? ` · ${t("scoreLabel", { score })}`
                      : ""}
                    {subject ? ` · ${subject}` : ""}
                  </button>
                </li>
              );
            })}
          </ul>
        )}

        <Input
          name="survivingComplaintId"
          id="survivingComplaintId"
          label={t("survivingComplaintIdLabel")}
          value={survivingId || effectiveSurviving}
          onChange={(event) => setSurvivingId(event.target.value)}
          disabled={busy}
          hint={t("survivingComplaintIdHint")}
        />

        <Textarea
          name="overrideJustification"
          id="overrideJustification"
          label={t("overrideJustificationLabel")}
          rows={3}
          value={justification}
          onChange={(event) => setJustification(event.target.value)}
          disabled={busy}
          hint={t("overrideJustificationHint")}
        />
      </div>
    </Modal>
  );
}
