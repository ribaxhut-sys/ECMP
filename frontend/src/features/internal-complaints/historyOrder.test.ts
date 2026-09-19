import { describe, expect, it } from "vitest";
import { sortInternalHistoryNewestFirst } from "./types";

describe("sortInternalHistoryNewestFirst", () => {
  it("puts later occurredAt first", () => {
    const sorted = sortInternalHistoryNewestFirst([
      { eventType: "RECEIVED", occurredAt: "2026-09-02T02:00:00.000Z" },
      { eventType: "RESOLUTION", occurredAt: "2026-09-02T02:00:00.001Z" },
    ]);
    expect(sorted.map((e) => e.eventType)).toEqual(["RESOLUTION", "RECEIVED"]);
  });

  it("keeps later-appended event first when timestamps match", () => {
    const sorted = sortInternalHistoryNewestFirst([
      { eventType: "RECEIVED", occurredAt: "2026-09-02T02:00:00.000Z" },
      { eventType: "RESOLUTION", occurredAt: "2026-09-02T02:00:00.000Z" },
    ]);
    expect(sorted.map((e) => e.eventType)).toEqual(["RESOLUTION", "RECEIVED"]);
  });
});
