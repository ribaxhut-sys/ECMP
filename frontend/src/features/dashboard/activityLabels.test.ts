import { describe, expect, it } from "vitest";
import { resolveActivityMeta } from "./activityLabels";

describe("resolveActivityMeta", () => {
  it("labels handling without falling back to generic update", () => {
    expect(resolveActivityMeta("complaint.handling_continued").labelKey).toBe(
      "activityHandlingContinued",
    );
    expect(resolveActivityMeta("complaint.handling_continued").badgeKey).toBe(
      "activityBadgeHandling",
    );
    expect(resolveActivityMeta("complaint.handling_taken_over").labelKey).toBe(
      "activityHandlingTakenOver",
    );
    expect(resolveActivityMeta("complaint.handling_taken_over").badgeKey).toBe(
      "activityBadgeHandling",
    );
  });

  it("labels HQ and case operations distinctly", () => {
    expect(resolveActivityMeta("complaint.hq_accepted").labelKey).toBe(
      "activityHqAccepted",
    );
    expect(resolveActivityMeta("complaint.hq_returned").labelKey).toBe(
      "activityHqReturned",
    );
    expect(resolveActivityMeta("complaint.escalation_cancelled").labelKey).toBe(
      "activityEscalationCancelled",
    );
    expect(resolveActivityMeta("complaint.case_created").labelKey).toBe(
      "activityCaseCreated",
    );
    expect(resolveActivityMeta("complaint.case_status_changed").labelKey).toBe(
      "activityCaseStatusChanged",
    );
    expect(resolveActivityMeta("complaint.other").labelKey).toBe("activityOther");
  });
});
