/**
 * HQ schedule calendar — Cabang uses the aggregate API; Pusat uses detail.
 */
import { cleanup, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";
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

import { HqScheduleView } from "./HqScheduleView";

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

  it("lists the week's escalations grouped by weekday and time below the table", async () => {
    mockOrgUnitCode = "PUSAT";
    fetchHqScheduleAvailabilityDetail.mockResolvedValue({ data: gridWithCases() });
    renderWithProviders(<HqScheduleView />);

    const heading = await screen.findByText("This week's escalations");
    const section = heading.closest("section")!;
    expect(within(section).getByText("Senin")).toBeInTheDocument();
    expect(within(section).getByText("08:00")).toBeInTheDocument();
    expect(within(section).getByText(/CASE-2026-000001/)).toBeInTheDocument();
    expect(within(section).getByText(/CASE-2026-000002/)).toBeInTheDocument();
    expect(within(section).getByText(/\(TAB\)/)).toBeInTheDocument();
    expect(within(section).getByText(/\(GAM\)/)).toBeInTheDocument();
  });

  it("shows an empty state in the weekly list when nothing is scheduled", async () => {
    renderWithProviders(<HqScheduleView />);
    expect(
      await screen.findByText("No escalations scheduled this week."),
    ).toBeInTheDocument();
  });

  it("hides the ratio badge once a slot is full, but shows it while there's room", async () => {
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
    expect(screen.queryByText("2/2 slot")).not.toBeInTheDocument();
    expect(screen.getByText("0/2 slot")).toBeInTheDocument();
  });

  it("tags a break slot instead of showing case data", async () => {
    fetchHqScheduleAvailability.mockResolvedValue({ data: gridWithCases() });
    renderWithProviders(<HqScheduleView />);

    expect(await screen.findByText("Break")).toBeInTheDocument();
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

    await screen.findByText("Break");
    expect(screen.queryByText("2026-08-22")).not.toBeInTheDocument();
    expect(screen.queryByText("2026-08-23")).not.toBeInTheDocument();
    expect(screen.getAllByText("Break")).toHaveLength(1);
  });

  it("imports the fixed-date national holidays for the selected year", async () => {
    hasPermission.mockImplementation((permission: string) =>
      ["complaints:read", "settings:read", "settings:update"].includes(permission),
    );
    const user = userEvent.setup();
    renderWithProviders(<HqScheduleView />);

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
});
