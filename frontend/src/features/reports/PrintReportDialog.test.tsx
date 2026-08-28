import { cleanup, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";
import { PrintReportDialog } from "./PrintReportDialog";

const printReportPdf = vi.fn();

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    printReportPdf: (...args: unknown[]) => printReportPdf(...args),
  };
});

describe("PrintReportDialog", () => {
  let clickSpy: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    printReportPdf.mockReset();
    vi.stubGlobal("URL", {
      ...URL,
      createObjectURL: vi.fn(() => "blob:mock-url"),
      revokeObjectURL: vi.fn(),
    });
    clickSpy = vi.fn();
    // jsdom does not implement anchor.click() navigation — spy on it so the
    // download trigger is observable without actually downloading anything.
    HTMLAnchorElement.prototype.click = clickSpy;
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("requests the selected category and period, then downloads the PDF", async () => {
    const user = userEvent.setup();
    printReportPdf.mockResolvedValue({
      blob: new Blob(["%PDF"], { type: "application/pdf" }),
      filename: "laporan-pengaduan-escalated.pdf",
    });
    const onClose = vi.fn();

    renderWithProviders(
      <PrintReportDialog open onClose={onClose} period="thisMonth" />,
    );

    await user.click(screen.getByRole("radio", { name: "Complaints Escalated" }));
    await user.selectOptions(screen.getByRole("combobox", { name: "Period" }), "thisWeek");
    await user.click(screen.getByRole("button", { name: "Download" }));

    await waitFor(() => expect(printReportPdf).toHaveBeenCalledTimes(1));
    const call = printReportPdf.mock.calls[0][0];
    expect(call.category).toBe("escalated");
    expect(call.periodLabel).toBe("This week");
    expect(call.dateFrom).toBeTruthy();
    expect(call.dateTo).toBeTruthy();

    await waitFor(() => expect(clickSpy).toHaveBeenCalledTimes(1));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("inherits the page period, including all-time with no date window", async () => {
    const user = userEvent.setup();
    printReportPdf.mockResolvedValue({
      blob: new Blob(["%PDF"], { type: "application/pdf" }),
      filename: "laporan-pengaduan-all.pdf",
    });

    renderWithProviders(
      <PrintReportDialog open onClose={vi.fn()} period="all" />,
    );

    expect(screen.getByRole("combobox", { name: "Period" })).toHaveValue("all");
    expect(screen.getAllByRole("option")).toHaveLength(6);
    expect(screen.queryByRole("radio", { name: "Other" })).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Download" }));

    await waitFor(() => expect(printReportPdf).toHaveBeenCalledTimes(1));
    const call = printReportPdf.mock.calls[0][0];
    expect(call.category).toBe("all");
    expect(call.periodLabel).toBe("All time");
    expect(call.dateFrom).toBeUndefined();
    expect(call.dateTo).toBeUndefined();
  });

  it("shows an error and does not close when the export fails", async () => {
    const user = userEvent.setup();
    printReportPdf.mockRejectedValue(new Error("boom"));
    const onClose = vi.fn();

    renderWithProviders(<PrintReportDialog open onClose={onClose} />);
    await user.click(screen.getByRole("button", { name: "Download" }));

    expect(
      await screen.findByText("Could not generate the report PDF. Try again."),
    ).toBeInTheDocument();
    expect(clickSpy).not.toHaveBeenCalled();
    expect(onClose).not.toHaveBeenCalled();
  });
});
