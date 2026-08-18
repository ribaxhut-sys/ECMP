import { cleanup, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { DatePicker, formatDateDDMMYYYY } from "./DatePicker";

describe("formatDateDDMMYYYY", () => {
  it("formats ISO yyyy-mm-dd as dd/mm/yyyy", () => {
    expect(formatDateDDMMYYYY("2026-09-16")).toBe("16/09/2026");
  });

  it("returns empty string for an empty/invalid value", () => {
    expect(formatDateDDMMYYYY("")).toBe("");
  });
});

describe("DatePicker", () => {
  afterEach(() => {
    cleanup();
  });

  it("shows dd/mm/yyyy on the trigger, not the browser locale format", () => {
    render(
      <DatePicker label="Tanggal" value="2026-09-16" onChange={() => {}} />,
    );
    expect(screen.getByText("16/09/2026")).toBeInTheDocument();
  });

  it("shows the placeholder when no value is set", () => {
    render(<DatePicker label="Tanggal" value="" onChange={() => {}} />);
    expect(screen.getByText("dd/mm/yyyy")).toBeInTheDocument();
  });

  it("opens the calendar and reports the picked day as ISO", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(
      <DatePicker
        label="Tanggal"
        value="2026-09-16"
        min="2026-09-01"
        max="2026-09-30"
        onChange={onChange}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Tanggal" }));
    const dialog = await screen.findByRole("dialog");
    expect(within(dialog).getByText("September 2026")).toBeInTheDocument();

    await user.click(within(dialog).getByRole("button", { name: "20/09/2026" }));
    expect(onChange).toHaveBeenCalledWith("2026-09-20");
  });

  it("disables days outside the min/max bounds", async () => {
    const user = userEvent.setup();
    render(
      <DatePicker
        label="Tanggal"
        value=""
        min="2026-09-10"
        max="2026-09-20"
        onChange={() => {}}
      />,
    );
    await user.click(screen.getByRole("button", { name: "Tanggal" }));
    const dialog = await screen.findByRole("dialog");
    expect(within(dialog).getByText("September 2026")).toBeInTheDocument();
    expect(within(dialog).getByRole("button", { name: "05/09/2026" })).toBeDisabled();
    expect(within(dialog).getByRole("button", { name: "15/09/2026" })).toBeEnabled();
  });

  it("disables Saturdays and Sundays when disabledWeekdays is set", async () => {
    const user = userEvent.setup();
    render(
      <DatePicker
        label="Tanggal"
        value="2026-09-16"
        disabledWeekdays={[0, 6]}
        onChange={() => {}}
      />,
    );
    await user.click(screen.getByRole("button", { name: "Tanggal" }));
    const dialog = await screen.findByRole("dialog");
    expect(within(dialog).getByRole("button", { name: "05/09/2026" })).toBeDisabled();
    expect(within(dialog).getByRole("button", { name: "06/09/2026" })).toBeDisabled();
    expect(within(dialog).getByRole("button", { name: "08/09/2026" })).toBeEnabled();
  });

  it("flips the calendar above the trigger when there isn't room below", async () => {
    const user = userEvent.setup();
    const getBoundingClientRect = vi
      .spyOn(HTMLDivElement.prototype, "getBoundingClientRect")
      .mockReturnValue({
        top: 700,
        bottom: 720,
        left: 0,
        right: 0,
        width: 0,
        height: 20,
        x: 0,
        y: 700,
        toJSON: () => {},
      });
    Object.defineProperty(window, "innerHeight", { value: 768, configurable: true });

    render(<DatePicker label="Tanggal" value="2026-09-16" onChange={() => {}} />);
    await user.click(screen.getByRole("button", { name: "Tanggal" }));
    const dialog = await screen.findByRole("dialog");
    expect(dialog).toHaveClass("bottom-full");

    getBoundingClientRect.mockRestore();
  });
});
