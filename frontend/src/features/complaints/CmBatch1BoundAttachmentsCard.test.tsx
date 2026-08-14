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
import { ApiError } from "@/lib/api";

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

  it("treats 404 list as empty, not an attachment error", async () => {
    fetchCmBatch1ComplaintAttachments.mockRejectedValue(
      new ApiError(404, "NOT_FOUND", "Sumber daya tidak ditemukan."),
    );
    renderWithProviders(<CmBatch1BoundAttachmentsCard complaintId={COMPLAINT_ID} />);
    await waitFor(() => {
      expect(screen.getByTestId("bound-empty")).toBeInTheDocument();
    });
    expect(screen.queryByText(/attachment error/i)).toBeNull();
  });

  it("still surfaces server errors when listing attachments", async () => {
    fetchCmBatch1ComplaintAttachments.mockRejectedValue(
      new ApiError(500, "INTERNAL", "store unavailable"),
    );
    renderWithProviders(<CmBatch1BoundAttachmentsCard complaintId={COMPLAINT_ID} />);
    await waitFor(() => {
      expect(screen.getByText("store unavailable")).toBeInTheDocument();
    });
    expect(screen.queryByTestId("bound-empty")).toBeNull();
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

  it("when locked keeps Open and hides upload/void chrome", async () => {
    hasPermission.mockImplementation((code: string) =>
      ["attachment:read", "attachment:create", "attachment:delete"].includes(
        code,
      ),
    );
    fetchCmBatch1ComplaintAttachments.mockResolvedValue({
      data: [
        {
          attachmentId: "att-bound-3",
          platformAttachmentId: "plat-3",
          status: "ACTIVE",
          classification: "customer_evidence",
          originalName: "test.pdf",
          mimeType: "application/pdf",
          sizeBytes: 45,
          checksumSha256: "abc",
          createdAt: "2026-08-11T00:00:00Z",
        },
      ],
      meta: { page: 1, pageSize: 100, totalItems: 1 },
    });

    renderWithProviders(
      <CmBatch1BoundAttachmentsCard
        complaintId={COMPLAINT_ID}
        allowUpload={false}
        allowVoid={false}
      />,
    );

    await waitFor(() => {
      expect(screen.getByTestId("bound-item-att-bound-3")).toBeInTheDocument();
    });
    expect(
      screen.getByText("test.pdf - 45 B - Taxpayer evidence"),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Open test.pdf" }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Delete attachment: test.pdf" }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByLabelText("Classification"),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Upload attachment to complaint" }),
    ).not.toBeInTheDocument();
  });
});
