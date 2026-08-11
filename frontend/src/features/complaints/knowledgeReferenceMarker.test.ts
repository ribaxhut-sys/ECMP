import { describe, expect, it } from "vitest";
import {
  buildKnowledgeMarker,
  detectMentionQuery,
  extractKnowledgeIds,
  insertKnowledgeMarker,
  parseKnowledgeReferenceSegments,
} from "./knowledgeReferenceMarker";

const KID_A = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa";
const KID_B = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb";

describe("buildKnowledgeMarker", () => {
  it("builds the @[title](knowledge:id) marker", () => {
    expect(buildKnowledgeMarker("SOP Penanganan Pengaduan v2.1", KID_A)).toBe(
      `@[SOP Penanganan Pengaduan v2.1](knowledge:${KID_A})`,
    );
  });

  it("strips brackets/parens from the title snapshot (cosmetic only)", () => {
    const marker = buildKnowledgeMarker("SOP [Draft] (final)", KID_A);
    expect(marker).toBe(`@[SOP Draft final](knowledge:${KID_A})`);
  });

  it("collapses internal whitespace", () => {
    const marker = buildKnowledgeMarker("SOP   Pengaduan\n\nRevisi", KID_A);
    expect(marker).toBe(`@[SOP Pengaduan Revisi](knowledge:${KID_A})`);
  });
});

describe("parseKnowledgeReferenceSegments", () => {
  it("returns a single text segment when there is no marker", () => {
    expect(parseKnowledgeReferenceSegments("Penyelesaian tanpa rujukan.")).toEqual([
      { type: "text", value: "Penyelesaian tanpa rujukan." },
    ]);
  });

  it("splits text around a single reference", () => {
    const text = `Sesuai @[SOP Pengaduan](knowledge:${KID_A}).`;
    expect(parseKnowledgeReferenceSegments(text)).toEqual([
      { type: "text", value: "Sesuai " },
      { type: "reference", knowledgeId: KID_A, title: "SOP Pengaduan" },
      { type: "text", value: "." },
    ]);
  });

  it("handles multiple references in one text", () => {
    const text = `Berdasarkan @[SOP A](knowledge:${KID_A}) dan @[Peraturan B](knowledge:${KID_B}).`;
    const segments = parseKnowledgeReferenceSegments(text);
    const refs = segments.filter((s) => s.type === "reference");
    expect(refs).toHaveLength(2);
    expect(refs[0]).toEqual({ type: "reference", knowledgeId: KID_A, title: "SOP A" });
    expect(refs[1]).toEqual({
      type: "reference",
      knowledgeId: KID_B,
      title: "Peraturan B",
    });
  });

  it("degrades a malformed marker (bad id) to plain text", () => {
    const text = "Sesuai @[SOP Rusak](knowledge:not-a-uuid).";
    expect(parseKnowledgeReferenceSegments(text)).toEqual([
      { type: "text", value: text },
    ]);
  });

  it("allows an empty title snapshot", () => {
    const text = `@[](knowledge:${KID_A})`;
    expect(parseKnowledgeReferenceSegments(text)).toEqual([
      { type: "reference", knowledgeId: KID_A, title: "" },
    ]);
  });
});

describe("extractKnowledgeIds", () => {
  it("returns an empty array for plain text", () => {
    expect(extractKnowledgeIds("Tidak ada rujukan.")).toEqual([]);
  });

  it("de-duplicates repeated references, preserving first-seen order", () => {
    const text = `@[SOP A](knowledge:${KID_A}) ... @[SOP B](knowledge:${KID_B}) ... @[SOP A lagi](knowledge:${KID_A})`;
    expect(extractKnowledgeIds(text)).toEqual([KID_A, KID_B]);
  });
});

describe("detectMentionQuery", () => {
  it("detects a bare @ at the caret", () => {
    const text = "Penyelesaian sesuai @";
    expect(detectMentionQuery(text, text.length)).toEqual({
      start: text.length - 1,
      query: "",
    });
  });

  it("detects an in-progress query after @", () => {
    const text = "Penyelesaian sesuai @pengaduan";
    expect(detectMentionQuery(text, text.length)).toEqual({
      start: 20,
      query: "pengaduan",
    });
  });

  it("returns null when there is no @ before the caret", () => {
    expect(detectMentionQuery("Tidak ada mention di sini", 10)).toBeNull();
  });

  it("returns null once the query contains a space (mention abandoned)", () => {
    const text = "Penyelesaian sesuai @foo bar";
    expect(detectMentionQuery(text, text.length)).toBeNull();
  });

  it("returns null when the caret sits inside an already-inserted marker", () => {
    const text = `Sesuai @[SOP Pengaduan](knowledge:${KID_A}) selesai`;
    // Caret in the middle of the marker's title text.
    expect(detectMentionQuery(text, 15)).toBeNull();
  });

  it("requires @ to start at a word boundary (not mid-word/email-like)", () => {
    expect(detectMentionQuery("user@example", 12)).toBeNull();
  });
});

describe("insertKnowledgeMarker", () => {
  it("replaces the @query span with the marker, keeping the existing trailing space (no double space)", () => {
    const text = "Penyelesaian sesuai @pengaduan lanjutan.";
    const mention = { start: 20, query: "pengaduan" };
    const caret = 30; // end of "@pengaduan", right before the existing space
    const result = insertKnowledgeMarker(text, mention, caret, "SOP Pengaduan", KID_A);
    expect(result.text).toBe(
      `Penyelesaian sesuai @[SOP Pengaduan](knowledge:${KID_A}) lanjutan.`,
    );
    expect(result.caret).toBe(20 + `@[SOP Pengaduan](knowledge:${KID_A})`.length);
  });

  it("inserts at a bare @ with no query text yet, adding a trailing space at end of text", () => {
    const text = "Sesuai @";
    const mention = { start: 7, query: "" };
    const result = insertKnowledgeMarker(text, mention, 8, "SOP", KID_A);
    expect(result.text).toBe(`Sesuai @[SOP](knowledge:${KID_A}) `);
  });

  it("does not produce a double space when text already continues right after the query", () => {
    const text = "Sesuai @pengaduan!";
    const mention = { start: 7, query: "pengaduan" };
    const caret = 17; // right before "!"
    const result = insertKnowledgeMarker(text, mention, caret, "SOP", KID_A);
    expect(result.text).toBe(`Sesuai @[SOP](knowledge:${KID_A}) !`);
  });
});
