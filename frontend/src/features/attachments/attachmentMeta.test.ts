import { describe, expect, it } from "vitest";
import { normalizeAttachmentMeta } from "./attachmentMeta";

describe("normalizeAttachmentMeta", () => {
  it("passes through the platform shape", () => {
    const meta = normalizeAttachmentMeta({
      id: "att-1",
      aggregateType: "Complaint",
      aggregateId: "cmp-1",
      fileName: "stored.docx",
      originalName: "Surat.docx",
      mimeType: "application/msword",
      extension: ".docx",
      sizeBytes: 10,
      checksumSha256: "abc",
      storageProvider: "local",
      uploadedBy: "user-1",
      uploadedAt: "2026-08-13T00:00:00Z",
      status: "AVAILABLE",
    });
    expect(meta?.id).toBe("att-1");
    expect(meta?.uploadedAt).toBe("2026-08-13T00:00:00Z");
  });

  it("maps the Batch 1 orchestration shape onto the platform fields", () => {
    const meta = normalizeAttachmentMeta({
      attachmentId: "b1-att-1",
      platformAttachmentId: "plat-1",
      status: "ACTIVE",
      classification: "customer_evidence",
      complaintId: "cmp-9",
      originalName: "Bukti.docx",
      mimeType:
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      sizeBytes: 4096,
      checksumSha256: "def",
      createdAt: "2026-08-14T01:00:00Z",
    });
    expect(meta?.id).toBe("plat-1");
    expect(meta?.aggregateId).toBe("cmp-9");
    expect(meta?.extension).toBeNull();
    expect(meta?.uploadedAt).toBe("2026-08-14T01:00:00Z");
  });

  it("rejects payloads without an id or file name", () => {
    expect(normalizeAttachmentMeta(null)).toBeNull();
    expect(normalizeAttachmentMeta({ originalName: "a.docx" })).toBeNull();
    expect(normalizeAttachmentMeta({ id: "att-1" })).toBeNull();
  });
});
