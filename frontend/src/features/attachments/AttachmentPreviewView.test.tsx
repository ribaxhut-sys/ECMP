/**
 * Standalone preview page — the "open in new tab" target. Must render the file
 * itself (including .docx) rather than handing the browser a download.
 */
import { cleanup, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";
import { ApiError } from "@/lib/api";

const fetchAttachment = vi.fn();
const downloadAttachment = vi.fn();
const renderAsync = vi.fn();

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchAttachment: (...args: unknown[]) => fetchAttachment(...args),
    downloadAttachment: (...args: unknown[]) => downloadAttachment(...args),
  };
});

vi.mock("docx-preview", () => ({
  renderAsync: (...args: unknown[]) => renderAsync(...args),
}));

import { AttachmentPreviewView } from "./AttachmentPreviewView";

const META = {
  id: "att-docx",
  aggregateType: "Complaint" as const,
  aggregateId: "cmp-1",
  fileName: "stored.docx",
  originalName: "Surat Keluhan.docx",
  storageProvider: "local",
  mimeType:
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  extension: ".docx",
  sizeBytes: 4096,
  checksumSha256: "abc",
  status: "AVAILABLE" as const,
  uploadedBy: "user-1",
  uploadedAt: "2026-08-13T00:00:00Z",
};

describe("AttachmentPreviewView", () => {
  beforeEach(() => {
    fetchAttachment.mockReset();
    downloadAttachment.mockReset();
    renderAsync.mockReset();
    fetchAttachment.mockResolvedValue({ data: META });
    downloadAttachment.mockResolvedValue({
      blob: new Blob(["PK"], { type: META.mimeType }),
      filename: META.originalName,
    });
    renderAsync.mockImplementation(async (_blob: Blob, container: HTMLElement) => {
      container.innerHTML = "<p>Isi dokumen</p>";
    });
    Object.assign(URL, {
      createObjectURL: vi.fn(() => "blob:preview"),
      revokeObjectURL: vi.fn(),
    });
  });

  afterEach(() => {
    cleanup();
  });

  it("renders a Word attachment inline on its own page", async () => {
    renderWithProviders(<AttachmentPreviewView id="att-docx" />);

    expect(await screen.findByText("Surat Keluhan.docx")).toBeInTheDocument();
    await screen.findByText("Isi dokumen");
    expect(fetchAttachment).toHaveBeenCalledWith("att-docx");
    expect(downloadAttachment).toHaveBeenCalledWith("att-docx");
  });

  it("sets the browser tab title to the file name, and restores it on unmount", async () => {
    const originalTitle = document.title;
    const { unmount } = renderWithProviders(<AttachmentPreviewView id="att-docx" />);

    await waitFor(() => expect(document.title).toBe("Surat Keluhan.docx"));

    unmount();
    expect(document.title).toBe(originalTitle);
  });

  it("shows a retryable error when the metadata call is rejected", async () => {
    fetchAttachment.mockRejectedValue(new ApiError(403, "FORBIDDEN", "no"));

    renderWithProviders(<AttachmentPreviewView id="att-docx" />);

    expect(
      await screen.findByText(/do not have permission to view this file/i),
    ).toBeInTheDocument();
    await waitFor(() => expect(downloadAttachment).not.toHaveBeenCalled());
  });
});
