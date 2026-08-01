/**
 * Component smoke for SCR-CM-004 staging panel (upload + void affordance).
 */
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const uploadCmBatch1Attachment = vi.fn();
const voidCmBatch1Attachment = vi.fn();
const hasPermission = vi.fn((code: string) =>
  ["attachment:create", "attachment:delete"].includes(code),
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
    uploadCmBatch1Attachment: (...args: unknown[]) =>
      uploadCmBatch1Attachment(...args),
    voidCmBatch1Attachment: (...args: unknown[]) =>
      voidCmBatch1Attachment(...args),
  };
});

import { StagingAttachmentsPanel } from "./StagingAttachmentsPanel";

describe("StagingAttachmentsPanel", () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    uploadCmBatch1Attachment.mockReset();
    voidCmBatch1Attachment.mockReset();
    hasPermission.mockImplementation((code: string) =>
      ["attachment:create", "attachment:delete"].includes(code),
    );
  });

  it("shows empty state and uploads a staged file", async () => {
    const user = userEvent.setup();
    uploadCmBatch1Attachment.mockResolvedValue({
      data: {
        attachmentId: "att-staged-1",
        platformAttachmentId: "plat-1",
        status: "STAGED",
        classification: "customer_evidence",
        stagingToken: "STG-panel",
        originalName: "shot.png",
        mimeType: "image/png",
        sizeBytes: 2048,
        checksumSha256: "abc",
        createdAt: "2026-07-31T00:00:00Z",
      },
    });

    render(<StagingAttachmentsPanel stagingToken="STG-panel" />);
    expect(screen.getByTestId("staging-empty")).toBeInTheDocument();

    const file = new File(["x"], "shot.png", { type: "image/png" });
    const input = screen.getByLabelText("Choose file to stage");
    await user.upload(input, file);

    await waitFor(() => {
      expect(uploadCmBatch1Attachment).toHaveBeenCalled();
    });
    expect(screen.getByTestId("staging-item-att-staged-1")).toBeInTheDocument();
    expect(screen.getByText("shot.png")).toBeInTheDocument();
  });

  it("voids a staged item with required reason", async () => {
    const user = userEvent.setup();
    uploadCmBatch1Attachment.mockResolvedValue({
      data: {
        attachmentId: "att-staged-2",
        platformAttachmentId: "plat-2",
        status: "STAGED",
        classification: "customer_evidence",
        stagingToken: "STG-panel",
        originalName: "doc.pdf",
        mimeType: "application/pdf",
        sizeBytes: 100,
        checksumSha256: "def",
        createdAt: "2026-07-31T00:00:00Z",
      },
    });
    voidCmBatch1Attachment.mockResolvedValue({
      data: {
        attachmentId: "att-staged-2",
        platformAttachmentId: "plat-2",
        status: "VOID",
        classification: "customer_evidence",
        originalName: "doc.pdf",
        mimeType: "application/pdf",
        sizeBytes: 100,
        checksumSha256: "def",
        voidReason: "wrong file",
        createdAt: "2026-07-31T00:00:00Z",
      },
    });

    render(<StagingAttachmentsPanel stagingToken="STG-panel" />);
    const file = new File(["x"], "doc.pdf", { type: "application/pdf" });
    await user.upload(screen.getByLabelText("Choose file to stage"), file);
    await waitFor(() => {
      expect(screen.getByTestId("staging-item-att-staged-2")).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: "Void doc.pdf" }));
    expect(screen.getByTestId("staging-void-form")).toBeInTheDocument();
    await user.type(screen.getByLabelText("Void reason"), "wrong file");
    await user.click(
      screen.getByRole("button", { name: "Confirm void staged attachment" }),
    );

    await waitFor(() => {
      expect(voidCmBatch1Attachment).toHaveBeenCalledWith(
        "att-staged-2",
        "wrong file",
      );
    });
    expect(screen.getByTestId("staging-empty")).toBeInTheDocument();
  });
});
