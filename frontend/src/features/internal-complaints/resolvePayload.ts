/** Machine sentinel — not shown to operators. Backend also defaults to this. */
export const INTERNAL_RESOLUTION_SENTINEL = "IC_DONE";

export type InternalResolveFieldError =
  | "resolutionSummaryRequiredError"
  | "commentRequiredError"
  | "rejectProposalReasonRequiredError";

export type InternalResolvePayloadAction = "PROPOSE" | "ACCEPT" | "REJECT";

export function buildInternalResolveRequest(input: {
  action: InternalResolvePayloadAction;
  summary: string;
  comment: string;
  rejectionReason?: string;
}):
  | {
      ok: true;
      body: {
        action: InternalResolvePayloadAction;
        comment: string;
        summary?: string;
        rejectionReason?: string;
        resolutionCode: typeof INTERNAL_RESOLUTION_SENTINEL;
      };
    }
  | { ok: false; error: InternalResolveFieldError } {
  const summary = input.summary.trim();
  const comment = input.comment.trim();
  if (input.action === "PROPOSE") {
    if (!summary) return { ok: false, error: "resolutionSummaryRequiredError" };
    if (!comment) return { ok: false, error: "commentRequiredError" };
    return {
      ok: true,
      body: {
        action: "PROPOSE",
        comment,
        summary,
        resolutionCode: INTERNAL_RESOLUTION_SENTINEL,
      },
    };
  }
  if (input.action === "REJECT") {
    const rejectionReason = (input.rejectionReason ?? comment).trim();
    if (!rejectionReason) {
      return { ok: false, error: "rejectProposalReasonRequiredError" };
    }
    return {
      ok: true,
      body: {
        action: "REJECT",
        comment: comment || rejectionReason,
        rejectionReason,
        resolutionCode: INTERNAL_RESOLUTION_SENTINEL,
      },
    };
  }
  return {
    ok: true,
    body: {
      action: "ACCEPT",
      comment: comment || "Usulan diterima",
      resolutionCode: INTERNAL_RESOLUTION_SENTINEL,
    },
  };
}
