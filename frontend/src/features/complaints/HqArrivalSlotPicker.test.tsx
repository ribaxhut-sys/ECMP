/**
 * HQ arrival slot picker — date label formatting and break-slot exclusion.
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

const gridDays = [
  {
    date: "2026-08-18",
    weekday: 2,
    closed: false,
    slots: [
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
];

describe("HqArrivalSlotPicker", () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    fetchHqScheduleAvailability.mockReset();
    fetchHqScheduleAvailability.mockResolvedValue({
      data: { startTime: "08:00", endTime: "13:00", slotMinutes: 60, capacityPerSlot: 2, days: gridDays },
    });
  });

  it("shows the date as DD-MM-YYYY with the weekday name", async () => {
    renderWithProviders(
      <HqArrivalSlotPicker value={null} onChange={() => {}} />,
    );
    await waitFor(() => {
      expect(fetchHqScheduleAvailability).toHaveBeenCalled();
    });
    expect(await screen.findByText("18-08-2026 (Selasa)")).toBeInTheDocument();
  });

  it("excludes the break slot from the time dropdown", async () => {
    renderWithProviders(
      <HqArrivalSlotPicker value={{ date: "2026-08-18", time: "" }} onChange={() => {}} />,
    );
    await waitFor(() => {
      expect(fetchHqScheduleAvailability).toHaveBeenCalled();
    });
    const timeSelect = await screen.findByLabelText(/Proposed arrival time/i);
    const optionValues = Array.from(timeSelect.querySelectorAll("option")).map(
      (opt) => opt.getAttribute("value"),
    );
    expect(optionValues).toContain("08:00");
    expect(optionValues).not.toContain("12:00");
  });
});
