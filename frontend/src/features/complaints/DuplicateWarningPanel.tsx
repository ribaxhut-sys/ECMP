"use client";

import { useState } from "react";
import type {
  CmBatch1DuplicateCheckResponse,
  CmBatch1DuplicateDecision,
} from "@/lib/api";
import { Alert, Button, Input, Modal, Textarea } from "@/shared/ui";

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
      setLocalError("Select or enter a surviving complaint ID to link.");
      return;
    }
    if (decision === "override") {
      if (justification.trim().length < 20) {
        setLocalError(
          "Override justification must be at least 20 characters.",
        );
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
      title="Possible duplicate complaints"
      size="lg"
      footer={
        <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:justify-end">
          <Button
            type="button"
            variant="outline"
            disabled={busy}
            onClick={onClose}
          >
            Cancel
          </Button>
          <Button
            type="button"
            variant="outline"
            disabled={busy}
            loading={busy}
            onClick={() => void decide("recommend_only")}
          >
            Recommend existing only
          </Button>
          <Button
            type="button"
            variant="outline"
            disabled={busy || !effectiveSurviving}
            loading={busy}
            onClick={() => void decide("link_existing")}
          >
            Link to existing
          </Button>
          <Button
            type="button"
            disabled={busy}
            loading={busy}
            onClick={() => void decide("override")}
          >
            Override & create new
          </Button>
        </div>
      }
    >
      <div className="space-y-4 text-sm">
        <Alert
          tone="warning"
          title="Duplicate warning"
          description="Candidates matched Batch-1 policy. You may link or override with justification. Case create is not available in Batch 1."
        />

        {result?.degraded ? (
          <Alert
            tone="info"
            title="Degraded check"
            description={
              result.laterReviewWorkItemId
                ? `Duplicate check degraded. Later-review work item: ${result.laterReviewWorkItemId}`
                : "Duplicate check degraded; proceed carefully."
            }
          />
        ) : null}

        {localError ? (
          <Alert tone="danger" title="Decision blocked" description={localError} />
        ) : null}

        {candidates.length === 0 ? (
          <p className="text-ecmp-text-secondary">No candidate details returned.</p>
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
                  className="rounded border border-ecmp-border p-2 font-mono text-xs"
                >
                  <button
                    type="button"
                    className="w-full text-left hover:underline"
                    onClick={() => setSurvivingId(id)}
                    disabled={busy}
                  >
                    {number ?? id}
                    {score != null ? ` · score ${score}` : ""}
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
          label="Surviving complaint ID (for link)"
          value={survivingId || effectiveSurviving}
          onChange={(event) => setSurvivingId(event.target.value)}
          disabled={busy}
          hint="Click a candidate above or paste an Aggregate complaint ID"
        />

        <Textarea
          name="overrideJustification"
          id="overrideJustification"
          label="Override justification"
          rows={3}
          value={justification}
          onChange={(event) => setJustification(event.target.value)}
          disabled={busy}
          hint="Required for override (min. 20 characters)"
        />
      </div>
    </Modal>
  );
}
