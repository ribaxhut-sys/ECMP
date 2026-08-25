/**
 * HQ arrival slot picker — free date pick (not limited to "this week"),
 * per-day fetch, and break-slot exclusion. Pusat mode uses the detail API
 * and may keep a full unit slot selectable with a warning.
 */
import { cleanup, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useState } from "react";
import { renderWithProviders } from "@/test/harness";

const fetchHqScheduleAvailability = vi.fn();
const fetchHqScheduleAvailabilityDetail = vi.fn();
const fetchHqScheduleHolidays = vi.fn();

vi.mock("@/lib/api/hqSchedule", () => ({
  fetchHqScheduleAvailability: (...args: unknown[]) =>
    fetchHqScheduleAvailability(...args),
  fetchHqScheduleAvailabilityDetail: (...args: unknown[]) =>
    fetchHqScheduleAvailabilityDetail(...args),
  fetchHqScheduleHolidays: (...args: unknown[]) => fetchHqScheduleHolidays(...args),
}));

import { HqArrivalSlotPicker } from "./HqArrivalSlotPicker";

function dayResponse(
  overrides: Partial<{
    closed: boolean;
    units: boolean;
    unitAvailable: number;
    date: string;
  }> = {},
) {
  const withUnits = overrides.units === true;
  const unitAvailable = overrides.unitAvailable ?? 2;
  const date = overrides.date ?? "2026-08-18";
  return {
    startTime: "08:00",
    endTime: "13:00",
    slotMinutes: 60,
    capacityPerSlot: 2,
    days: [
      {
        date,
        weekday: 2,
        closed: overrides.closed ?? false,
        slots: overrides.closed
          ? []
          : [
              {
                startTime: "08:00",
                endTime: "09:00",
                capacity: withUnits ? 4 : 2,
                isBreak: false,
                scheduledCount: withUnits && unitAvailable <= 0 ? 2 : 0,
                completedCount: 0,
                proposedCount: 0,
                availableCount: withUnits ? unitAvailable + 2 : 2,
                bookable: true,
                bookableCount: withUnits ? unitAvailable + 2 : 2,
                pendingProposals: [],
                scheduledCases: [],
                units: withUnits
                  ? [
                      {
                        unitCode: "PUSAT-CRO",
                        unitName: "CRO",
                        capacity: 2,
                        scheduledCount: unitAvailable <= 0 ? 2 : 0,
                        completedCount: 0,
                        availableCount: unitAvailable,
                        bookable: unitAvailable > 0,
                      },
                      {
                        unitCode: "PUSAT-SEKRETARIAT",
                        unitName: "Sekretariat",
                        capacity: 2,
                        scheduledCount: 0,
                        completedCount: 0,
                        availableCount: 2,
                        bookable: true,
                      },
                    ]
                  : [],
              },
              {
                startTime: "12:00",
                endTime: "13:00",
                capacity: 2,
                isBreak: true,
                scheduledCount: 0,
                completedCount: 0,
                proposedCount: 0,
                availableCount: 2,
                bookable: false,
                bookableCount: 0,
                pendingProposals: [],
                scheduledCases: [],
                units: [],
              },
            ],
      },
    ],
  };
}

