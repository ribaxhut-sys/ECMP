import { describe, expect, it } from "vitest";
import {
  cmBatch1AttachmentListLabel,
  formatCmBatch1AttachmentBytes,
  isCmBatch1AttachmentVoidable,
  normalizeCmBatch1VoidReason,
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
    expect(cmBatch1AttachmentListLabel(0)).toBe("No bound attachments");
    expect(cmBatch1AttachmentListLabel(1)).toBe("1 attachment");
    expect(cmBatch1AttachmentListLabel(3)).toBe("3 attachments");
  });
});
