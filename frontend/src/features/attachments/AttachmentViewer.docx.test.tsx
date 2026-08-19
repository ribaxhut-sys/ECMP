/**
 * .docx preview path — the viewer must render Word files inline instead of
 * falling back to the download-only message (docx-preview is mocked; the real
 * library is a browser-only chunk).
 */
import { cleanup, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";
import type { Attachment } from "@/lib/api";

const downloadAttachment = vi.fn();
const renderAsync = vi.fn();

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    downloadAttachment: (...args: unknown[]) => downloadAttachment(...args),
  };
});

vi.mock("docx-preview", () => ({
  renderAsync: (...args: unknown[]) => renderAsync(...args),
}));

import { AttachmentViewer } from "./AttachmentViewer";

const DOCX: Attachment = {
  id: "att-docx",
  aggregateType: "Complaint",
  aggregateId: "cmp-1",
  fileName: "stored.docx",
  originalName: "Surat Keluhan.docx",
  storageProvider: "local",
  mimeType:
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  extension: ".docx",
  sizeBytes: 4096,
  checksumSha256: "abc",
  status: "AVAILABLE",
  uploadedBy: "user-1",
  uploadedAt: "2026-08-13T00:00:00Z",
};

describe("AttachmentViewer — .docx", () => {
  beforeEach(() => {
    downloadAttachment.mockReset();
    renderAsync.mockReset();
    downloadAttachment.mockResolvedValue({
      blob: new Blob(["PK"], { type: DOCX.mimeType }),
      filename: DOCX.originalName,
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

  it("renders the document inline and never creates an object URL for it", async () => {
    renderWithProviders(
      <AttachmentViewer attachment={DOCX} open onClose={() => {}} />,
    );

    await waitFor(() =>
      expect(screen.getByTestId("attachment-docx-preview")).toBeInTheDocument(),
    );
    await waitFor(() => expect(renderAsync).toHaveBeenCalledTimes(1));
    await screen.findByText("Isi dokumen");
    expect(URL.createObjectURL).not.toHaveBeenCalled();
  });

  it("keeps tracked changes, comments and alt-chunks out of the render", async () => {
    renderWithProviders(
      <AttachmentViewer attachment={DOCX} open onClose={() => {}} />,
    );

    await waitFor(() => expect(renderAsync).toHaveBeenCalledTimes(1));
    const options = renderAsync.mock.calls[0][3] as Record<string, unknown>;
    expect(options.renderAltChunks).toBe(false);
    expect(options.renderChanges).toBe(false);
    expect(options.renderComments).toBe(false);
  });

  it("opens the in-app preview route in a new tab instead of a blob URL", async () => {
    const user = userEvent.setup();
    const open = vi.fn(() => ({}) as Window);
    vi.stubGlobal("open", open);

    renderWithProviders(
      <AttachmentViewer attachment={DOCX} open onClose={() => {}} />,
    );
    await waitFor(() => expect(renderAsync).toHaveBeenCalled());
    downloadAttachment.mockClear();

    await user.click(screen.getByRole("button", { name: /new tab/i }));

    expect(open).toHaveBeenCalledWith(
      "/attachments/att-docx/preview",
      "_blank",
      "noopener,noreferrer",
    );
    // No second fetch, and nothing handed to the tab as a blob.
    expect(downloadAttachment).not.toHaveBeenCalled();
    expect(URL.createObjectURL).not.toHaveBeenCalled();
    vi.unstubAllGlobals();
  });

  it("offers a download fallback when rendering fails", async () => {
    renderAsync.mockRejectedValue(new Error("corrupt zip"));

    renderWithProviders(
      <AttachmentViewer attachment={DOCX} open onClose={() => {}} />,
    );

    expect(await screen.findByText(/tidak dapat ditampilkan|could not be rendered/i))
      .toBeInTheDocument();
  });
});
