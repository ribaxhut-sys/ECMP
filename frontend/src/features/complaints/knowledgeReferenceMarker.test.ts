import { describe, expect, it } from "vitest";
import {
  buildMentionMarker,
  detectMentionQuery,
  extractMentionRefs,
  insertMentionMarker,
  parseKnowledgeReferenceSegments,
} from "./knowledgeReferenceMarker";

const KID_A = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa";
const KID_B = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb";
const AID_A = "cccccccc-cccc-4ccc-8ccc-cccccccccccc";
const FID_A = "dddddddd-dddd-4ddd-8ddd-dddddddddddd";

describe("buildMentionMarker", () => {
  it("builds the @[title](knowledge:id) marker", () => {
    expect(
      buildMentionMarker("knowledge", "SOP Penanganan Pengaduan v2.1", KID_A),
    ).toBe(`@[SOP Penanganan Pengaduan v2.1](knowledge:${KID_A})`);
  });

  it("builds the @[title](announcement:id) marker", () => {
    expect(buildMentionMarker("announcement", "Libur Nasional", AID_A)).toBe(
      `@[Libur Nasional](announcement:${AID_A})`,
    );
  });

  it("builds the @[title](attachment:id) marker", () => {
    expect(buildMentionMarker("attachment", "Formulir Klaim.pdf", FID_A)).toBe(
      `@[Formulir Klaim.pdf](attachment:${FID_A})`,
    );
  });

  it("strips brackets/parens from the title snapshot (cosmetic only)", () => {
    const marker = buildMentionMarker("knowledge", "SOP [Draft] (final)", KID_A);
    expect(marker).toBe(`@[SOP Draft final](knowledge:${KID_A})`);
  });

  it("collapses internal whitespace", () => {
    const marker = buildMentionMarker(
      "knowledge",
      "SOP   Pengaduan\n\nRevisi",
      KID_A,
    );
    expect(marker).toBe(`@[SOP Pengaduan Revisi](knowledge:${KID_A})`);
  });
});

describe("parseKnowledgeReferenceSegments", () => {
  it("returns a single text segment when there is no marker", () => {
    expect(parseKnowledgeReferenceSegments("Penyelesaian tanpa rujukan.")).toEqual([
      { type: "text", value: "Penyelesaian tanpa rujukan." },
    ]);
  });

  it("splits text around a single knowledge reference", () => {
    const text = `Sesuai @[SOP Pengaduan](knowledge:${KID_A}).`;
    expect(parseKnowledgeReferenceSegments(text)).toEqual([
      { type: "text", value: "Sesuai " },
      { type: "reference", kind: "knowledge", id: KID_A, title: "SOP Pengaduan" },
      { type: "text", value: "." },
    ]);
  });

  it("parses announcement and attachment references", () => {
    const text = `Lihat @[Libur Nasional](announcement:${AID_A}) dan @[Formulir.pdf](attachment:${FID_A}).`;
    const segments = parseKnowledgeReferenceSegments(text);
    const refs = segments.filter((s) => s.type === "reference");
    expect(refs).toEqual([
      { type: "reference", kind: "announcement", id: AID_A, title: "Libur Nasional" },
      { type: "reference", kind: "attachment", id: FID_A, title: "Formulir.pdf" },
    ]);
  });

  it("handles multiple references of mixed kinds in one text", () => {
    const text = `Berdasarkan @[SOP A](knowledge:${KID_A}) dan @[Peraturan B](knowledge:${KID_B}).`;
    const segments = parseKnowledgeReferenceSegments(text);
    const refs = segments.filter((s) => s.type === "reference");
    expect(refs).toHaveLength(2);
    expect(refs[0]).toEqual({
      type: "reference",
      kind: "knowledge",
      id: KID_A,
      title: "SOP A",
    });
    expect(refs[1]).toEqual({
      type: "reference",
      kind: "knowledge",
      id: KID_B,
      title: "Peraturan B",
    });
  });

  it("degrades a malformed marker (bad id) to plain text", () => {
    const text = "Sesuai @[SOP Rusak](knowledge:not-a-uuid).";
    expect(parseKnowledgeReferenceSegments(text)).toEqual([
      { type: "text", value: text },
    ]);
  });

  it("degrades an unknown kind to plain text", () => {
    const text = `Sesuai @[X](unknown:${KID_A}).`;
    expect(parseKnowledgeReferenceSegments(text)).toEqual([
      { type: "text", value: text },
    ]);
  });

  it("allows an empty title snapshot", () => {
    const text = `@[](knowledge:${KID_A})`;
    expect(parseKnowledgeReferenceSegments(text)).toEqual([
      { type: "reference", kind: "knowledge", id: KID_A, title: "" },
    ]);
  });
});

describe("extractMentionRefs", () => {
  it("returns an empty array for plain text", () => {
    expect(extractMentionRefs("Tidak ada rujukan.")).toEqual([]);
  });

  it("de-duplicates repeated references by kind+id, preserving first-seen order", () => {
    const text = `@[SOP A](knowledge:${KID_A}) ... @[Libur](announcement:${AID_A}) ... @[SOP A lagi](knowledge:${KID_A})`;
    expect(extractMentionRefs(text)).toEqual([
      { kind: "knowledge", id: KID_A },
      { kind: "announcement", id: AID_A },
    ]);
  });

  it("does not collapse the same id across different kinds", () => {
    const text = `@[A](knowledge:${KID_A}) @[B](announcement:${KID_A})`;
    expect(extractMentionRefs(text)).toEqual([
      { kind: "knowledge", id: KID_A },
      { kind: "announcement", id: KID_A },
    ]);
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

describe("insertMentionMarker", () => {
  it("replaces the @query span with the marker, keeping the existing trailing space (no double space)", () => {
    const text = "Penyelesaian sesuai @pengaduan lanjutan.";
    const mention = { start: 20, query: "pengaduan" };
    const caret = 30; // end of "@pengaduan", right before the existing space
    const result = insertMentionMarker(
      text,
      mention,
      caret,
      "knowledge",
      "SOP Pengaduan",
      KID_A,
    );
    expect(result.text).toBe(
      `Penyelesaian sesuai @[SOP Pengaduan](knowledge:${KID_A}) lanjutan.`,
    );
    expect(result.caret).toBe(20 + `@[SOP Pengaduan](knowledge:${KID_A})`.length);
  });

  it("inserts an announcement marker at a bare @ with no query text yet, adding a trailing space at end of text", () => {
    const text = "Sesuai @";
    const mention = { start: 7, query: "" };
    const result = insertMentionMarker(
      text,
      mention,
      8,
      "announcement",
      "Libur Nasional",
      AID_A,
    );
    expect(result.text).toBe(`Sesuai @[Libur Nasional](announcement:${AID_A}) `);
  });

  it("does not produce a double space when text already continues right after the query", () => {
    const text = "Sesuai @formulir!";
    const mention = { start: 7, query: "formulir" };
    const caret = 16; // right before "!"
    const result = insertMentionMarker(
      text,
      mention,
      caret,
      "attachment",
      "Formulir.pdf",
      FID_A,
    );
    expect(result.text).toBe(`Sesuai @[Formulir.pdf](attachment:${FID_A}) !`);
  });
});
