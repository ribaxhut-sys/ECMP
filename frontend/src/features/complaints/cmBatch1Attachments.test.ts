import { afterEach, describe, expect, it, vi } from "vitest";
import {
  cmBatch1AttachmentListLabel,
  cmBatch1VoidTargetId,
  formatCmBatch1AttachmentBytes,
  isCmBatch1AttachmentVoidable,
  isSameCmBatch1Attachment,
  normalizeCmBatch1Attachment,
  normalizeCmBatch1VoidReason,
  openBlankAttachmentTab,
  pickCmBatch1UploadFiles,
  showAttachmentInTab,
  CM_BATCH1_MAX_MULTI_UPLOAD,
} from "./cmBatch1Attachments";

describe("isCmBatch1AttachmentVoidable", () => {
  it("allows staged/active/transferred", () => {
    expect(isCmBatch1AttachmentVoidable("STAGED")).toBe(true);
    expect(isCmBatch1AttachmentVoidable("ACTIVE")).toBe(true);
    expect(isCmBatch1AttachmentVoidable("TRANSFERRED")).toBe(true);
  });

  it("rejects void and superseded", () => {
    expect(isCmBatch1AttachmentVoidable("VOID")).toBe(false);
    expect(isCmBatch1AttachmentVoidable("SUPERSEDED")).toBe(false);
  });
});

describe("normalizeCmBatch1VoidReason", () => {
  it("trims and rejects empty", () => {
    expect(normalizeCmBatch1VoidReason("  customer retract  ")).toBe(
      "customer retract",
    );
    expect(normalizeCmBatch1VoidReason("   ")).toBeNull();
    expect(normalizeCmBatch1VoidReason(null)).toBeNull();
  });
});

describe("formatCmBatch1AttachmentBytes", () => {
  it("formats sizes", () => {
    expect(formatCmBatch1AttachmentBytes(500)).toBe("500 B");
    expect(formatCmBatch1AttachmentBytes(2048)).toBe("2.0 KB");
    expect(formatCmBatch1AttachmentBytes(2 * 1024 * 1024)).toBe("2.0 MB");
    expect(formatCmBatch1AttachmentBytes(Number.NaN)).toBe("—");
  });
});

describe("cmBatch1AttachmentListLabel", () => {
  it("labels counts", () => {
    expect(cmBatch1AttachmentListLabel(0)).toBe("attachmentCountNone");
    expect(cmBatch1AttachmentListLabel(1)).toBe("attachmentCountOne");
    expect(cmBatch1AttachmentListLabel(3)).toBe("attachmentCountMany");
  });
});

describe("isSameCmBatch1Attachment / void target", () => {
  it("matches batch or platform id", () => {
    const item = {
      attachmentId: "batch-1",
      platformAttachmentId: "plat-1",
    };
    expect(isSameCmBatch1Attachment(item, "batch-1")).toBe(true);
    expect(isSameCmBatch1Attachment(item, "plat-1")).toBe(true);
    expect(isSameCmBatch1Attachment(item, "other")).toBe(false);
    expect(cmBatch1VoidTargetId(item)).toBe("batch-1");
  });

  it("reads snake_case ids", () => {
    const item = {
      attachment_id: "batch-2",
      platform_attachment_id: "plat-2",
    };
    expect(cmBatch1VoidTargetId(item)).toBe("batch-2");
    expect(isSameCmBatch1Attachment(item, "plat-2")).toBe(true);
  });
});

describe("normalizeCmBatch1Attachment", () => {
  it("maps snake_case upload payloads", () => {
    const normalized = normalizeCmBatch1Attachment({
      attachment_id: "a1",
      platform_attachment_id: "p1",
      status: "STAGED",
      classification: "customer_evidence",
      original_name: "x.png",
      mime_type: "image/png",
      size_bytes: 9,
      checksum_sha256: "z",
      created_at: "2026-08-08T00:00:00Z",
    });
    expect(normalized.attachmentId).toBe("a1");
    expect(normalized.platformAttachmentId).toBe("p1");
    expect(normalized.originalName).toBe("x.png");
    expect(normalized.sizeBytes).toBe(9);
  });
});

describe("pickCmBatch1UploadFiles", () => {
  function asFileList(files: File[]): FileList {
    const list = {
      length: files.length,
      item: (index: number) => files[index] ?? null,
      [Symbol.iterator]: files[Symbol.iterator].bind(files),
    } as FileList & Record<number, File>;
    files.forEach((file, index) => {
      list[index] = file;
    });
    return list;
  }

  it("returns all files when under the cap", () => {
    const result = pickCmBatch1UploadFiles(
      asFileList([
        new File(["a"], "a.png", { type: "image/png" }),
        new File(["b"], "b.png", { type: "image/png" }),
      ]),
    );
    expect(result.files).toHaveLength(2);
    expect(result.truncated).toBe(false);
  });

  it("truncates above the multi-upload cap", () => {
    const files = Array.from(
      { length: CM_BATCH1_MAX_MULTI_UPLOAD + 3 },
      (_, i) => new File([String(i)], `f${i}.txt`, { type: "text/plain" }),
    );
    const result = pickCmBatch1UploadFiles(asFileList(files));
    expect(result.files).toHaveLength(CM_BATCH1_MAX_MULTI_UPLOAD);
    expect(result.truncated).toBe(true);
  });
});

describe("openBlankAttachmentTab", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns the window and clears opener (no noopener false-null)", () => {
    const preview = { opener: window as unknown as Window, location: { replace: vi.fn(), href: "" } };
    const open = vi.fn(() => preview);
    vi.stubGlobal("open", open);

    const tab = openBlankAttachmentTab();
    expect(open).toHaveBeenCalledWith("about:blank", "_blank");
    expect(tab).toBe(preview);
    expect(preview.opener).toBeNull();
  });

  it("returns null when the browser blocks the tab", () => {
    vi.stubGlobal("open", vi.fn(() => null));
    expect(openBlankAttachmentTab()).toBeNull();
  });
});

describe("showAttachmentInTab", () => {
  it("uses location.replace", () => {
    const replace = vi.fn();
    const tab = {
      location: { replace, href: "" },
    } as unknown as Window;
    showAttachmentInTab(tab, "blob:test");
    expect(replace).toHaveBeenCalledWith("blob:test");
  });
});
