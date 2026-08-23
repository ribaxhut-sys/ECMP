/**
 * Catalog table — preview opens from the file name (no separate eye button).
 */
import { cleanup, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";

const fetchAnnouncementAttachmentLibrary = vi.fn();
const downloadAttachment = vi.fn();
const pinAnnouncementAttachment = vi.fn();
const unpinAnnouncementAttachment = vi.fn();

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchAnnouncementAttachmentLibrary: (...args: unknown[]) =>
      fetchAnnouncementAttachmentLibrary(...args),
    downloadAttachment: (...args: unknown[]) => downloadAttachment(...args),
    pinAnnouncementAttachment: (...args: unknown[]) =>
      pinAnnouncementAttachment(...args),
    unpinAnnouncementAttachment: (...args: unknown[]) =>
      unpinAnnouncementAttachment(...args),
  };
});

import { ApiError } from "@/lib/api/client";
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
  pinned: false,
};

describe("AttachmentsWorkspace", () => {
  beforeEach(() => {
    fetchAnnouncementAttachmentLibrary.mockReset();
    downloadAttachment.mockReset();
    pinAnnouncementAttachment.mockReset();
    unpinAnnouncementAttachment.mockReset();
    fetchAnnouncementAttachmentLibrary.mockResolvedValue({ data: [ITEM] });
    downloadAttachment.mockResolvedValue({
      blob: new Blob(["x"], { type: "image/png" }),
      filename: ITEM.fileName,
    });
    pinAnnouncementAttachment.mockResolvedValue(undefined);
    unpinAnnouncementAttachment.mockResolvedValue(undefined);
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

  it("pins an attachment and reloads the list", async () => {
    const user = userEvent.setup();
    renderWithProviders(<AttachmentsWorkspace />);

    const pinButtons = await screen.findAllByRole("button", { name: /^pin$/i });
    fetchAnnouncementAttachmentLibrary.mockResolvedValueOnce({
      data: [{ ...ITEM, pinned: true }],
    });
    await user.click(pinButtons[0]!);

    await waitFor(() => {
      expect(pinAnnouncementAttachment).toHaveBeenCalledWith("att-1");
    });
    expect(
      (await screen.findAllByRole("button", { name: /^unpin$/i })).length,
    ).toBeGreaterThan(0);
  });

  it("shows the pin-limit message on a 409 CONFLICT from the pin endpoint", async () => {
    const user = userEvent.setup();
    pinAnnouncementAttachment.mockRejectedValue(
      new ApiError(409, "CONFLICT", "Attachment pin limit reached"),
    );
    renderWithProviders(<AttachmentsWorkspace />);

    const pinButtons = await screen.findAllByRole("button", { name: /^pin$/i });
    await user.click(pinButtons[0]!);

    expect(
      await screen.findByText(/maksimal 10 lampiran|at most 10 attachments/i),
    ).toBeInTheDocument();
  });
});
