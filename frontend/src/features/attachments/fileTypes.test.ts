import { describe, expect, it } from "vitest";
import {
  fileTypeLabel,
  formatFileSize,
  getPreviewKind,
  isAllowedInternalComplaintFile,
  normalizeExtension,
} from "./fileTypes";

describe("normalizeExtension", () => {
  it("prefers metadata extension and adds leading dot", () => {
    expect(normalizeExtension("png", "a.txt")).toBe(".png");
    expect(normalizeExtension(".PDF", "a.txt")).toBe(".pdf");
  });

  it("falls back to filename extension", () => {
    expect(normalizeExtension(null, "report.PDF")).toBe(".pdf");
    expect(normalizeExtension("", "noext")).toBe("");
  });
});

describe("getPreviewKind", () => {
  it("classifies pdf and images", () => {
    expect(getPreviewKind("application/pdf", null, "a.bin")).toBe("pdf");
    expect(getPreviewKind("image/png", null, "a.bin")).toBe("image");
    expect(getPreviewKind("text/plain", ".png", "a.txt")).toBe("image");
    expect(getPreviewKind("text/plain", null, "a.txt")).toBe("unsupported");
    expect(getPreviewKind("application/zip", ".zip", "bukti.zip")).toBe(
      "unsupported",
    );
  });
});

describe("isAllowedInternalComplaintFile", () => {
  it("allows images and zip, rejects pdf", () => {
    const png = new File(["x"], "a.png", { type: "image/png" });
    const zip = new File(["PK"], "a.zip", { type: "application/zip" });
    const pdf = new File(["%PDF"], "a.pdf", { type: "application/pdf" });
    expect(isAllowedInternalComplaintFile(png)).toBe(true);
    expect(isAllowedInternalComplaintFile(zip)).toBe(true);
    expect(isAllowedInternalComplaintFile(pdf)).toBe(false);
  });
});

describe("formatFileSize", () => {
  it("formats bytes/kb/mb and guards invalid input", () => {
    expect(formatFileSize(512)).toBe("512 B");
    expect(formatFileSize(2048)).toBe("2.0 KB");
    expect(formatFileSize(-1)).toBe("—");
  });
});

describe("fileTypeLabel", () => {
  it("prefers extension then mime subtype", () => {
    expect(fileTypeLabel("image/png", ".png", "a.png")).toBe("PNG");
    expect(fileTypeLabel("application/pdf", null, "a")).toBe("PDF");
    expect(fileTypeLabel("", null, "a")).toBe("FILE");
  });
});
