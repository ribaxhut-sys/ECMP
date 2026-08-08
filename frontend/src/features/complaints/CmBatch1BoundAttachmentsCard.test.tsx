/**
 * Component smoke for confirmation bound attachments (API-509 / API-512).
 */
import { cleanup, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";

const fetchCmBatch1ComplaintAttachments = vi.fn();
const voidCmBatch1Attachment = vi.fn();
const hasPermission = vi.fn((code: string) =>
  ["attachment:read", "attachment:delete"].includes(code),
);

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({
    hasPermission,
    user: null,
  }),
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchCmBatch1ComplaintAttachments: (...args: unknown[]) =>
      fetchCmBatch1ComplaintAttachments(...args),
    voidCmBatch1Attachment: (...args: unknown[]) =>
      voidCmBatch1Attachment(...args),
  };
});

import { CmBatch1BoundAttachmentsCard } from "./CmBatch1BoundAttachmentsCard";

const COMPLAINT_ID = "11111111-1111-1111-1111-111111111111";

describe("CmBatch1BoundAttachmentsCard", () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    fetchCmBatch1ComplaintAttachments.mockReset();
    voidCmBatch1Attachment.mockReset();
    hasPermission.mockImplementation((code: string) =>
      ["attachment:read", "attachment:delete"].includes(code),
    );
  });

  it("lists bound attachments from Aggregate complaint id", async () => {
    fetchCmBatch1ComplaintAttachments.mockResolvedValue({
      data: [
        {
          attachmentId: "att-bound-1",
          platformAttachmentId: "plat-1",
          status: "ACTIVE",
          classification: "customer_evidence",
          originalName: "bound.pdf",
          mimeType: "application/pdf",
          sizeBytes: 4096,
          checksumSha256: "xyz",
          createdAt: "2026-07-31T00:00:00Z",
        },
      ],
      meta: { page: 1, pageSize: 100, totalItems: 1 },
    });

    renderWithProviders(<CmBatch1BoundAttachmentsCard complaintId={COMPLAINT_ID} />);

    await waitFor(() => {
      expect(screen.getByTestId("bound-item-att-bound-1")).toBeInTheDocument();
    });
    expect(fetchCmBatch1ComplaintAttachments).toHaveBeenCalledWith(COMPLAINT_ID);
    expect(screen.getByText("1 attachment")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Open bound.pdf" }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Download bound.pdf" }),
    ).not.toBeInTheDocument();
  });

  it("shows empty label when none bound", async () => {
    fetchCmBatch1ComplaintAttachments.mockResolvedValue({
      data: [],
      meta: { page: 1, pageSize: 100, totalItems: 0 },
    });
    renderWithProviders(<CmBatch1BoundAttachmentsCard complaintId={COMPLAINT_ID} />);
    await waitFor(() => {
      expect(screen.getByTestId("bound-empty")).toBeInTheDocument();
    });
  });

  it("voids a bound attachment in one click", async () => {
    const user = userEvent.setup();
    fetchCmBatch1ComplaintAttachments.mockResolvedValue({
      data: [
        {
          attachmentId: "att-bound-2",
          platformAttachmentId: "plat-2",
          status: "ACTIVE",
          classification: "official_letter",
          originalName: "letter.pdf",
          mimeType: "application/pdf",
          sizeBytes: 100,
          checksumSha256: "qqq",
          createdAt: "2026-07-31T00:00:00Z",
        },
      ],
      meta: { page: 1, pageSize: 100, totalItems: 1 },
    });
    voidCmBatch1Attachment.mockResolvedValue({
      data: {
        attachmentId: "att-bound-2",
        platformAttachmentId: "plat-2",
        status: "VOID",
        classification: "official_letter",
        originalName: "letter.pdf",
        mimeType: "application/pdf",
        sizeBytes: 100,
        checksumSha256: "qqq",
        voidReason: "removed_by_uploader",
        createdAt: "2026-07-31T00:00:00Z",
      },
    });

    renderWithProviders(<CmBatch1BoundAttachmentsCard complaintId={COMPLAINT_ID} />);
    await waitFor(() => {
      expect(screen.getByTestId("bound-item-att-bound-2")).toBeInTheDocument();
    });

    await user.click(
      screen.getByRole("button", { name: "Delete attachment: letter.pdf" }),
    );
    expect(screen.queryByTestId("bound-void-form")).not.toBeInTheDocument();

    await waitFor(() => {
      expect(voidCmBatch1Attachment).toHaveBeenCalledWith(
        "att-bound-2",
        "removed_by_uploader",
      );
    });
    expect(screen.getByTestId("bound-empty")).toBeInTheDocument();
  });
});
