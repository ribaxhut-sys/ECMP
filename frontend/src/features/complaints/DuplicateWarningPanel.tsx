"use client";

import { useState } from "react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import type {
  CmBatch1DuplicateCheckResponse,
  CmBatch1DuplicateDecision,
} from "@/lib/api";
import { Alert, Badge, Button, Empty, Input, Modal, Textarea } from "@/shared/ui";

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

function formatWhen(value: string | null | undefined): string {
  if (!value) return "";
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

/**
 * SCR-CM-003 — Duplicate warning dialog (detect/warn/link/override/recommend).
 * Batch-1: no Add Case. Candidates include status + review link (FR-003 §9).
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
            primaryAction={{
              label: tCommon("closeDialog"),
              onClick: onClose,
              disabled: busy,
            }}
          />
        ) : (
          <ul className="max-h-64 space-y-2 overflow-auto">
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
              const statusRaw =
                typeof c.status === "string" ? c.status.toUpperCase() : "";
              const isClosed = statusRaw === "CLOSED" || c.open === false;
              const createdLabel = formatWhen(
                typeof c.createdAt === "string" ? c.createdAt : undefined,
              );
              const selected = effectiveSurviving === id;
              const detailHref = `/complaints/cm/${encodeURIComponent(id)}`;
              return (
                <li
                  key={id}
                  className={
                    selected
                      ? "rounded-[var(--ecmp-radius-md)] border border-ecmp-primary bg-ecmp-primary-muted/40 p-3"
                      : "rounded-[var(--ecmp-radius-md)] border border-ecmp-border p-3"
                  }
                >
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                    <button
                      type="button"
                      className="min-w-0 flex-1 text-left"
                      onClick={() => setSurvivingId(id)}
                      disabled={busy}
                    >
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-mono text-[length:var(--ecmp-font-body-small-size)] font-medium text-ecmp-text-primary">
                          {number ?? id}
                        </span>
                        <Badge tone={isClosed ? "success" : "info"}>
                          {isClosed ? t("statusClosed") : t("statusOpen")}
                        </Badge>
                        {score != null ? (
                          <span className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                            {t("scoreLabel", { score })}
                          </span>
                        ) : null}
                      </div>
                      {subject ? (
                        <p className="mt-1 text-ecmp-text-primary">{subject}</p>
                      ) : null}
                      {createdLabel ? (
                        <p className="mt-0.5 text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                          {t("candidateCreatedAt", { date: createdLabel })}
                        </p>
                      ) : null}
                    </button>
                    <Link
                      href={detailHref}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex shrink-0 items-center justify-center rounded-[var(--ecmp-radius-button)] border border-ecmp-border bg-ecmp-surface px-3 py-1.5 text-[length:var(--ecmp-font-helper-size)] font-medium text-ecmp-primary underline-offset-2 hover:bg-ecmp-hover hover:underline"
                      onClick={(event) => event.stopPropagation()}
                    >
                      {t("reviewCandidate")}
                    </Link>
                  </div>
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
