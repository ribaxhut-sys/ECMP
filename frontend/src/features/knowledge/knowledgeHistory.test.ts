import { describe, expect, it } from "vitest";
import {
  knowledgeHistoryDiffFields,
  knowledgeHistoryEventIcon,
  knowledgeHistoryEventLabelKey,
  knowledgeHistoryIsPostPublish,
} from "./knowledgeHistory";

describe("knowledgeHistoryEventLabelKey", () => {
  it("maps known event types to their i18n key", () => {
    expect(knowledgeHistoryEventLabelKey("KnowledgeCreated")).toBe("historyEventCreated");
    expect(knowledgeHistoryEventLabelKey("KnowledgeUpdated")).toBe("historyEventUpdated");
    expect(knowledgeHistoryEventLabelKey("KnowledgePublished")).toBe("historyEventPublished");
    expect(knowledgeHistoryEventLabelKey("KnowledgeFileReplaced")).toBe(
      "historyEventFileReplaced",
    );
    expect(knowledgeHistoryEventLabelKey("KnowledgeFilePrimaryChanged")).toBe(
      "historyEventFilePrimaryChanged",
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

describe("knowledgeHistoryIsPostPublish", () => {
  it("is true only when metadata.postPublish is exactly true (DEC-030)", () => {
    expect(knowledgeHistoryIsPostPublish({ metadata: { postPublish: true } })).toBe(true);
    expect(knowledgeHistoryIsPostPublish({ metadata: { postPublish: false } })).toBe(false);
    expect(knowledgeHistoryIsPostPublish({ metadata: null })).toBe(false);
    expect(knowledgeHistoryIsPostPublish({ metadata: { reason: "SET" } })).toBe(false);
  });
});
