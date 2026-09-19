/**
 * Component smoke for SCR-CM-004 staging panel (upload + one-click void).
 */
import { cleanup, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";

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

  it("shows open and delete after a successful staging upload", async () => {
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

    renderWithProviders(
      <StagingAttachmentsPanel
        stagingToken="STG-panel"
        customerId="CUST-LAB-001"
      />,
    );

    const file = new File(["x"], "shot.png", { type: "image/png" });
    const input = screen.getByLabelText("Choose one or more files");
    await user.upload(input, file);

    await waitFor(() => {
      expect(screen.getByTestId("staging-item-att-staged-1")).toBeInTheDocument();
    });
    expect(
      screen.getByRole("button", { name: "Open shot.png" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Delete attachment: shot.png" }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Download shot.png" }),
    ).not.toBeInTheDocument();
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

    renderWithProviders(
      <StagingAttachmentsPanel
        stagingToken="STG-panel"
        customerId="CUST-LAB-001"
      />,
    );
    expect(screen.getByTestId("staging-empty")).toBeInTheDocument();

    const file = new File(["x"], "shot.png", { type: "image/png" });
    const input = screen.getByLabelText("Choose one or more files");
    await user.upload(input, file);

    await waitFor(() => {
      expect(uploadCmBatch1Attachment).toHaveBeenCalled();
    });
    expect(uploadCmBatch1Attachment.mock.calls[0]?.[0]).toMatchObject({
      customerId: "CUST-LAB-001",
      stagingToken: "STG-panel",
    });
    expect(screen.getByTestId("staging-item-att-staged-1")).toBeInTheDocument();
    expect(screen.getByText("shot.png")).toBeInTheDocument();
  });

  it("voids a staged item in one click without a reason form", async () => {
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
        voidReason: "removed_by_uploader",
        createdAt: "2026-07-31T00:00:00Z",
      },
    });

    renderWithProviders(
      <StagingAttachmentsPanel
        stagingToken="STG-panel"
        customerId="CUST-LAB-001"
      />,
    );
    const file = new File(["x"], "doc.pdf", { type: "application/pdf" });
    await user.upload(screen.getByLabelText("Choose one or more files"), file);
    await waitFor(() => {
      expect(screen.getByTestId("staging-item-att-staged-2")).toBeInTheDocument();
    });

    await user.click(
      screen.getByRole("button", { name: "Delete attachment: doc.pdf" }),
    );
    expect(screen.queryByTestId("staging-void-form")).not.toBeInTheDocument();

    await waitFor(() => {
      expect(voidCmBatch1Attachment).toHaveBeenCalledWith(
        "att-staged-2",
        "removed_by_uploader",
      );
    });
    expect(screen.getByTestId("staging-empty")).toBeInTheDocument();
  });

  it("uploads multiple selected files in one picker action", async () => {
    const user = userEvent.setup();
    uploadCmBatch1Attachment
      .mockResolvedValueOnce({
        data: {
          attachmentId: "att-m1",
          platformAttachmentId: "plat-m1",
          status: "STAGED",
          classification: "customer_evidence",
          stagingToken: "STG-panel",
          originalName: "one.png",
          mimeType: "image/png",
          sizeBytes: 1,
          checksumSha256: "1",
          createdAt: "2026-07-31T00:00:00Z",
        },
      })
      .mockResolvedValueOnce({
        data: {
          attachmentId: "att-m2",
          platformAttachmentId: "plat-m2",
          status: "STAGED",
          classification: "customer_evidence",
          stagingToken: "STG-panel",
          originalName: "two.png",
          mimeType: "image/png",
          sizeBytes: 2,
          checksumSha256: "2",
          createdAt: "2026-07-31T00:00:01Z",
        },
      });

    renderWithProviders(
      <StagingAttachmentsPanel
        stagingToken="STG-panel"
        customerId="CUST-LAB-001"
      />,
    );
    const input = screen.getByLabelText("Choose one or more files");
    expect(input).toHaveAttribute("multiple");
    await user.upload(input, [
      new File(["1"], "one.png", { type: "image/png" }),
      new File(["2"], "two.png", { type: "image/png" }),
    ]);

    await waitFor(() => {
      expect(uploadCmBatch1Attachment).toHaveBeenCalledTimes(2);
    });
    expect(screen.getByTestId("staging-item-att-m1")).toBeInTheDocument();
    expect(screen.getByTestId("staging-item-att-m2")).toBeInTheDocument();
  });

  it("removes only the voided row when two staged files exist", async () => {
    const user = userEvent.setup();
    uploadCmBatch1Attachment
      .mockResolvedValueOnce({
        data: {
          attachmentId: "att-a",
          platformAttachmentId: "plat-a",
          status: "STAGED",
          classification: "customer_evidence",
          stagingToken: "STG-panel",
          originalName: "a.png",
          mimeType: "image/png",
          sizeBytes: 1,
          checksumSha256: "a",
          createdAt: "2026-07-31T00:00:00Z",
        },
      })
      .mockResolvedValueOnce({
        data: {
          attachmentId: "att-b",
          platformAttachmentId: "plat-b",
          status: "STAGED",
          classification: "customer_evidence",
          stagingToken: "STG-panel",
          originalName: "b.png",
          mimeType: "image/png",
          sizeBytes: 2,
          checksumSha256: "b",
          createdAt: "2026-07-31T00:00:01Z",
        },
      });
    voidCmBatch1Attachment.mockResolvedValue({
      data: {
        attachmentId: "att-a",
        platformAttachmentId: "plat-a",
        status: "VOID",
        classification: "customer_evidence",
        originalName: "a.png",
        mimeType: "image/png",
        sizeBytes: 1,
        checksumSha256: "a",
        voidReason: "removed_by_uploader",
        createdAt: "2026-07-31T00:00:00Z",
      },
    });

    renderWithProviders(
      <StagingAttachmentsPanel
        stagingToken="STG-panel"
        customerId="CUST-LAB-001"
      />,
    );
    const input = screen.getByLabelText("Choose one or more files");
    await user.upload(input, new File(["a"], "a.png", { type: "image/png" }));
    await user.upload(input, new File(["b"], "b.png", { type: "image/png" }));

    await waitFor(() => {
      expect(screen.getByTestId("staging-item-att-a")).toBeInTheDocument();
      expect(screen.getByTestId("staging-item-att-b")).toBeInTheDocument();
    });

    await user.click(
      screen.getByRole("button", { name: "Delete attachment: a.png" }),
    );

    await waitFor(() => {
      expect(voidCmBatch1Attachment).toHaveBeenCalledWith(
        "att-a",
        "removed_by_uploader",
      );
    });
    expect(screen.queryByTestId("staging-item-att-a")).not.toBeInTheDocument();
    expect(screen.getByTestId("staging-item-att-b")).toBeInTheDocument();
    expect(screen.getByText("b.png")).toBeInTheDocument();
  });
});
