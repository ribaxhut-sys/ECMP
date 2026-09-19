import { cleanup, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";
import { AnnouncementExpandPanelAttachments } from "./AnnouncementExpandPanelAttachments";

const downloadAttachment = vi.fn();

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    downloadAttachment: (...args: unknown[]) => downloadAttachment(...args),
  };
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("AnnouncementExpandPanelAttachments", () => {
  it("renders a clear attachments heading and empty state", () => {
    renderWithProviders(
      <AnnouncementExpandPanelAttachments
        attachments={[]}
        attachmentCount={0}
      />,
    );

    expect(
      screen.getByRole("region", { name: /lampiran|attachments/i }),
    ).toBeInTheDocument();
    expect(screen.getByText(/tidak ada lampiran|no attachments/i)).toBeInTheDocument();
  });

  it("shows type badge, size, and downloads on click", async () => {
    const user = userEvent.setup();
    downloadAttachment.mockResolvedValue({
      blob: new Blob(["pdf"], { type: "application/pdf" }),
      filename: "memo.pdf",
      mimeType: "application/pdf",
      checksum: null,
    });

    renderWithProviders(
      <AnnouncementExpandPanelAttachments
        attachments={[
          {
            id: "att-1",
            fileName: "memo.pdf",
            mimeType: "application/pdf",
            sizeBytes: 2048,
            visibility: "PUBLISHED",
            createdAt: "2026-08-01T00:00:00Z",
          },
        ]}
        attachmentCount={1}
      />,
    );

    expect(screen.getByText("PDF")).toBeInTheDocument();
    expect(screen.getByText(/2(\.0)?\s*KB/i)).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /memo\.pdf/i }));
    expect(downloadAttachment).toHaveBeenCalledWith("att-1");
  });
});
