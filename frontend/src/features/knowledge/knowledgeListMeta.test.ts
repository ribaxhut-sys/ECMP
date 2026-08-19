import { describe, expect, it } from "vitest";
import {
  buildKnowledgeListMeta,
  pickKnowledgeDisplayFile,
} from "./knowledgeListMeta";
import type { KnowledgeFile } from "@/lib/api/types";

const labels = {
  status: "Aktif",
  effective: (date: string) => `berlaku ${date}`,
  uploaded: (date: string) => `unggah ${date}`,
  inactive: (date: string) => `nonaktif ${date}`,
  files: (count: number) => `${count} berkas`,
  emDash: "—",
};

function file(overrides: Partial<KnowledgeFile> = {}): KnowledgeFile {
  return {
    id: "a1111111-1111-1111-1111-111111111111",
    fileName: "sop.pdf",
    mimeType: "application/pdf",
    sizeBytes: 1024,
    role: "PRIMARY",
    createdAt: "2026-08-01T00:00:00Z",
    ...overrides,
  };
}

describe("pickKnowledgeDisplayFile", () => {
  it("returns null when there are no files", () => {
    expect(pickKnowledgeDisplayFile([])).toBeNull();
    expect(pickKnowledgeDisplayFile(undefined)).toBeNull();
  });

  it("prefers PRIMARY over other roles", () => {
    const primary = file({ id: "p", role: "PRIMARY", fileName: "main.pdf" });
    const supporting = file({
      id: "s",
      role: "SUPPORTING",
      fileName: "extra.pdf",
    });
    expect(pickKnowledgeDisplayFile([supporting, primary])).toBe(primary);
  });

  it("falls back to the first file when none is PRIMARY", () => {
    const first = file({ id: "1", role: "SUPPORTING", fileName: "a.pdf" });
    const second = file({ id: "2", role: "SUPPORTING", fileName: "b.pdf" });
    expect(pickKnowledgeDisplayFile([first, second])).toBe(first);
  });
});

describe("buildKnowledgeListMeta", () => {
  it("appends the display file type label", () => {
    const meta = buildKnowledgeListMeta(
      {
        documentNumber: "SOP-001",
        versionLabel: "1",
        status: "ACTIVE",
        effectiveFrom: "2026-08-11T00:00:00Z",
        effectiveTo: null,
        createdAt: "2026-08-11T00:00:00Z",
        updatedAt: "2026-08-11T00:00:00Z",
        files: [file()],
      },
      labels,
      () => "11/08/2026",
    );
    expect(meta).toContain("PDF");
    expect(meta).toContain("SOP-001");
    // One file — the count segment stays out of the way.
    expect(meta).not.toContain("berkas");
  });

  it("counts the attached files when a record carries more than one", () => {
    const meta = buildKnowledgeListMeta(
      {
        documentNumber: null,
        versionLabel: null,
        status: "ACTIVE",
        effectiveFrom: "2026-08-11T00:00:00Z",
        effectiveTo: null,
        createdAt: "2026-08-11T00:00:00Z",
        updatedAt: "2026-08-11T00:00:00Z",
        files: [
          file({ id: "1", fileName: "panduan-a.docx" }),
          file({ id: "2", role: "SUPPORTING", fileName: "panduan-b.docx" }),
        ],
      },
      labels,
      () => "11/08/2026",
    );
    expect(meta).toContain("2 berkas");
  });
});
