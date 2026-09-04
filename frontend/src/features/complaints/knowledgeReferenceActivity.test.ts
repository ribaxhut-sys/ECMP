import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { Announcement, Attachment, Knowledge } from "@/lib/api/types";

const fetchKnowledge = vi.fn();
const fetchAnnouncement = vi.fn();
const fetchAttachment = vi.fn();

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchKnowledge: (...args: unknown[]) => fetchKnowledge(...args),
    fetchAnnouncement: (...args: unknown[]) => fetchAnnouncement(...args),
    fetchAttachment: (...args: unknown[]) => fetchAttachment(...args),
  };
});

import {
  isAnnouncementReferenceActive,
  isAttachmentReferenceActive,
  isKnowledgeReferenceActive,
  resolveMentionReferenceMeta,
} from "./knowledgeReferenceActivity";

const labels = {
  knowledgeType: (type: string) => `Jenis:${type}`,
  announcement: "Pengumuman",
  attachment: "Lampiran",
};

describe("isKnowledgeReferenceActive", () => {
  const now = new Date("2026-08-11T00:00:00Z");

  it("returns true for ACTIVE without effective bounds", () => {
    expect(
      isKnowledgeReferenceActive(
        { status: "ACTIVE", effectiveFrom: null, effectiveTo: null },
        now,
      ),
    ).toBe(true);
  });

  it("returns false for ARCHIVED / DRAFT", () => {
    expect(
      isKnowledgeReferenceActive(
        { status: "ARCHIVED", effectiveFrom: null, effectiveTo: null },
        now,
      ),
    ).toBe(false);
    expect(
      isKnowledgeReferenceActive(
        { status: "DRAFT", effectiveFrom: null, effectiveTo: null },
        now,
      ),
    ).toBe(false);
  });

  it("returns false when outside the effective window", () => {
    expect(
      isKnowledgeReferenceActive(
        {
          status: "ACTIVE",
          effectiveFrom: null,
          effectiveTo: "2026-01-01T00:00:00Z",
        },
        now,
      ),
    ).toBe(false);
    expect(
      isKnowledgeReferenceActive(
        {
          status: "ACTIVE",
          effectiveFrom: "2026-12-01T00:00:00Z",
          effectiveTo: null,
        },
        now,
      ),
    ).toBe(false);
  });
});

describe("isAnnouncementReferenceActive", () => {
  it("returns true only for PUBLISHED effective status", () => {
    expect(isAnnouncementReferenceActive({ effectiveStatus: "PUBLISHED" })).toBe(
      true,
    );
    expect(isAnnouncementReferenceActive({ effectiveStatus: "EXPIRED" })).toBe(
      false,
    );
    expect(isAnnouncementReferenceActive({ effectiveStatus: "DRAFT" })).toBe(
      false,
    );
    expect(isAnnouncementReferenceActive({ effectiveStatus: "SCHEDULED" })).toBe(
      false,
    );
  });
});

describe("isAttachmentReferenceActive", () => {
  it("returns true only for AVAILABLE status", () => {
    expect(isAttachmentReferenceActive({ status: "AVAILABLE" })).toBe(true);
    expect(isAttachmentReferenceActive({ status: "DELETED" })).toBe(false);
    expect(isAttachmentReferenceActive({ status: "UPLOADED" })).toBe(false);
    expect(isAttachmentReferenceActive({ status: "FAILED" })).toBe(false);
  });
});

describe("resolveMentionReferenceMeta", () => {
  beforeEach(() => {
    fetchKnowledge.mockReset();
    fetchAnnouncement.mockReset();
    fetchAttachment.mockReset();
  });
  afterEach(() => vi.clearAllMocks());

  it("resolves a knowledge reference via fetchKnowledge", async () => {
    fetchKnowledge.mockResolvedValue({
      data: {
        status: "ACTIVE",
        effectiveFrom: null,
        effectiveTo: null,
        knowledgeType: "SOP",
      } satisfies Partial<Knowledge>,
    });
    const meta = await resolveMentionReferenceMeta(
      "knowledge",
      "k1",
      labels,
    );
    expect(fetchKnowledge).toHaveBeenCalledWith("k1");
    expect(meta).toEqual({ active: true, typeLabel: "Jenis:SOP" });
  });

  it("resolves an announcement reference via fetchAnnouncement", async () => {
    fetchAnnouncement.mockResolvedValue({
      data: { effectiveStatus: "EXPIRED" } satisfies Partial<Announcement>,
    });
    const meta = await resolveMentionReferenceMeta(
      "announcement",
      "a1",
      labels,
    );
    expect(fetchAnnouncement).toHaveBeenCalledWith("a1");
    expect(meta).toEqual({ active: false, typeLabel: "Pengumuman" });
  });

  it("resolves an attachment reference via fetchAttachment", async () => {
    fetchAttachment.mockResolvedValue({
      data: { status: "AVAILABLE" } satisfies Partial<Attachment>,
    });
    const meta = await resolveMentionReferenceMeta(
      "attachment",
      "f1",
      labels,
    );
    expect(fetchAttachment).toHaveBeenCalledWith("f1");
    expect(meta).toEqual({ active: true, typeLabel: "Lampiran" });
  });

  it("propagates a rejected fetch so the caller can degrade to inactive", async () => {
    fetchAttachment.mockRejectedValue(new Error("404"));
    await expect(
      resolveMentionReferenceMeta("attachment", "missing", labels),
    ).rejects.toThrow("404");
  });
});
