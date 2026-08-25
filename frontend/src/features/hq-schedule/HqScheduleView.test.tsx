/**
 * HQ schedule calendar — Cabang uses the aggregate API; Pusat uses detail.
 */
import { cleanup, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
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

import {
  HqScheduleView,
  dayOccupancyTotals,
  dayUnitBreakdown,
  isArrivalOverdue,
  isSlotPast,
  matchingScheduledCases,
  slotOccupancy,
  summarizeHqWeek,
  UNASSIGNED_UNIT_FILTER,
} from "./HqScheduleView";

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
            completedCount: 0,
            proposedCount: 0,
            availableCount: 0,
            bookable: false,
            bookableCount: 0,
            pendingProposals: [],
            scheduledCases: [
              {
                complaintId: "case-own",
                complaintNumber: "TAB-2608-0001",
                owningUnitId: "UPPPD-A",
                unitCode: "TAB",
                cases: [
                  { caseId: "id-case-2026-000001", caseNumber: "CASE-2026-000001" },
                ],
              },
              {
                complaintId: "case-other",
                complaintNumber: "GAM-2608-0002",
                owningUnitId: "UPPPD-B",
                unitCode: "GAM",
                cases: [
                  { caseId: "id-case-2026-000002", caseNumber: "CASE-2026-000002" },
                ],
              },
            ],
          },
          {
            startTime: "09:00",
            endTime: "10:00",
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
          },
        ],
      },
    ],
  };
}

