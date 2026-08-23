import { describe, expect, it } from "vitest";
import type { Knowledge } from "@/lib/api/types";
import {
  createEmptyKnowledgeForm,
  knowledgeFormFromExisting,
  toKnowledgeCreateRequest,
  toKnowledgeUpdateRequest,
  validateKnowledgeForm,
} from "./knowledgeForm";

describe("createEmptyKnowledgeForm", () => {
  it("defaults to SOP type with no dates", () => {
    const values = createEmptyKnowledgeForm();
    expect(values.knowledgeType).toBe("SOP");
    expect(values.effectiveFrom).toBe("");
    expect(values.effectiveTo).toBe("");
  });
});

describe("validateKnowledgeForm", () => {
  it("requires a title", () => {
    const errors = validateKnowledgeForm({
      ...createEmptyKnowledgeForm(),
      title: "   ",
    });
    expect(errors.title).toBe("required");
  });

  it("rejects a title over 200 characters", () => {
    const errors = validateKnowledgeForm({
      ...createEmptyKnowledgeForm(),
      title: "a".repeat(201),
    });
    expect(errors.title).toBe("knowledgeTitleMax");
  });

  it("accepts a well-formed form with no dates", () => {
    const errors = validateKnowledgeForm({
      ...createEmptyKnowledgeForm(),
      title: "SOP Penanganan Pengaduan",
    });
    expect(errors).toEqual({});
  });

  it("rejects an unparsable effectiveFrom date", () => {
    const errors = validateKnowledgeForm({
      ...createEmptyKnowledgeForm(),
      title: "Judul",
      effectiveFrom: "not-a-date",
    });
    expect(errors.effectiveFrom).toBe("knowledgeEffectiveFromInvalid");
  });

  it("rejects an unparsable effectiveTo date", () => {
    const errors = validateKnowledgeForm({
      ...createEmptyKnowledgeForm(),
      title: "Judul",
      effectiveTo: "not-a-date",
    });
    expect(errors.effectiveTo).toBe("knowledgeEffectiveToInvalid");
  });

  it("rejects effectiveTo that is not after effectiveFrom", () => {
    const errors = validateKnowledgeForm({
      ...createEmptyKnowledgeForm(),
      title: "Judul",
      effectiveFrom: "2026-12-31T12:00",
      effectiveTo: "2026-12-31T11:00",
    });
    expect(errors.effectiveTo).toBe("knowledgeEffectiveToBeforeFrom");
  });
});

describe("toKnowledgeCreateRequest", () => {
  it("trims title and converts blank optional fields to null", () => {
    const request = toKnowledgeCreateRequest({
      ...createEmptyKnowledgeForm(),
      title: "  SOP Penanganan Pengaduan  ",
      knowledgeType: "SOP",
    });
    expect(request.title).toBe("SOP Penanganan Pengaduan");
    expect(request.documentNumber).toBeNull();
    expect(request.summary).toBeNull();
    expect(request.versionLabel).toBeNull();
    expect(request.effectiveFrom).toBeNull();
    expect(request.effectiveTo).toBeNull();
    expect(request.supersedesKnowledgeId).toBeNull();
  });

  it("passes supersedesKnowledgeId through when provided", () => {
    const request = toKnowledgeCreateRequest(
      { ...createEmptyKnowledgeForm(), title: "SOP v2" },
      { supersedesKnowledgeId: "11111111-1111-1111-1111-111111111111" },
    );
    expect(request.supersedesKnowledgeId).toBe(
      "11111111-1111-1111-1111-111111111111",
    );
  });

  it("converts a datetime-local effectiveFrom to an ISO string", () => {
    const request = toKnowledgeCreateRequest({
      ...createEmptyKnowledgeForm(),
      title: "Judul",
      effectiveFrom: "2026-12-31T23:59",
    });
    expect(request.effectiveFrom).not.toBeNull();
    expect(new Date(request.effectiveFrom as string).getUTCFullYear()).toBe(2026);
  });
});

describe("toKnowledgeUpdateRequest", () => {
  it("never includes supersedesKnowledgeId (immutable after create)", () => {
    const request = toKnowledgeUpdateRequest({
      ...createEmptyKnowledgeForm(),
      title: "Judul",
    });
    expect(request).not.toHaveProperty("supersedesKnowledgeId");
  });
});

describe("knowledgeFormFromExisting", () => {
  const base: Knowledge = {
    id: "k1",
    title: "SOP Penanganan Pengaduan",
    knowledgeType: "SOP",
    status: "ACTIVE",
    documentNumber: "SOP-001",
    summary: "Ringkasan",
    versionLabel: "2.1",
    effectiveFrom: null,
    effectiveTo: null,
    ownerOrgUnitId: "PUSAT",
    publishedAt: null,
    publishedBy: null,
    supersedesKnowledgeId: null,
    supersedesTitle: null,
    createdBy: null,
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedBy: null,
    updatedAt: "2026-01-01T00:00:00.000Z",
    editable: true,
    editableUntil: null,
    files: [],
  };

  it("round-trips a knowledge record with no effective window", () => {
    const values = knowledgeFormFromExisting(base);
    expect(values).toEqual({
      title: "SOP Penanganan Pengaduan",
      knowledgeType: "SOP",
      documentNumber: "SOP-001",
      summary: "Ringkasan",
      versionLabel: "2.1",
      effectiveFrom: "",
      effectiveTo: "",
    });
  });

  it("formats an ISO effectiveTo as a datetime-local value", () => {
    const values = knowledgeFormFromExisting({
      ...base,
      effectiveTo: "2026-12-31T23:59:00.000Z",
    });
    expect(values.effectiveTo).toMatch(/^2026-12-31T\d{2}:59$/);
  });

  it("falls back to empty strings for null optional fields", () => {
    const values = knowledgeFormFromExisting({
      ...base,
      documentNumber: null,
      summary: null,
      versionLabel: null,
    });
    expect(values.documentNumber).toBe("");
    expect(values.summary).toBe("");
    expect(values.versionLabel).toBe("");
  });
});
