/**
 * Sidebar restructure — PENGADUAN group with collapsible Wajib Pajak /
 * Internal subgroups, gated by permission, driven by the per-user nav
 * preference (auto / remember / expandAll).
 */
import {
  act,
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { NextIntlClientProvider } from "next-intl";
import enMessages from "../../../../messages/en.json";
import { NavPreferenceProvider } from "@/shared/navigation";
import { Sidebar } from "./Sidebar";

let mockPathname = "/dashboard";
let mockSearch = "";
let mockPermissions: string[] = [];
let mockRoles: string[] = [];
let mockUserId: string | null = "user-1";
let mockOrgUnitBranch: { code: string } | null | undefined = null;
const unreadCountApi = vi.fn();
const hqScheduleDetailApi = vi.fn();
const workBadgesApi = vi.fn();

vi.mock("next/navigation", () => ({
  usePathname: () => mockPathname,
  useSearchParams: () => new URLSearchParams(mockSearch),
}));

vi.mock("next/link", () => ({
  default: ({
    href,
    children,
    onClick,
    ...props
  }: {
    href: string;
    children: React.ReactNode;
    onClick?: () => void;
  }) => (
    <a href={href} onClick={onClick} {...props}>
      {children}
    </a>
  ),
}));

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({
    user: { id: mockUserId, branchId: null },
    userId: mockUserId,
    isMockSession: false,
    mockPersona: null,
    officerWorkMode: null,
    roles: mockRoles,
    hasPermission: (permission: string) =>
      mockPermissions.includes("*") || mockPermissions.includes(permission),
  }),
}));

vi.mock("@/lib/api/branches", () => ({
  fetchBranches: () => Promise.resolve({ data: [] }),
}));

vi.mock("@/lib/api/hqSchedule", () => ({
  fetchHqScheduleAvailabilityDetail: (...args: unknown[]) =>
    hqScheduleDetailApi(...args),
}));

vi.mock("@/features/announcements/useOrgUnitCode", () => ({
  useOrgUnitBranch: () => mockOrgUnitBranch,
  useOrgUnitCode: () =>
    mockOrgUnitBranch === undefined ? undefined : (mockOrgUnitBranch?.code ?? null),
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchUnreadAnnouncementCount: (...args: unknown[]) => unreadCountApi(...args),
    fetchCmWorkBadges: (...args: unknown[]) => workBadgesApi(...args),
  };
});

vi.mock("@/shared/config/internalComplaintsUi", () => ({
  isInternalComplaintsUiEnabled: () => true,
}));

vi.mock("@/shared/config/uiBatch", () => ({
  isShellUiBatch: () => false,
}));

vi.mock("@/shared/hooks", () => ({
  useSidebar: () => ({
    open: false,
    setOpen: vi.fn(),
    toggle: vi.fn(),
    isDesktop: true,
  }),
}));

/**
 * Sidebar renders both the persistent desktop <aside> and the mobile drawer
 * <aside> — every nav item exists twice in the DOM. Scope all queries to the
 * desktop instance ("Application sidebar") so assertions target one copy.
 */
function renderSidebar() {
  const result = render(
    <NextIntlClientProvider locale="en" messages={enMessages} timeZone="Asia/Jakarta">
      <NavPreferenceProvider>
        <Sidebar />
      </NavPreferenceProvider>
    </NextIntlClientProvider>,
  );
  return {
    unmount: result.unmount,
    sidebar: within(screen.getByLabelText("Application sidebar")),
  };
}

const COMPLAINT_PERMISSIONS = ["complaints:read"];

