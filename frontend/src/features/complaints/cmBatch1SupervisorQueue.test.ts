import { describe, expect, it } from "vitest";
import {
  CM_BATCH1_AGING_UI_FIELDS,
  CM_BATCH1_LATER_REVIEW_UI_FIELDS,
  CM_BATCH1_SUPERVISOR_QUEUE_LIMIT_MAX,
  clampCmBatch1SupervisorQueueLimit,
  cmBatch1LaterReviewReasonIsUnknown,
  cmBatch1LaterReviewReasonLabel,
  cmBatch1LaterReviewReasonTone,
  cmBatch1SupervisorStatusLabel,
  isCmBatch1AgingPastThreshold,
  isKnownCmBatch1LaterReviewReason,
} from "./cmBatch1SupervisorQueue";

describe("cmBatch1SupervisorQueue contract helpers", () => {
  it("keeps known reasons verbatim and tones mapped without rewrite", () => {
    expect(isKnownCmBatch1LaterReviewReason("duplicate_check_degraded")).toBe(
      true,
    );
    expect(cmBatch1LaterReviewReasonLabel("duplicate_check_degraded")).toBe(
      "duplicate_check_degraded",
    );
    expect(cmBatch1LaterReviewReasonTone("duplicate_check_degraded")).toBe(
      "danger",
    );
    expect(cmBatch1LaterReviewReasonLabel("attachment_bind_failed")).toBe(
      "attachment_bind_failed",
    );
    expect(cmBatch1LaterReviewReasonTone("attachment_bind_failed")).toBe(
      "warning",
    );
    expect(cmBatch1LaterReviewReasonIsUnknown("duplicate_check_degraded")).toBe(
      false,
    );
  });

  it("displays unknown reason safely without remapping status meaning", () => {
    expect(isKnownCmBatch1LaterReviewReason("future_enrichment_v2")).toBe(
      false,
    );
    expect(cmBatch1LaterReviewReasonLabel("future_enrichment_v2")).toBe(
      "future_enrichment_v2",
    );
    expect(cmBatch1LaterReviewReasonTone("future_enrichment_v2")).toBe(
      "neutral",
    );
    expect(cmBatch1LaterReviewReasonIsUnknown("future_enrichment_v2")).toBe(
      true,
    );
    expect(cmBatch1LaterReviewReasonLabel("   ")).toBe("(empty reason)");
  });

  it("pass-through status labels", () => {
    expect(cmBatch1SupervisorStatusLabel("OPEN")).toBe("OPEN");
    expect(cmBatch1SupervisorStatusLabel("REGISTERED")).toBe("REGISTERED");
    expect(cmBatch1SupervisorStatusLabel("")).toBe("—");
  });

  it("aging threshold boundary uses inclusive ageHours >= threshold", () => {
    expect(isCmBatch1AgingPastThreshold(24, 24)).toBe(true);
    expect(isCmBatch1AgingPastThreshold(23.99, 24)).toBe(false);
    expect(isCmBatch1AgingPastThreshold(48, 24)).toBe(true);
  });

  it("documents UI field sets from API-513 (no invented columns)", () => {
    expect([...CM_BATCH1_LATER_REVIEW_UI_FIELDS]).toEqual([
      "workItemId",
      "customerId",
      "complaintId",
      "reason",
      "status",
      "createdAt",
      "ageHours",
    ]);
    expect([...CM_BATCH1_AGING_UI_FIELDS]).toContain("caseCreated");
    expect(clampCmBatch1SupervisorQueueLimit(9999)).toBe(
      CM_BATCH1_SUPERVISOR_QUEUE_LIMIT_MAX,
    );
    expect(clampCmBatch1SupervisorQueueLimit(0)).toBe(1);
  });
});