describe("HqScheduleView", () => {
  beforeAll(() => {
    // jsdom has no scrollIntoView; the pinned clock below now makes several
    // fixtures' single day match "today", so the today-column effect runs.
    Object.defineProperty(HTMLElement.prototype, "scrollIntoView", {
      configurable: true,
      writable: true,
      value: vi.fn(),
    });
  });

  afterEach(() => {
    cleanup();
    vi.useRealTimers();
  });

  beforeEach(() => {
    // Pin "now" to before the 08:00 slot on the fixture's Monday so every
    // gridWithCases() slot reads as current, not past — individual tests
    // override with their own setSystemTime for overdue/past-slot scenarios.
    vi.useFakeTimers({ toFake: ["Date"] });
    vi.setSystemTime(new Date("2026-08-17T07:30:00"));
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
      data: [
        { id: "b1", code: "UPPPD-A", name: "Cabang Tanah Abang" },
        { id: "p-cro", code: "PUSAT-CRO", name: "CRO Pusat" },
        { id: "p-sek", code: "PUSAT-SEKRETARIAT", name: "Sekretariat" },
        { id: "p-sub", code: "PUSAT-SUBAN-1", name: "Suban 1" },
      ],
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

  it("lets a Cabang agent open only its own case", async () => {
    fetchHqScheduleAvailability.mockResolvedValue({ data: gridWithCases() });
    renderWithProviders(<HqScheduleView />);

    const ownLink = await screen.findByRole("link", { name: /CASE-2026-000001/ });
    expect(ownLink).toHaveAttribute(
      "href",
      "/complaints/cm/cases/id-case-2026-000001",
    );

    const otherCase = screen.getAllByText(/CASE-2026-000002/)[0];
    expect(otherCase.closest("a")).toBeNull();
  });

  it("links each Case number to its own Case, not to the parent complaint", async () => {
    const grid = gridWithCases();
    grid.days[0].slots[0].scheduledCases[0].cases = [
      { caseId: "id-a", caseNumber: "CASE-2026-000001" },
      { caseId: "id-b", caseNumber: "CASE-2026-000010" },
    ];
    fetchHqScheduleAvailability.mockResolvedValue({ data: grid });
    renderWithProviders(<HqScheduleView />);

    expect(
      await screen.findByRole("link", { name: "CASE-2026-000001" }),
    ).toHaveAttribute("href", "/complaints/cm/cases/id-a");
    expect(screen.getByRole("link", { name: "CASE-2026-000010" })).toHaveAttribute(
      "href",
      "/complaints/cm/cases/id-b",
    );
    expect(
      screen.queryByRole("link", { name: /TAB-2608-0001/ }),
    ).not.toBeInTheDocument();
  });

  it("falls back to the complaint for a legacy arrival with no Case", async () => {
    const grid = gridWithCases();
    grid.days[0].slots[0].scheduledCases[0].cases = [];
    fetchHqScheduleAvailability.mockResolvedValue({ data: grid });
    renderWithProviders(<HqScheduleView />);

    expect(
      await screen.findByRole("link", { name: "TAB-2608-0001" }),
    ).toHaveAttribute("href", "/complaints/cm/case-own");
  });

  it("lets a Pusat reviewer open every case regardless of branch", async () => {
    mockOrgUnitCode = "PUSAT";
    fetchHqScheduleAvailabilityDetail.mockResolvedValue({ data: gridWithCases() });
    renderWithProviders(<HqScheduleView />);

    expect(
      await screen.findByRole("link", { name: /CASE-2026-000001/ }),
    ).toBeInTheDocument();
    expect(
      await screen.findByRole("link", { name: /CASE-2026-000002/ }),
    ).toBeInTheDocument();
  });

  it("renders scheduled cases on the day board without a duplicate weekly list", async () => {
    mockOrgUnitCode = "PUSAT";
    fetchHqScheduleAvailabilityDetail.mockResolvedValue({ data: gridWithCases() });
    renderWithProviders(<HqScheduleView />);

    const board = await screen.findByTestId("hq-schedule-board");
    expect(within(board).getByText("Senin")).toBeInTheDocument();
    expect(within(board).getByTestId("hq-schedule-slot-2026-08-17-08:00")).toBeInTheDocument();
    expect(within(board).getByRole("link", { name: /CASE-2026-000001/ })).toBeInTheDocument();
    expect(within(board).getByRole("link", { name: /CASE-2026-000002/ })).toBeInTheDocument();
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
      completedCount: 0,
      proposedCount: 0,
      availableCount: 2,
      bookable: true,
      bookableCount: 2,
      pendingProposals: [],
      scheduledCases: [],
    });
    fetchHqScheduleAvailability.mockResolvedValue({ data: grid });
    renderWithProviders(<HqScheduleView />);

    await screen.findAllByText(/CASE-2026-000001/);
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
        completedCount: 0,
        proposedCount: 0,
        availableCount: 2,
        bookable: true,
        bookableCount: 2,
        pendingProposals: [],
        scheduledCases: [],
      },
      {
        startTime: "11:00",
        endTime: "12:00",
        capacity: 2,
        isBreak: false,
        scheduledCount: 1,
        completedCount: 0,
        proposedCount: 0,
        availableCount: 1,
        bookable: true,
        bookableCount: 1,
        pendingProposals: [],
        scheduledCases: [
          {
            complaintId: "case-partial",
            complaintNumber: "TAB-2608-0003",
            owningUnitId: "UPPPD-A",
            unitCode: "TAB",
            cases: [
              { caseId: "id-case-2026-000003", caseNumber: "CASE-2026-000003" },
            ],
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

  it("keeps a completed visit listed with a checklist tag and still counts it toward occupancy", async () => {
    const grid = gridWithCases();
    grid.days[0]!.slots.push({
      startTime: "10:00",
      endTime: "11:00",
      capacity: 2,
      isBreak: false,
      scheduledCount: 1,
      completedCount: 1,
      proposedCount: 0,
      availableCount: 1,
      bookable: true,
      bookableCount: 1,
      pendingProposals: [],
      scheduledCases: [
        {
          complaintId: "case-done",
          complaintNumber: "TAB-2608-0009",
          owningUnitId: "UPPPD-A",
          unitCode: "TAB",
          cases: [
            { caseId: "id-case-2026-000009", caseNumber: "CASE-2026-000009" },
          ],
          completed: true,
        },
      ],
    });
    fetchHqScheduleAvailability.mockResolvedValue({ data: grid });
    renderWithProviders(<HqScheduleView />);

    const slot = await screen.findByTestId("hq-schedule-slot-2026-08-17-10:00");
    expect(slot).toHaveAttribute("data-occupancy", "partial");
    expect(within(slot).getByText("1/2 slot")).toBeInTheDocument();
    expect(within(slot).getByText(/CASE-2026-000009/)).toBeInTheDocument();
    expect(within(slot).getByLabelText("Done")).toBeInTheDocument();
    expect(within(slot).queryByText("Done")).not.toBeInTheDocument();
    expect(within(slot).getByText(/CASE-2026-000009/).closest("[data-completed]")).toHaveAttribute(
      "data-completed",
      "true",
    );
  });

  it("tags a scheduled case as overdue once its slot end time has passed", async () => {
    vi.useFakeTimers({ toFake: ["Date"] });
    vi.setSystemTime(new Date("2026-08-17T09:30:00"));
    fetchHqScheduleAvailability.mockResolvedValue({ data: gridWithCases() });
    renderWithProviders(<HqScheduleView />);

    // 08:00-09:00 slot, now 09:30 — past end time and not completed.
    const slot = await screen.findByTestId("hq-schedule-slot-2026-08-17-08:00");
    expect(
      within(slot).getByText(/CASE-2026-000001/).closest("[data-overdue]"),
    ).toHaveAttribute("data-overdue", "true");
    expect(within(slot).getAllByLabelText("Past slot — WP hasn't arrived")).toHaveLength(2);
  });

  it("does not tag a scheduled case as overdue while its slot is still current", async () => {
    vi.useFakeTimers({ toFake: ["Date"] });
    vi.setSystemTime(new Date("2026-08-17T08:30:00"));
    fetchHqScheduleAvailability.mockResolvedValue({ data: gridWithCases() });
    renderWithProviders(<HqScheduleView />);

    const slot = await screen.findByTestId("hq-schedule-slot-2026-08-17-08:00");
    expect(
      within(slot).getByText(/CASE-2026-000001/).closest("[data-overdue]"),
    ).toHaveAttribute("data-overdue", "false");
    expect(
      within(slot).queryByLabelText("Past slot — WP hasn't arrived"),
    ).not.toBeInTheDocument();
  });

  it("does not tag a completed visit as overdue after the slot has passed", async () => {
    vi.useFakeTimers({ toFake: ["Date"] });
    vi.setSystemTime(new Date("2026-08-17T12:00:00"));
    const grid = gridWithCases();
    grid.days[0]!.slots[0]!.scheduledCases = [
      {
        complaintId: "case-done",
        complaintNumber: "TAB-2608-0009",
        owningUnitId: "UPPPD-A",
        unitCode: "TAB",
        cases: [
          { caseId: "id-case-2026-000009", caseNumber: "CASE-2026-000009" },
        ],
        completed: true,
      },
    ];
    fetchHqScheduleAvailability.mockResolvedValue({ data: grid });
    renderWithProviders(<HqScheduleView />);

    const slot = await screen.findByTestId("hq-schedule-slot-2026-08-17-08:00");
    expect(
      within(slot).getByText(/CASE-2026-000009/).closest("[data-overdue]"),
    ).toHaveAttribute("data-overdue", "false");
    expect(within(slot).getByLabelText("Done")).toBeInTheDocument();
    expect(
      within(slot).queryByLabelText("Past slot — WP hasn't arrived"),
    ).not.toBeInTheDocument();
  });

  it("treats a slot as overdue only after its end time", () => {
    const now = new Date("2026-08-17T09:00:00").getTime();
    expect(isArrivalOverdue("2026-08-17", "09:00", now)).toBe(false);
    expect(isArrivalOverdue("2026-08-17", "09:00", now + 1)).toBe(true);
    expect(isArrivalOverdue("2026-08-17", "08:00", now)).toBe(true);
    expect(isArrivalOverdue("not-a-date", "09:00", now)).toBe(false);
  });

  it("treats a slot as past only after its own end time, not its start time", () => {
    const now = new Date("2026-08-17T08:30:00").getTime();
    expect(isSlotPast("2026-08-17", "09:00", now)).toBe(false); // still in progress
    expect(isSlotPast("2026-08-17", "08:00", now)).toBe(true); // ended already
    expect(isSlotPast("not-a-date", "09:00", now)).toBe(false);
  });

  it("shows a completed/scheduled outcome instead of a capacity ratio once the slot has fully elapsed", async () => {
    vi.setSystemTime(new Date("2026-08-17T09:30:00")); // 08:00-09:00 slot is over
    const grid = gridWithCases();
    grid.days[0]!.slots[0]!.completedCount = 1; // 2 scheduled, 1 closed, 1 still open
    fetchHqScheduleAvailability.mockResolvedValue({ data: grid });
    renderWithProviders(<HqScheduleView />);

    const slot = await screen.findByTestId("hq-schedule-slot-2026-08-17-08:00");
    expect(within(slot).getByText("1/2 done")).toBeInTheDocument();
    expect(within(slot).queryByText("2/2 slot")).not.toBeInTheDocument();
    expect(slot).toHaveAttribute("data-past", "true");
    expect(slot).not.toHaveClass("border-l-ecmp-danger");
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

  it("summarizes scheduled, today, and bookable slot counts from visible weekdays", () => {
    expect(summarizeHqWeek(gridWithCases().days, "2026-08-17")).toEqual({
      scheduled: 2,
      today: 2,
      todayCompleted: 0,
      bookable: 0,
      weekCompleted: 0,
    });
    expect(summarizeHqWeek(gridWithCases().days, "2026-08-18")).toEqual({
      scheduled: 2,
      today: 0,
      todayCompleted: 0,
      bookable: 0,
      weekCompleted: 0,
    });
  });

  it("counts a completed visit toward scheduled and week-completed totals", () => {
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
                scheduledCount: 1,
                completedCount: 1,
                proposedCount: 0,
                availableCount: 1,
                bookable: true,
                bookableCount: 1,
                pendingProposals: [],
                scheduledCases: [
                  {
                    complaintId: "done",
                    complaintNumber: "TAB-2608-0009",
                    owningUnitId: "UPPPD-A",
                    unitCode: "TAB",
                    cases: [
                      { caseId: "id-case-2026-000009", caseNumber: "CASE-2026-000009" },
                    ],
                    completed: true,
                  },
                ],
              },
            ],
          },
        ],
        "2026-08-17",
      ),
    ).toEqual({ scheduled: 1, today: 1, todayCompleted: 1, bookable: 1, weekCompleted: 1 });
  });

  it("maps occupancy from booked count, not leftover capacity", () => {
    expect(slotOccupancy(0, 2)).toBe("empty");
    expect(slotOccupancy(1, 2)).toBe("partial");
    expect(slotOccupancy(2, 2)).toBe("full");
    expect(slotOccupancy(1, 3)).toBe("partial");
    expect(slotOccupancy(2, 3)).toBe("partial");
    expect(slotOccupancy(3, 3)).toBe("full");
  });

  it("shows the Jumat half slot with its end time and keeps break occupants listed", async () => {
    mockOrgUnitCode = "PUSAT";
    mockRoles = ["AGENT"];
    fetchHqScheduleAvailabilityDetail.mockResolvedValue({
      data: {
        startTime: "08:00",
        endTime: "16:00",
        slotMinutes: 60,
        capacityPerSlot: 2,
        days: [
          {
            date: "2026-08-21",
            weekday: 5,
            closed: false,
            slots: [
              {
                startTime: "11:00",
                endTime: "11:30",
                capacity: 1,
                isBreak: false,
                partial: true,
                scheduledCount: 0,
                completedCount: 0,
                proposedCount: 0,
                availableCount: 1,
                bookable: true,
                bookableCount: 1,
                pendingProposals: [],
                scheduledCases: [],
              },
              {
                startTime: "11:30",
                endTime: "13:30",
                capacity: 0,
                isBreak: true,
                partial: false,
                scheduledCount: 1,
                completedCount: 0,
                proposedCount: 0,
                availableCount: 0,
                bookable: false,
                bookableCount: 0,
                pendingProposals: [],
                scheduledCases: [
                  {
                    complaintId: "legacy",
                    complaintNumber: "TAB-2608-0011",
                    owningUnitId: "UPPPD-A",
                    unitCode: "TAB",
                    cases: [
                      { caseId: "id-case-2026-000011", caseNumber: "CASE-2026-000011" },
                    ],
                  },
                ],
              },
            ],
          },
        ],
      },
    });
    renderWithProviders(<HqScheduleView />);

    const halfSlot = await screen.findByTestId("hq-schedule-slot-2026-08-21-11:00");
    expect(halfSlot).toHaveTextContent("11:00\u201311:30");
    expect(halfSlot).toHaveTextContent("0/1");

    // Booked before the Jumat window changed — still on the board.
    const breakSlot = screen.getByTestId("hq-schedule-slot-2026-08-21-11:30");
    expect(breakSlot).toHaveTextContent("11:30\u201313:30");
    expect(
      within(breakSlot).getByRole("link", { name: /CASE-2026-000011/ }),
    ).toBeInTheDocument();
  });

  it("shows destination-unit filter chips only for units that have scheduled visits", async () => {
    mockOrgUnitCode = "PUSAT";
    mockRoles = ["AGENT"];
    const user = userEvent.setup();
    fetchHqScheduleAvailabilityDetail.mockResolvedValue({
      data: {
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
                capacity: 4,
                isBreak: false,
                scheduledCount: 2,
                completedCount: 0,
                proposedCount: 0,
                availableCount: 2,
                bookable: false,
                bookableCount: 0,
                pendingProposals: [],
                scheduledCases: [
                  {
                    complaintId: "cro",
                    complaintNumber: "TAB-2608-0020",
                    owningUnitId: "UPPPD-A",
                    unitCode: "TAB",
                    cases: [
                      { caseId: "id-case-2026-000020", caseNumber: "CASE-2026-000020" },
                    ],
                    destinationUnitCode: "PUSAT-CRO",
                  },
                  {
                    complaintId: "legacy",
                    complaintNumber: "TAB-2608-0021",
                    owningUnitId: "UPPPD-A",
                    unitCode: "TAB",
                    cases: [
                      { caseId: "id-case-2026-000021", caseNumber: "CASE-2026-000021" },
                    ],
                    destinationUnitCode: null,
                  },
                ],
                units: [
                  {
                    unitCode: "PUSAT-CRO",
                    unitName: "CRO Pusat",
                    capacity: 2,
                    scheduledCount: 1,
                    completedCount: 0,
                    availableCount: 1,
                    bookable: true,
                  },
                ],
              },
            ],
          },
        ],
      },
    });
    renderWithProviders(<HqScheduleView />);

    const filters = await screen.findByTestId("hq-schedule-unit-filter");
    expect(
      within(filters).getByRole("button", { name: "CRO Pusat" }),
    ).toBeInTheDocument();
    // Suban / Sekretariat are not schedule destinations — chips stay absent.
    expect(
      within(filters).queryByRole("button", { name: "Sekretariat" }),
    ).not.toBeInTheDocument();
    expect(
      within(filters).queryByRole("button", { name: "Suban 1" }),
    ).not.toBeInTheDocument();

    await user.click(within(filters).getByRole("button", { name: "CRO Pusat" }));
    const slot = screen.getByTestId("hq-schedule-slot-2026-08-17-08:00");
    expect(within(slot).getByText(/CASE-2026-000020/)).toBeInTheDocument();
    expect(within(slot).queryByText(/CASE-2026-000021/)).not.toBeInTheDocument();
  });

  it("matches scheduled cases and day breakdown helpers by destination unit", () => {
    const cases = [
      {
        complaintId: "a",
        complaintNumber: "A",
        unitCode: "TAB",
        cases: [
          { caseId: "id-case-a", caseNumber: "CASE-A" },
        ],
        destinationUnitCode: "PUSAT-SEKRETARIAT",
      },
      {
        complaintId: "b",
        complaintNumber: "B",
        unitCode: "TAB",
        cases: [
          { caseId: "id-case-b", caseNumber: "CASE-B" },
        ],
        destinationUnitCode: null,
      },
    ];
    expect(matchingScheduledCases(cases, null)).toHaveLength(2);
    expect(matchingScheduledCases(cases, "PUSAT-SEKRETARIAT")).toHaveLength(1);
    expect(matchingScheduledCases(cases, UNASSIGNED_UNIT_FILTER)).toHaveLength(1);

    const day = {
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
          completedCount: 1,
          proposedCount: 0,
          availableCount: 0,
          bookable: false,
          bookableCount: 0,
          pendingProposals: [],
          scheduledCases: cases.map((c, i) => ({
            ...c,
            completed: i === 0,
          })),
        },
      ],
    };
    expect(dayOccupancyTotals(day, null)).toEqual({ scheduled: 2, completed: 1 });
    expect(dayUnitBreakdown(day)).toEqual([
      { code: "PUSAT-SEKRETARIAT", count: 1 },
      { code: null, count: 1 },
    ]);
  });
});
