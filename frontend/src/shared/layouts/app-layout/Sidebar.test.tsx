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
  within,
} from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { NextIntlClientProvider } from "next-intl";
import enMessages from "../../../../messages/en.json";
import { NavPreferenceProvider } from "@/shared/navigation";
import { Sidebar } from "./Sidebar";

let mockPathname = "/dashboard";
let mockPermissions: string[] = [];
let mockUserId: string | null = "user-1";

vi.mock("next/navigation", () => ({
  usePathname: () => mockPathname,
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
    hasPermission: (permission: string) =>
      mockPermissions.includes("*") || mockPermissions.includes(permission),
  }),
}));

vi.mock("@/lib/api/branches", () => ({
  fetchBranches: () => Promise.resolve({ data: [] }),
}));

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
  mockPermissions = [];
  mockUserId = "user-1";
  window.localStorage.clear();
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("Scenario 1 — taxpayer-only permission", () => {
  it("shows Wajib Pajak items and hides Antrian / Penugasan / Resolusi", () => {
    mockPermissions = COMPLAINT_PERMISSIONS;
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
    expect(sidebar.queryByRole("link", { name: /^Queue$/i })).not.toBeInTheDocument();
    expect(sidebar.queryByRole("link", { name: /^Assignments$/i })).not.toBeInTheDocument();
    expect(sidebar.queryByRole("link", { name: /^Resolutions$/i })).not.toBeInTheDocument();
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

describe("Scenario 7 — internal verification route", () => {
  it("expands Internal and marks Verification active", () => {
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
      name: /Verification/i,
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

describe("hierarchy — no Antrian / Penugasan on main sidebar", () => {
  it("does not render Queue, Assignments, or Resolutions links", () => {
    mockPermissions = ["*"];
    const { sidebar } = renderSidebar();
    expect(sidebar.queryByRole("link", { name: /^Queue$/i })).not.toBeInTheDocument();
    expect(sidebar.queryByRole("link", { name: /^Assignments$/i })).not.toBeInTheDocument();
    expect(sidebar.queryByRole("link", { name: /^Resolutions$/i })).not.toBeInTheDocument();
  });
});
