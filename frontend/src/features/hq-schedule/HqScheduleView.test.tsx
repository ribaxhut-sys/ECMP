/**
 * HQ schedule calendar — Cabang uses the aggregate API; Pusat uses detail.
 */
import { cleanup, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";
import { toLocalDateKey } from "@/shared/utils/datetime";
import type { HqScheduleAvailabilityResponse } from "@/lib/api/hqSchedule";

const fetchHqScheduleAvailability = vi.fn();
const fetchHqScheduleAvailabilityDetail = vi.fn();
const fetchHqScheduleHolidays = vi.fn();
const fetchBranches = vi.fn();
const createHqScheduleHoliday = vi.fn();
const hasPermission = vi.fn<(permission: string) => boolean>(() => false);
let mockRoles: string[] = [];
let mockOrgUnitCode: string | null | undefined = "UPPPD-A";

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({
    hasPermission,
    roles: mockRoles,
    status: "authenticated",
    user: null,
  }),
}));

vi.mock("@/features/announcements/useOrgUnitCode", () => ({
  useOrgUnitCode: () => mockOrgUnitCode,
}));

vi.mock("@/lib/api", () => ({
  fetchBranches: (...args: unknown[]) => fetchBranches(...args),
}));

vi.mock("@/lib/api/hqSchedule", () => ({
  fetchHqScheduleAvailability: (...args: unknown[]) =>
    fetchHqScheduleAvailability(...args),
  fetchHqScheduleAvailabilityDetail: (...args: unknown[]) =>
    fetchHqScheduleAvailabilityDetail(...args),
  fetchHqScheduleHolidays: (...args: unknown[]) => fetchHqScheduleHolidays(...args),
  createHqScheduleHoliday: (...args: unknown[]) => createHqScheduleHoliday(...args),
  deleteHqScheduleHoliday: vi.fn(),
}));

import { HqScheduleView, slotOccupancy, summarizeHqWeek } from "./HqScheduleView";

const emptyGrid = {
  startTime: "08:00",
  slotMinutes: 60,
  capacityPerSlot: 2,
  days: [],
};

