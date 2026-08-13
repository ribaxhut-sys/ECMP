/**
 * Catalog table — preview opens from the file name (no separate eye button).
 */
import { cleanup, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";

const fetchAnnouncementAttachmentLibrary = vi.fn();
const downloadAttachment = vi.fn();

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchAnnouncementAttachmentLibrary: (...args: unknown[]) =>
      fetchAnnouncementAttachmentLibrary(...args),
    downloadAttachment: (...args: unknown[]) => downloadAttachment(...args),
  };
});

import { AttachmentsWorkspace } from "./AttachmentsWorkspace";

const ITEM = {
  id: "att-1",
  fileName: "bukti.png",
  mimeType: "image/png",
  sizeBytes: 2048,
  createdAt: "2026-08-13T00:00:00Z",
  accessLevel: "PUBLIC" as const,
  uploadedOrgUnitId: "PUSAT",
  uploadedBy: "user-1",
  uploadedByName: "Admin",
  usageCount: 0,
};

describe("AttachmentsWorkspace", () => {
  beforeEach(() => {
    fetchAnnouncementAttachmentLibrary.mockReset();
    downloadAttachment.mockReset();
    fetchAnnouncementAttachmentLibrary.mockResolvedValue({ data: [ITEM] });
    downloadAttachment.mockResolvedValue({
      blob: new Blob(["x"], { type: "image/png" }),
      filename: ITEM.fileName,
    });
    Object.assign(URL, {
      createObjectURL: vi.fn(() => "blob:preview"),
      revokeObjectURL: vi.fn(),
    });
  });

  afterEach(() => {
    cleanup();
  });

  it("opens the viewer from the file name and has no separate preview icon", async () => {
    const user = userEvent.setup();
    renderWithProviders(<AttachmentsWorkspace />);

    const names = await screen.findAllByRole("button", {
      name: /preview: bukti\.png/i,
    });
    expect(names.length).toBeGreaterThan(0);
    expect(
      screen.queryByRole("button", { name: /^preview$/i }),
    ).not.toBeInTheDocument();

    await user.click(names[0]!);

    await waitFor(() => {
      expect(screen.getByTestId("attachment-viewer")).toBeInTheDocument();
    });
    expect(downloadAttachment).toHaveBeenCalledWith("att-1");
  });
});
