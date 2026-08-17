/** Machine sentinel — not shown to operators. Backend also defaults to this. */
export const INTERNAL_RESOLUTION_SENTINEL = "IC_DONE";

export type InternalResolveFieldError =
  | "resolutionSummaryRequiredError"
  | "commentRequiredError";

export function buildInternalResolveRequest(input: {
  action: "PROPOSE" | "ACCEPT";
  summary: string;
  comment: string;
}):
  | {
      ok: true;
      body: {
        action: "PROPOSE" | "ACCEPT";
        comment: string;
        summary: string;
        resolutionCode: typeof INTERNAL_RESOLUTION_SENTINEL;
      };
    }
  | { ok: false; error: InternalResolveFieldError } {
  const summary = input.summary.trim();
  const comment = input.comment.trim();
  if (!summary) return { ok: false, error: "resolutionSummaryRequiredError" };
  if (!comment) return { ok: false, error: "commentRequiredError" };
  return {
    ok: true,
    body: {
      action: input.action,
      comment,
      summary,
      resolutionCode: INTERNAL_RESOLUTION_SENTINEL,
    },
  };
}