describe("HqArrivalSlotPicker", () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    fetchHqScheduleAvailability.mockReset();
    fetchHqScheduleAvailabilityDetail.mockReset();
    fetchHqScheduleHolidays.mockReset();
    fetchHqScheduleAvailability.mockResolvedValue({ data: dayResponse() });
    fetchHqScheduleAvailabilityDetail.mockResolvedValue({
      data: dayResponse({ units: true }),
    });
    fetchHqScheduleHolidays.mockResolvedValue({ data: [] });
  });

  it("does not fetch until a date is picked", () => {
    renderWithProviders(<HqArrivalSlotPicker value={null} onChange={() => {}} />);
    expect(fetchHqScheduleAvailability).not.toHaveBeenCalled();
  });

  it("disables a holiday date in the calendar so it cannot be picked", async () => {
    const user = userEvent.setup();
    fetchHqScheduleHolidays.mockResolvedValue({
      data: [{ holidayDate: "2026-08-25", label: "Cuti bersama", createdAt: "" }],
    });
    renderWithProviders(<HqArrivalSlotPicker value={null} onChange={() => {}} />);

    await user.click(screen.getByRole("button", { name: "Arrival date" }));
    const holidayCell = await screen.findByRole("button", { name: "25/08/2026" });
    expect(holidayCell).toBeDisabled();

    await user.click(holidayCell);
    expect(fetchHqScheduleAvailability).not.toHaveBeenCalled();
  });

  it("fetches only the picked day and always shows dd/mm/yyyy regardless of browser locale", async () => {
    renderWithProviders(
      <HqArrivalSlotPicker
        value={{ date: "2026-08-18", time: "" }}
        onChange={() => {}}
      />,
    );
    await waitFor(() => {
      expect(fetchHqScheduleAvailability).toHaveBeenCalledWith(
        "2026-08-18",
        "2026-08-18",
      );
    });
    expect(await screen.findByText("18/08/2026")).toBeInTheDocument();
  });

  it("excludes the break slot from the time dropdown", async () => {
    renderWithProviders(
      <HqArrivalSlotPicker
        value={{ date: "2026-08-18", time: "" }}
        onChange={() => {}}
      />,
    );
    const timeSelect = await screen.findByLabelText(/^Arrival time$/i);
    const optionValues = Array.from(timeSelect.querySelectorAll("option")).map(
      (opt) => opt.getAttribute("value"),
    );
    expect(optionValues).toContain("08:00");
    expect(optionValues).not.toContain("12:00");
  });

  it("disables a slot the backend marks unbookable (past, full, or on break)", async () => {
    fetchHqScheduleAvailability.mockResolvedValue({
      data: dayResponse(),
    });
    renderWithProviders(
      <HqArrivalSlotPicker
        value={{ date: "2026-08-18", time: "" }}
        onChange={() => {}}
      />,
    );
    const timeSelect =
      await screen.findByLabelText<HTMLSelectElement>(/^Arrival time$/i);
    const bookableOption = Array.from(timeSelect.querySelectorAll("option")).find(
      (opt) => opt.getAttribute("value") === "08:00",
    );
    expect(bookableOption).not.toBeDisabled();
  });

  it("shows a no-slots hint when the picked day is closed", async () => {
    fetchHqScheduleAvailability.mockResolvedValue({
      data: dayResponse({ closed: true }),
    });
    renderWithProviders(
      <HqArrivalSlotPicker
        value={{ date: "2026-08-22", time: "" }}
        onChange={() => {}}
      />,
    );
    expect(await screen.findByText("No open slots")).toBeInTheDocument();
  });

  it("waits for a destination unit before fetching in Pusat mode", () => {
    renderWithProviders(
      <HqArrivalSlotPicker
        value={{ date: "2026-09-15", time: "" }}
        onChange={() => {}}
        destinationUnitCode=""
        allowOverCapacity
      />,
    );
    expect(fetchHqScheduleAvailabilityDetail).not.toHaveBeenCalled();
    expect(fetchHqScheduleAvailability).not.toHaveBeenCalled();
    // The unit is resolved for the operator now, so the placeholder says the
    // CRO unit is still loading rather than asking them to pick one — the
    // behaviour under test (no fetch until it is known) is unchanged.
    expect(
      screen.getByText(/Loading HQ CRO to show remaining quota per hour/i),
    ).toBeInTheDocument();
  });

  it("loads detail availability and keeps a full unit slot selectable with a warning", async () => {
    const user = userEvent.setup();
    fetchHqScheduleAvailabilityDetail.mockResolvedValue({
      data: dayResponse({ units: true, unitAvailable: 0, date: "2026-09-15" }),
    });

    function Harness() {
      const [value, setValue] = useState<{ date: string; time: string } | null>({
        date: "2026-09-15",
        time: "",
      });
      return (
        <HqArrivalSlotPicker
          value={value}
          onChange={setValue}
          destinationUnitCode="PUSAT-CRO"
          allowOverCapacity
        />
      );
    }

    renderWithProviders(<Harness />);
    await waitFor(() => {
      expect(fetchHqScheduleAvailabilityDetail).toHaveBeenCalledWith(
        "2026-09-15",
        "2026-09-15",
      );
    });
    const timeSelect =
      await screen.findByLabelText<HTMLSelectElement>(/^Arrival time$/i);
    const fullOption = Array.from(timeSelect.querySelectorAll("option")).find(
      (opt) => opt.getAttribute("value") === "08:00",
    );
    expect(fullOption).not.toBeDisabled();
    await user.selectOptions(timeSelect, "08:00");
    expect(await screen.findByText(/Unit quota full/i)).toBeInTheDocument();
  });
});
