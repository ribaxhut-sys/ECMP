import { describe, expect, it } from "vitest";
import {
  INTERNAL_ASSIGNMENT_STATUSES,
  INTERNAL_FOLLOW_UP_STATUSES,
  resolveQueueEmptyHint,
  siblingQueueCounts,
} from "./internalQueues";

describe("internalQueues", () => {
  it("counts receive / handling / closure slices", () => {
    expect(
      siblingQueueCounts([
        { status: "ASSIGNED" },
        { status: "CREATED" },
        { status: "IN_PROGRESS" },
        { status: "RESOLVED" },
        { status: "CLOSED" },
      ]),
    ).toEqual({ assignments: 2, followUp: 2, verification: 1 });
  });

  it("points follow-up empty state to Antrian terima when only CREATED tickets remain", () => {
    const hint = resolveQueueEmptyHint("followUp", {
      assignments: 1,
      followUp: 0,
      verification: 1,
    });
    expect(hint.descriptionKey).toBe("followUpEmptyWaitingReceive");
    expect(hint.descriptionValues).toEqual({ count: 1 });
    expect(hint.primaryHref).toBe("/internal/assignments");
    expect(hint.secondaryHref).toBe("/internal/verification");
  });

  it("points follow-up empty state to closure approval when only RESOLVED remains", () => {
    const hint = resolveQueueEmptyHint("followUp", {
      assignments: 0,
      followUp: 0,
      verification: 2,
    });
    expect(hint.descriptionKey).toBe("followUpEmptyWaitingVerification");
    expect(hint.primaryHref).toBe("/internal/verification");
  });

  it("lists Assigned and In-progress on the handling queue", () => {
    expect(INTERNAL_FOLLOW_UP_STATUSES).toEqual(["IN_PROGRESS", "ASSIGNED"]);
    expect(INTERNAL_ASSIGNMENT_STATUSES).toEqual(["ASSIGNED", "CREATED"]);
  });

  it("uses the generic list empty copy for reports", () => {
    expect(
      resolveQueueEmptyHint("reports", {
        assignments: 0,
        followUp: 0,
        verification: 0,
      }),
    ).toEqual({
      titleKey: "listEmpty",
      descriptionKey: "listEmptyDescription",
    });
  });
});
