/**
 * HQ arrival slot picker — free date pick (not limited to "this week"),
 * per-day fetch, and break-slot exclusion.
 */
import { cleanup, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";

const fetchHqScheduleAvailability = vi.fn();

vi.mock("@/lib/api/hqSchedule", () => ({
  fetchHqScheduleAvailability: (...args: unknown[]) =>
    fetchHqScheduleAvailability(...args),
}));

import { HqArrivalSlotPicker } from "./HqArrivalSlotPicker";

function dayResponse(overrides: Partial<{ closed: boolean }> = {}) {
  return {
    startTime: "08:00",
    endTime: "13:00",
    slotMinutes: 60,
    capacityPerSlot: 2,
    days: [
      {
        date: "2026-08-18",
        weekday: 2,
        closed: overrides.closed ?? false,
        slots: overrides.closed
          ? []
          : [
              {
                startTime: "08:00",
                endTime: "09:00",
                capacity: 2,
                isBreak: false,
                scheduledCount: 0,
                proposedCount: 0,
                availableCount: 2,
                pendingProposals: [],
                scheduledCases: [],
              },
              {
                startTime: "12:00",
                endTime: "13:00",
                capacity: 2,
                isBreak: true,
                scheduledCount: 0,
                proposedCount: 0,
                availableCount: 2,
                pendingProposals: [],
                scheduledCases: [],
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
    fetchHqScheduleAvailability.mockResolvedValue({ data: dayResponse() });
  });

  it("does not fetch until a date is picked", () => {
    renderWithProviders(<HqArrivalSlotPicker value={null} onChange={() => {}} />);
    expect(fetchHqScheduleAvailability).not.toHaveBeenCalled();
  });

  it("fetches only the picked day and shows the weekday label", async () => {
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
    expect(await screen.findByText("Selasa, 18-08-2026")).toBeInTheDocument();
  });

  it("excludes the break slot from the time dropdown", async () => {
    renderWithProviders(
      <HqArrivalSlotPicker
        value={{ date: "2026-08-18", time: "" }}
        onChange={() => {}}
      />,
    );
    const timeSelect = await screen.findByLabelText(/Proposed arrival time/i);
    const optionValues = Array.from(timeSelect.querySelectorAll("option")).map(
      (opt) => opt.getAttribute("value"),
    );
    expect(optionValues).toContain("08:00");
    expect(optionValues).not.toContain("12:00");
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
});
