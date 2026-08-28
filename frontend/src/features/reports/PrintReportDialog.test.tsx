import { cleanup, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";
import { PrintReportDialog } from "./PrintReportDialog";

const printReportPdf = vi.fn();
const openBlankAttachmentTab = vi.fn();
const showAttachmentInTab = vi.fn();

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    printReportPdf: (...args: unknown[]) => printReportPdf(...args),
  };
});

vi.mock("@/features/complaints/cmBatch1Attachments", async () => {
  const actual = await vi.importActual<
    typeof import("@/features/complaints/cmBatch1Attachments")
  >("@/features/complaints/cmBatch1Attachments");
  return {
    ...actual,
    openBlankAttachmentTab: () => openBlankAttachmentTab(),
    showAttachmentInTab: (...args: unknown[]) => showAttachmentInTab(...args),
  };
});

describe("PrintReportDialog", () => {
  beforeEach(() => {
    printReportPdf.mockReset();
    openBlankAttachmentTab.mockReset();
    showAttachmentInTab.mockReset();
    vi.stubGlobal("URL", {
      ...URL,
      createObjectURL: vi.fn(() => "blob:mock-url"),
      revokeObjectURL: vi.fn(),
    });
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("requests the selected category and period, then opens the PDF in the reserved tab", async () => {
    const user = userEvent.setup();
    const fakeTab = { close: vi.fn() } as unknown as Window;
    openBlankAttachmentTab.mockReturnValue(fakeTab);
    printReportPdf.mockResolvedValue({
      blob: new Blob(["%PDF"], { type: "application/pdf" }),
      filename: "laporan-pengaduan-escalated.pdf",
    });
    const onClose = vi.fn();

    renderWithProviders(<PrintReportDialog open onClose={onClose} />);

    await user.click(screen.getByRole("radio", { name: "Complaints Escalated" }));
    await user.click(screen.getByRole("radio", { name: "This week" }));
    await user.click(screen.getByRole("button", { name: "Print" }));

    await waitFor(() => expect(printReportPdf).toHaveBeenCalledTimes(1));
    const call = printReportPdf.mock.calls[0][0];
    expect(call.category).toBe("escalated");
    expect(call.periodLabel).toBe("This week");
    expect(call.dateFrom).toBeTruthy();
    expect(call.dateTo).toBeTruthy();

    await waitFor(() => expect(showAttachmentInTab).toHaveBeenCalledWith(fakeTab, "blob:mock-url"));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("shows a popup-blocked message and never calls the API when the tab cannot open", async () => {
    const user = userEvent.setup();
    openBlankAttachmentTab.mockReturnValue(null);

    renderWithProviders(<PrintReportDialog open onClose={vi.fn()} />);
    await user.click(screen.getByRole("button", { name: "Print" }));

    expect(
      await screen.findByText(/blocked the popup/i),
    ).toBeInTheDocument();
    expect(printReportPdf).not.toHaveBeenCalled();
  });

  it("closes the reserved tab and surfaces an error when the export fails", async () => {
    const user = userEvent.setup();
    const fakeTab = { close: vi.fn() } as unknown as Window;
    openBlankAttachmentTab.mockReturnValue(fakeTab);
    printReportPdf.mockRejectedValue(new Error("boom"));

    renderWithProviders(<PrintReportDialog open onClose={vi.fn()} />);
    await user.click(screen.getByRole("button", { name: "Print" }));

    await waitFor(() => expect(fakeTab.close).toHaveBeenCalledTimes(1));
    expect(
      await screen.findByText("Could not generate the report PDF. Try again."),
    ).toBeInTheDocument();
  });
});
