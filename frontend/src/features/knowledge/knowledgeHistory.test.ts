import { describe, expect, it } from "vitest";
import {
  knowledgeHistoryDiffFields,
  knowledgeHistoryEventIcon,
  knowledgeHistoryEventLabelKey,
} from "./knowledgeHistory";

describe("knowledgeHistoryEventLabelKey", () => {
  it("maps known event types to their i18n key", () => {
    expect(knowledgeHistoryEventLabelKey("KnowledgeCreated")).toBe("historyEventCreated");
    expect(knowledgeHistoryEventLabelKey("KnowledgeUpdated")).toBe("historyEventUpdated");
    expect(knowledgeHistoryEventLabelKey("KnowledgePublished")).toBe("historyEventPublished");
    expect(knowledgeHistoryEventLabelKey("KnowledgeFileReplaced")).toBe(
      "historyEventFileReplaced",
    );
  });

  it("falls back to a generic label for an unrecognized event type", () => {
    expect(knowledgeHistoryEventLabelKey("SomethingUnknown")).toBe("historyEventOther");
  });
});

describe("knowledgeHistoryEventIcon", () => {
  it("returns a distinct glyph per known event type", () => {
    expect(knowledgeHistoryEventIcon("KnowledgeCreated")).toBe("+");
    expect(knowledgeHistoryEventIcon("KnowledgeDeleted")).toBe("✕");
  });
});

describe("knowledgeHistoryDiffFields", () => {
  it("returns only the fields present in oldValues, in form order", () => {
    const diffs = knowledgeHistoryDiffFields({
      oldValues: { summary: "Lama", effectiveFrom: null },
      newValues: { summary: "Baru", effectiveFrom: "2026-08-01T00:00:00Z" },
    });
    expect(diffs).toEqual([
      { field: "summary", oldValue: "Lama", newValue: "Baru" },
      { field: "effectiveFrom", oldValue: null, newValue: "2026-08-01T00:00:00Z" },
    ]);
  });

  it("returns an empty list when there is nothing to diff", () => {
    expect(knowledgeHistoryDiffFields({ oldValues: null, newValues: null })).toEqual([]);
  });
});