function gridWithCases(): HqScheduleAvailabilityResponse {
  return {
    startTime: "08:00",
    endTime: "10:00",
    slotMinutes: 60,
    capacityPerSlot: 2,
    days: [
      {
        date: "2026-08-17",
        weekday: 1,
        closed: false,
        slots: [
          {
            startTime: "08:00",
            endTime: "09:00",
            capacity: 2,
            isBreak: false,
            scheduledCount: 2,
            proposedCount: 0,
            availableCount: 0,
            pendingProposals: [],
            scheduledCases: [
              {
                complaintId: "case-own",
                complaintNumber: "TAB-2608-0001",
                owningUnitId: "UPPPD-A",
                unitCode: "TAB",
                caseNumbers: ["CASE-2026-000001"],
              },
              {
                complaintId: "case-other",
                complaintNumber: "GAM-2608-0002",
                owningUnitId: "UPPPD-B",
                unitCode: "GAM",
                caseNumbers: ["CASE-2026-000002"],
              },
            ],
          },
          {
            startTime: "09:00",
            endTime: "10:00",
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

describe("HqScheduleView", () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    fetchHqScheduleAvailability.mockReset();
    fetchHqScheduleAvailabilityDetail.mockReset();
    fetchHqScheduleHolidays.mockReset();
    fetchBranches.mockReset();
    createHqScheduleHoliday.mockReset();
    hasPermission.mockReset().mockImplementation((permission: string) => {
      return permission === "complaints:read";
    });
    mockRoles = ["AGENT"];
    mockOrgUnitCode = "UPPPD-A";
    fetchHqScheduleAvailability.mockResolvedValue({ data: emptyGrid });
    fetchHqScheduleAvailabilityDetail.mockResolvedValue({ data: emptyGrid });
    fetchHqScheduleHolidays.mockResolvedValue({ data: [] });
    fetchBranches.mockResolvedValue({
      data: [{ id: "b1", code: "UPPPD-A", name: "Cabang Tanah Abang" }],
    });
    createHqScheduleHoliday.mockResolvedValue({ data: {} });
  });

  it("loads the branch aggregate grid for a Cabang agent", async () => {
    renderWithProviders(<HqScheduleView />);
    await waitFor(() => {
      expect(fetchHqScheduleAvailability).toHaveBeenCalled();
    });
    expect(fetchHqScheduleAvailabilityDetail).not.toHaveBeenCalled();
    expect(screen.getByRole("heading", { name: /Taxpayer Escalation Schedule/i })).toBeInTheDocument();
  });

  it("loads the Pusat detail grid for a PUSAT agent", async () => {
    mockOrgUnitCode = "PUSAT";
    renderWithProviders(<HqScheduleView />);
    await waitFor(() => {
      expect(fetchHqScheduleAvailabilityDetail).toHaveBeenCalled();
    });
    expect(fetchHqScheduleAvailability).not.toHaveBeenCalled();
  });

  it("lets a Cabang agent open only its own case, with a tooltip on the branch tag", async () => {
    fetchHqScheduleAvailability.mockResolvedValue({ data: gridWithCases() });
    renderWithProviders(<HqScheduleView />);

    const ownLink = await screen.findByRole("link", { name: "CASE-2026-000001" });
    expect(ownLink).toHaveAttribute("href", "/complaints/cm/case-own");

    const otherCase = screen.getAllByText("CASE-2026-000002")[0];
    expect(otherCase.closest("a")).toBeNull();

    await waitFor(() => {
      expect(screen.getByTitle("Cabang Tanah Abang")).toBeInTheDocument();
    });
    expect(screen.getByTitle("Cabang Tanah Abang")).toHaveTextContent("TAB");
    expect(screen.queryByText("Cabang Tanah Abang")).not.toBeInTheDocument();
  });

  it("lets a Pusat reviewer open every case regardless of branch", async () => {
    mockOrgUnitCode = "PUSAT";
    fetchHqScheduleAvailabilityDetail.mockResolvedValue({ data: gridWithCases() });
    renderWithProviders(<HqScheduleView />);

    expect(
      await screen.findByRole("link", { name: "CASE-2026-000001" }),
    ).toBeInTheDocument();
    expect(
      await screen.findByRole("link", { name: "CASE-2026-000002" }),
    ).toBeInTheDocument();
  });

  it("renders scheduled cases on the day board without a duplicate weekly list", async () => {
    mockOrgUnitCode = "PUSAT";
    fetchHqScheduleAvailabilityDetail.mockResolvedValue({ data: gridWithCases() });
    renderWithProviders(<HqScheduleView />);

    const board = await screen.findByTestId("hq-schedule-board");
    expect(within(board).getByText("Senin")).toBeInTheDocument();
    expect(within(board).getByTestId("hq-schedule-slot-2026-08-17-08:00")).toBeInTheDocument();
    expect(within(board).getByRole("link", { name: "CASE-2026-000001" })).toBeInTheDocument();
    expect(within(board).getByRole("link", { name: "CASE-2026-000002" })).toBeInTheDocument();
    expect(within(board).getByText("GAM")).toBeInTheDocument();
    expect(screen.queryByText("This week's escalations")).not.toBeInTheDocument();
  });

  it("keeps week controls named and snaps today's column into view", async () => {
    const today = toLocalDateKey(new Date());
    const grid = gridWithCases();
    grid.days[0]!.date = today;
    const scrollIntoView = vi.fn();
    Object.defineProperty(HTMLElement.prototype, "scrollIntoView", {
      configurable: true,
      writable: true,
      value: scrollIntoView,
    });
    fetchHqScheduleAvailability.mockResolvedValue({ data: grid });
    renderWithProviders(<HqScheduleView />);

    expect(
      await screen.findByRole("button", { name: "Previous week" }),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "This week" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Next week" })).toBeInTheDocument();
    expect(screen.getByRole("group", { name: "Week navigation" })).toBeInTheDocument();
    expect(screen.getByText("Swipe for other days")).toBeInTheDocument();

    const board = await screen.findByTestId("hq-schedule-board");
    expect(board).toHaveClass("snap-x");
    expect(board).toHaveAttribute("aria-label", "Weekday arrival slots");
    const todayCol = await screen.findByTestId(`hq-schedule-day-${today}`);
    expect(todayCol).toHaveAttribute("data-today", "true");
    await waitFor(() => {
      expect(scrollIntoView).toHaveBeenCalled();
    });
  });

  it("enables This week after navigating away from the current week", async () => {
    const user = userEvent.setup();
    fetchHqScheduleAvailability.mockResolvedValue({ data: gridWithCases() });
    renderWithProviders(<HqScheduleView />);

    expect(await screen.findByRole("button", { name: "This week" })).toBeDisabled();
    await user.click(screen.getByRole("button", { name: "Next week" }));
    expect(screen.getByRole("button", { name: "This week" })).toBeEnabled();
  });

  it("shows the closed-week message when there are no working slots", async () => {
    renderWithProviders(<HqScheduleView />);
    expect(await screen.findByText("No working slots this week.")).toBeInTheDocument();
    expect(screen.queryByTestId("hq-schedule-board")).not.toBeInTheDocument();
  });

  it("shows capacity on both full and open slots", async () => {
    const grid = gridWithCases();
    grid.days[0]!.slots.push({
      startTime: "10:00",
      endTime: "11:00",
      capacity: 2,
      isBreak: false,
      scheduledCount: 0,
      proposedCount: 0,
      availableCount: 2,
      pendingProposals: [],
      scheduledCases: [],
    });
    fetchHqScheduleAvailability.mockResolvedValue({ data: grid });
    renderWithProviders(<HqScheduleView />);

    await screen.findAllByText("CASE-2026-000001");
    expect(screen.getAllByText("2/2 slot").length).toBeGreaterThan(0);
    expect(screen.getAllByText("0/2 slot").length).toBeGreaterThan(0);
    expect(screen.queryByText("Slot available")).not.toBeInTheDocument();
  });

  it("colors slots by occupancy: empty green, partial warning, full danger", async () => {
    const grid = gridWithCases();
    grid.days[0]!.slots.push(
      {
        startTime: "10:00",
        endTime: "11:00",
        capacity: 2,
        isBreak: false,
        scheduledCount: 0,
        proposedCount: 0,
        availableCount: 2,
        pendingProposals: [],
        scheduledCases: [],
      },
      {
        startTime: "11:00",
        endTime: "12:00",
        capacity: 2,
        isBreak: false,
        scheduledCount: 1,
        proposedCount: 0,
        availableCount: 1,
        pendingProposals: [],
        scheduledCases: [
          {
            complaintId: "case-partial",
            complaintNumber: "TAB-2608-0003",
            owningUnitId: "UPPPD-A",
            unitCode: "TAB",
            caseNumbers: ["CASE-2026-000003"],
          },
        ],
      },
    );
    fetchHqScheduleAvailability.mockResolvedValue({ data: grid });
    renderWithProviders(<HqScheduleView />);

    const full = await screen.findByTestId("hq-schedule-slot-2026-08-17-08:00");
    const empty = await screen.findByTestId("hq-schedule-slot-2026-08-17-10:00");
    const partial = await screen.findByTestId("hq-schedule-slot-2026-08-17-11:00");
    expect(full).toHaveAttribute("data-occupancy", "full");
    expect(empty).toHaveAttribute("data-occupancy", "empty");
    expect(partial).toHaveAttribute("data-occupancy", "partial");
    expect(full).toHaveClass("border-l-ecmp-danger");
    expect(empty).toHaveClass("border-l-ecmp-success");
    expect(partial).toHaveClass("border-l-ecmp-warning");
  });

  it("keeps a completed visit listed with a checklist tag and empty occupancy", async () => {
    const grid = gridWithCases();
    grid.days[0]!.slots.push({
      startTime: "10:00",
      endTime: "11:00",
      capacity: 2,
      isBreak: false,
      scheduledCount: 0,
      proposedCount: 0,
      availableCount: 2,
      pendingProposals: [],
      scheduledCases: [
        {
          complaintId: "case-done",
          complaintNumber: "TAB-2608-0009",
          owningUnitId: "UPPPD-A",
          unitCode: "TAB",
          caseNumbers: ["CASE-2026-000009"],
          completed: true,
        },
      ],
    });
    fetchHqScheduleAvailability.mockResolvedValue({ data: grid });
    renderWithProviders(<HqScheduleView />);

    const slot = await screen.findByTestId("hq-schedule-slot-2026-08-17-10:00");
    expect(slot).toHaveAttribute("data-occupancy", "empty");
    expect(within(slot).getByText("CASE-2026-000009")).toBeInTheDocument();
    expect(within(slot).getByText("Done")).toBeInTheDocument();
    expect(within(slot).getByText("CASE-2026-000009").closest("[data-completed]")).toHaveAttribute(
      "data-completed",
      "true",
    );
  });

  it("tags a break slot instead of showing case data", async () => {
    fetchHqScheduleAvailability.mockResolvedValue({ data: gridWithCases() });
    renderWithProviders(<HqScheduleView />);

    expect(await screen.findByText(/Break/)).toBeInTheDocument();
  });

  it("hides weekend columns and merges the break row into one cell", async () => {
    const grid = gridWithCases();
    grid.days.push(
      {
        date: "2026-08-22",
        weekday: 6,
        closed: true,
        closedReason: "WEEKEND",
        holidayLabel: null,
        slots: [],
      },
      {
        date: "2026-08-23",
        weekday: 7,
        closed: true,
        closedReason: "WEEKEND",
        holidayLabel: null,
        slots: [],
      },
    );
    fetchHqScheduleAvailability.mockResolvedValue({ data: grid });
    renderWithProviders(<HqScheduleView />);

    expect(await screen.findByText(/Break/)).toBeInTheDocument();
    expect(screen.queryByText("22-08-2026")).not.toBeInTheDocument();
    expect(screen.queryByText("23-08-2026")).not.toBeInTheDocument();
    expect(screen.getAllByText(/Break/)).toHaveLength(1);
  });

  it("imports the fixed-date national holidays for the selected year", async () => {
    hasPermission.mockImplementation((permission: string) =>
      ["complaints:read", "settings:read", "settings:update"].includes(permission),
    );
    const user = userEvent.setup();
    renderWithProviders(<HqScheduleView />);

    await user.click(await screen.findByText("Holidays this week"));
    const importButton = await screen.findByRole("button", {
      name: /Import fixed-date holidays/i,
    });
    await user.click(importButton);

    await waitFor(() => {
      expect(createHqScheduleHoliday).toHaveBeenCalledTimes(5);
    });
    const currentYear = new Date().getFullYear();
    expect(createHqScheduleHoliday).toHaveBeenCalledWith(
      expect.objectContaining({ holidayDate: `${currentYear}-01-01` }),
    );
    expect(createHqScheduleHoliday).toHaveBeenCalledWith(
      expect.objectContaining({ holidayDate: `${currentYear}-08-17` }),
    );
  });

  it("summarizes scheduled, today, and empty slot counts from visible weekdays", () => {
    expect(
      summarizeHqWeek(gridWithCases().days, "2026-08-17"),
    ).toEqual({ scheduled: 2, today: 2, empty: 0 });
    expect(
      summarizeHqWeek(gridWithCases().days, "2026-08-18"),
    ).toEqual({ scheduled: 2, today: 0, empty: 0 });
  });

  it("counts completed visits in week totals while occupancy stays empty", () => {
    expect(
      summarizeHqWeek(
        [
          {
            date: "2026-08-17",
            weekday: 1,
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
                scheduledCases: [
                  {
                    complaintId: "done",
                    complaintNumber: "TAB-2608-0009",
                    owningUnitId: "UPPPD-A",
                    unitCode: "TAB",
                    caseNumbers: ["CASE-2026-000009"],
                    completed: true,
                  },
                ],
              },
            ],
          },
        ],
        "2026-08-17",
      ),
    ).toEqual({ scheduled: 1, today: 1, empty: 2 });
  });

  it("maps occupancy from booked count, not leftover capacity", () => {
    expect(slotOccupancy(0, 2)).toBe("empty");
    expect(slotOccupancy(1, 2)).toBe("partial");
    expect(slotOccupancy(2, 2)).toBe("full");
    expect(slotOccupancy(1, 3)).toBe("partial");
    expect(slotOccupancy(2, 3)).toBe("partial");
    expect(slotOccupancy(3, 3)).toBe("full");
  });
});