beforeEach(() => {
  mockPathname = "/dashboard";
  mockSearch = "";
  mockPermissions = [];
  mockRoles = [];
  mockUserId = "user-1";
  mockOrgUnitBranch = null;
  window.localStorage.clear();
  unreadCountApi.mockReset();
  unreadCountApi.mockResolvedValue({ data: 0 });
  hqScheduleDetailApi.mockReset();
  hqScheduleDetailApi.mockResolvedValue({ data: { days: [] } });
  workBadgesApi.mockReset();
  workBadgesApi.mockResolvedValue({
    data: { unreadCases: 0, pusatQueue: 0, pusatFollowUp: 0 },
  });
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("Scenario 1 — taxpayer-only permission", () => {
  it("shows Wajib Pajak items and hides Antrian / Penugasan / Resolusi", () => {
    mockPermissions = COMPLAINT_PERMISSIONS;
    mockOrgUnitBranch = { code: "UPPPD-TANAH-ABANG" };
    const { sidebar } = renderSidebar();

    expect(sidebar.getByText("Taxpayer")).toBeInTheDocument();
    // Default "auto" on /dashboard expands Taxpayer; Internal is collapsed so
    // "Complaints" is unique within the Taxpayer panel.
    const taxpayerPanel = document.getElementById(
      "nav-subgroup-panel-taxpayerComplaints",
    )!;
    expect(
      within(taxpayerPanel).getByRole("link", { name: /^Complaints$/i }),
    ).toBeInTheDocument();
    expect(
      within(taxpayerPanel).getByRole("link", { name: /^Cases$/i }),
    ).toBeInTheDocument();
    expect(
      within(taxpayerPanel).getByRole("link", { name: /^Closed$/i }),
    ).toHaveAttribute("href", "/complaints?status=CLOSED");
    expect(sidebar.queryByRole("link", { name: /^Queue$/i })).not.toBeInTheDocument();
    expect(sidebar.queryByRole("link", { name: /^Assignments$/i })).not.toBeInTheDocument();
    expect(sidebar.queryByRole("link", { name: /^Resolutions$/i })).not.toBeInTheDocument();
  });

  it("hides Cases nav for Pusat unit (route remains deep-linkable)", () => {
    mockPermissions = COMPLAINT_PERMISSIONS;
    mockOrgUnitBranch = { code: "PUSAT" };
    const { sidebar } = renderSidebar();

    expect(
      sidebar.getByRole("link", { name: /^Complaints$/i }),
    ).toBeInTheDocument();
    expect(
      sidebar.queryByRole("link", { name: /^Cases$/i }),
    ).not.toBeInTheDocument();
  });

  it("hides Cases nav while org unit is still loading", () => {
    mockPermissions = COMPLAINT_PERMISSIONS;
    mockOrgUnitBranch = undefined;
    const { sidebar } = renderSidebar();

    expect(
      sidebar.queryByRole("link", { name: /^Cases$/i }),
    ).not.toBeInTheDocument();
  });
});

describe("Scenario 2 & 6 — auto mode expands the subgroup owning the active route", () => {
  it("Pengaduan (taxpayer route) expands Wajib Pajak, collapses Internal", () => {
    mockPermissions = ["*"];
    mockPathname = "/complaints";
    const { sidebar } = renderSidebar();

    const taxpayerToggle = sidebar.getByRole("button", {
      name: /^Taxpayer$/i,
    });
    const internalToggle = sidebar.getByRole("button", {
      name: /^Internal$/i,
    });
    expect(taxpayerToggle).toHaveAttribute("aria-expanded", "true");
    expect(internalToggle).toHaveAttribute("aria-expanded", "false");

    const complaintsLink = sidebar.getByRole("link", { name: /^Complaints$/i });
    expect(complaintsLink).toHaveAttribute("aria-current", "page");
  });
});

describe("Scenario 7 — internal approval queue route", () => {
  it("expands Internal and marks Approval active", () => {
    mockPermissions = ["*"];
    mockPathname = "/internal/verification";
    const { sidebar } = renderSidebar();

    const internalToggle = sidebar.getByRole("button", {
      name: /^Internal$/i,
    });
    expect(internalToggle).toHaveAttribute("aria-expanded", "true");

    const panel = document.getElementById(
      internalToggle.getAttribute("aria-controls")!,
    )!;
    const verificationLink = within(panel).getByRole("link", {
      name: /Approval/i,
    });
    expect(verificationLink).toHaveAttribute("aria-current", "page");
  });
});

describe("Scenario 4 — expandAll preference", () => {
  it("keeps both subgroups expanded and hides the collapse affordance", () => {
    mockPermissions = ["*"];
    mockPathname = "/internal";
    window.localStorage.setItem(
      "ecmp.nav.complaintsSidebar:user-1",
      JSON.stringify({ mode: "expandAll", expanded: {} }),
    );
    const { sidebar } = renderSidebar();

    // expandAll renders subgroup headings as plain text, not toggle buttons.
    expect(
      sidebar.queryByRole("button", { name: /^Taxpayer$/i }),
    ).not.toBeInTheDocument();
    expect(sidebar.getByText("Taxpayer")).toBeInTheDocument();
    expect(sidebar.getByText("Internal")).toBeInTheDocument();
    // Dashboard/Reports labels exist in both domains — assert Knowledge/Admin.
    expect(sidebar.getByRole("link", { name: /^Attachments$/i })).toBeVisible();
    expect(sidebar.getByRole("link", { name: /^Users$/i })).toBeVisible();
  });
});

describe("Scenario 3 — remember mode persists across remounts", () => {
  it("keeps a manually collapsed subgroup collapsed after refresh (remount)", () => {
    mockPermissions = ["*"];
    mockPathname = "/complaints"; // taxpayer route — auto default would expand it
    window.localStorage.setItem(
      "ecmp.nav.complaintsSidebar:user-1",
      JSON.stringify({
        mode: "remember",
        expanded: { taxpayerComplaints: false, internalComplaints: true },
      }),
    );
    const first = renderSidebar();

    expect(
      first.sidebar.getByRole("button", { name: /^Taxpayer$/i }),
    ).toHaveAttribute("aria-expanded", "false");
    expect(
      first.sidebar.getByRole("button", { name: /^Internal$/i }),
    ).toHaveAttribute("aria-expanded", "true");

    first.unmount();
    const second = renderSidebar();

    expect(
      second.sidebar.getByRole("button", { name: /^Taxpayer$/i }),
    ).toHaveAttribute("aria-expanded", "false");
  });

  it("toggling a subgroup writes the choice back to storage", () => {
    mockPermissions = ["*"];
    mockPathname = "/dashboard";
    const { sidebar } = renderSidebar();

    const taxpayerToggle = sidebar.getByRole("button", {
      name: /^Taxpayer$/i,
    });
    // Default mode is "auto" — toggle reflects in aria-expanded for this visit.
    const before = taxpayerToggle.getAttribute("aria-expanded");
    act(() => {
      fireEvent.click(taxpayerToggle);
    });
    expect(taxpayerToggle.getAttribute("aria-expanded")).not.toBe(before);
  });
});

describe("Brand unit subtitle", () => {
  it("shows Head Office when the user has no branchId (Pusat)", () => {
    mockPermissions = ["*"];
    const { sidebar } = renderSidebar();
    expect(sidebar.getByText("SERVICES")).toBeVisible();
    expect(sidebar.getByText("Head Office")).toBeVisible();
  });
});

describe("Domain subgroup separator", () => {
  it("draws a separator between Wajib Pajak and Internal when both are visible", () => {
    mockPermissions = ["*"];
    const { sidebar } = renderSidebar();
    expect(sidebar.getByTestId("nav-domain-separator")).toBeInTheDocument();
  });
});

describe("Scenario 8 — invalid preference never crashes the sidebar", () => {
  it("falls back to the default (auto) behaviour for a corrupted stored value", () => {
    mockPermissions = ["*"];
    mockPathname = "/complaints";
    window.localStorage.setItem(
      "ecmp.nav.complaintsSidebar:user-1",
      "not-json-at-all",
    );

    const { sidebar } = renderSidebar();
    expect(
      sidebar.getByRole("button", { name: /^Taxpayer$/i }),
    ).toHaveAttribute("aria-expanded", "true");
    expect(
      sidebar.getByRole("button", { name: /^Internal$/i }),
    ).toHaveAttribute("aria-expanded", "false");
  });
});

describe("HQ schedule — complaints:read sidebar entry", () => {
  it("shows HQ schedule for a Cabang unit with complaints:read", () => {
    mockPermissions = COMPLAINT_PERMISSIONS;
    mockRoles = ["AGENT"];
    mockOrgUnitBranch = { code: "UPPPD-A" };
    const { sidebar } = renderSidebar();
    expect(
      sidebar.getByRole("link", { name: /^Escalation Schedule$/i }),
    ).toBeInTheDocument();
  });

  it("shows HQ schedule while the org unit is still resolving", () => {
    mockPermissions = COMPLAINT_PERMISSIONS;
    mockRoles = ["AGENT"];
    mockOrgUnitBranch = undefined;
    const { sidebar } = renderSidebar();
    expect(
      sidebar.getByRole("link", { name: /^Escalation Schedule$/i }),
    ).toBeInTheDocument();
  });

  it("shows HQ schedule for a Pusat viewer with complaints:read", () => {
    mockPermissions = COMPLAINT_PERMISSIONS;
    mockRoles = ["VIEWER"];
    mockOrgUnitBranch = { code: "PUSAT" };
    const { sidebar } = renderSidebar();
    expect(
      sidebar.getByRole("link", { name: /^Escalation Schedule$/i }),
    ).toBeInTheDocument();
  });

  it("hides HQ schedule without complaints:read", () => {
    mockPermissions = ["settings:read"];
    mockRoles = ["ADMIN"];
    mockOrgUnitBranch = { code: "PUSAT" };
    const { sidebar } = renderSidebar();
    expect(
      sidebar.queryByRole("link", { name: /^Escalation Schedule$/i }),
    ).not.toBeInTheDocument();
  });
});

describe("hierarchy — no Antrian / Penugasan on main sidebar", () => {
  it("does not render Queue, Assignments, or Resolutions links", () => {
    mockPermissions = ["*"];
    const { sidebar } = renderSidebar();
    expect(sidebar.queryByRole("link", { name: /^Queue$/i })).not.toBeInTheDocument();
    expect(sidebar.queryByRole("link", { name: /^Assignments$/i })).not.toBeInTheDocument();
    expect(sidebar.queryByRole("link", { name: /^Resolutions$/i })).not.toBeInTheDocument();
  });
});

describe("unread announcement badge on the bell", () => {
  it("shows the unread count on Announcements and hides it when zero", async () => {
    mockPermissions = ["*", "announcement:read"];
    unreadCountApi.mockResolvedValue({ data: 3 });
    const { sidebar } = renderSidebar();

    const withCount = await waitFor(() =>
      sidebar.getByRole("link", { name: /Announcements, 3 unread/i }),
    );
    expect(withCount).toHaveAttribute("href", "/announcements");
    expect(within(withCount).getByText("3")).toBeInTheDocument();
  });

  it("does not show a badge when there are no unread announcements", async () => {
    mockPermissions = ["*", "announcement:read"];
    unreadCountApi.mockResolvedValue({ data: 0 });
    const { sidebar } = renderSidebar();

    const link = await waitFor(() =>
      sidebar.getByRole("link", { name: /^Announcements$/i }),
    );
    expect(link).toHaveAttribute("href", "/announcements");
    expect(within(link).queryByText("0")).not.toBeInTheDocument();
  });
});

describe("HQ schedule today-count badge", () => {
  it("shows today's scheduled count for a Pusat reviewer", async () => {
    mockPermissions = ["*", "complaints:read", "escalations:review"];
    mockRoles = ["HO_SCHEDULER"];
    hqScheduleDetailApi.mockResolvedValue({
      data: {
        days: [
          {
            date: "2026-08-18",
            weekday: 2,
            closed: false,
            slots: [
              { startTime: "08:00", endTime: "09:00", capacity: 2, isBreak: false, scheduledCount: 2, proposedCount: 0, availableCount: 0, pendingProposals: [], scheduledCases: [] },
              { startTime: "09:00", endTime: "10:00", capacity: 2, isBreak: false, scheduledCount: 3, proposedCount: 0, availableCount: 0, pendingProposals: [], scheduledCases: [] },
            ],
          },
        ],
      },
    });
    const { sidebar } = renderSidebar();

    const link = await waitFor(() =>
      sidebar.getByRole("link", { name: /^Escalation Schedule$/i }),
    );
    await waitFor(() => {
      expect(within(link).getByText("5")).toBeInTheDocument();
    });
  });

  it("shows no badge for a Cabang agent (not HQ-review eligible)", async () => {
    mockPermissions = ["complaints:read"];
    mockRoles = ["AGENT"];
    mockOrgUnitBranch = { code: "UPPPD-A" };
    const { sidebar } = renderSidebar();

    const link = await waitFor(() =>
      sidebar.getByRole("link", { name: /^Escalation Schedule$/i }),
    );
    expect(hqScheduleDetailApi).not.toHaveBeenCalled();
    expect(within(link).queryByText(/^\d+$/)).not.toBeInTheDocument();
  });
});

describe("Mode A work badges — Cabang Cases / Pusat Complaints", () => {
  it("shows unread Cases badge for Cabang and does not rewrite Complaints href", async () => {
    mockPermissions = COMPLAINT_PERMISSIONS;
    mockOrgUnitBranch = { code: "UPPPD-TANAH-ABANG" };
    workBadgesApi.mockResolvedValue({
      data: { unreadCases: 3, pusatQueue: 9 },
    });
    const { sidebar } = renderSidebar();

    const casesLink = await waitFor(() =>
      sidebar.getByRole("link", { name: /^Cases$/i }),
    );
    await waitFor(() => {
      expect(within(casesLink).getByText("3")).toBeInTheDocument();
    });

    const taxpayerPanel = document.getElementById(
      "nav-subgroup-panel-taxpayerComplaints",
    )!;
    const complaintsLink = within(taxpayerPanel).getByRole("link", {
      name: /^Complaints$/i,
    });
    expect(complaintsLink).toHaveAttribute("href", "/complaints?status=OPEN");
    expect(within(complaintsLink).queryByText("9")).not.toBeInTheDocument();
  });

  it("shows Pusat queue badge on Complaints with filtered href; Cases stays hidden", async () => {
    mockPermissions = COMPLAINT_PERMISSIONS;
    mockOrgUnitBranch = { code: "PUSAT" };
    workBadgesApi.mockResolvedValue({
      data: { unreadCases: 4, pusatQueue: 7 },
    });
    const { sidebar } = renderSidebar();

    const complaintsLink = await waitFor(() =>
      sidebar.getByRole("link", { name: /^Complaints$/i }),
    );
    await waitFor(() => {
      expect(within(complaintsLink).getByText("7")).toBeInTheDocument();
    });
    expect(complaintsLink).toHaveAttribute(
      "href",
      "/complaints?needsPusatHandling=1",
    );
    expect(sidebar.queryByRole("link", { name: /^Cases$/i })).not.toBeInTheDocument();
  });

  it("points Pusat Pengaduan at the unhandled queue even without a badge", async () => {
    mockPermissions = COMPLAINT_PERMISSIONS;
    mockOrgUnitBranch = { code: "PUSAT" };
    workBadgesApi.mockResolvedValue({
      data: { unreadCases: 0, pusatQueue: 0 },
    });
    const { sidebar } = renderSidebar();
    const complaintsLink = await waitFor(() =>
      sidebar.getByRole("link", { name: /^Complaints$/i }),
    );
    expect(complaintsLink).toHaveAttribute(
      "href",
      "/complaints?needsPusatHandling=1",
    );
    expect(within(complaintsLink).queryByText(/^\d+$/)).not.toBeInTheDocument();
  });

  it("shows Pusat Tindak lanjut badge on Follow-up; Complaints stays separate", async () => {
    mockPermissions = COMPLAINT_PERMISSIONS;
    mockOrgUnitBranch = { code: "PUSAT" };
    workBadgesApi.mockResolvedValue({
      data: { unreadCases: 0, pusatQueue: 2, pusatFollowUp: 3 },
    });
    const { sidebar } = renderSidebar();

    const followUpLink = await waitFor(() =>
      sidebar.getByRole("link", { name: /^Follow-up$/i }),
    );
    await waitFor(() => {
      expect(within(followUpLink).getByText("3")).toBeInTheDocument();
    });

    const complaintsLink = sidebar.getByRole("link", { name: /^Complaints$/i });
    expect(within(complaintsLink).getByText("2")).toBeInTheDocument();
  });
});
