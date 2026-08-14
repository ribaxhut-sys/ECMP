/**
 * UM-SEC-001 TASK 4 — Credential Surface removal.
 *
 * Confirms the User Management screen never renders a Reset Password
 * affordance, never puts a plaintext credential into the DOM, and does not
 * offer Print/Copy. This is a regression lock, not a redesign: none of these
 * verify a *new* feature, only the absence of the removed one.
 */
import { cleanup, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";
import type { UserRef } from "@/lib/api";

const fetchUsers = vi.fn();
const fetchAllUsers = vi.fn();
const fetchRoles = vi.fn();
const fetchBranches = vi.fn();
const updateUserStatus = vi.fn();
const updateUserRole = vi.fn();
let authRoles = ["ADMIN"];
let authBranchId: string | null = null;
const hasPermission = vi.fn((code: string) =>
  ["users:read", "users:create", "users:update"].includes(code),
);

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), back: vi.fn() }),
}));

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({
    user: { branchId: authBranchId },
    userId: "current-user",
    roles: authRoles,
    hasPermission,
  }),
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    fetchUsers: (...args: unknown[]) => fetchUsers(...args),
    fetchAllUsers: (...args: unknown[]) => fetchAllUsers(...args),
    fetchRoles: (...args: unknown[]) => fetchRoles(...args),
    fetchBranches: (...args: unknown[]) => fetchBranches(...args),
    updateUserStatus: (...args: unknown[]) => updateUserStatus(...args),
    updateUserRole: (...args: unknown[]) => updateUserRole(...args),
  };
});

import { UserManagement } from "./UserManagement";

const ROWS: UserRef[] = [
  {
    id: "u-1",
    username: "3100000000000099",
    email: "member@example.com",
    fullName: "Member One",
    roleId: "r-1",
    roleCode: "AGENT",
    roleName: "Agent",
    branchId: "b-1",
    isActive: true,
    lastLoginAt: "2026-08-01T00:00:00Z",
    createdAt: "2026-01-01T00:00:00Z",
    updatedAt: "2026-08-01T00:00:00Z",
  },
];

function role(id: string, code: string, name: string) {
  return { id, code, name, description: null, isSystem: false, isActive: true };
}

describe("UserManagement — credential surface removed", () => {
  afterEach(() => cleanup());

  beforeEach(() => {
    fetchUsers.mockReset();
    fetchAllUsers.mockReset();
    fetchRoles.mockReset();
    fetchBranches.mockReset();
    updateUserStatus.mockReset();
    updateUserRole.mockReset();
    authRoles = ["ADMIN"];
    authBranchId = null;
    hasPermission.mockImplementation((code: string) =>
      ["users:read", "users:create", "users:update"].includes(code),
    );
    fetchUsers.mockResolvedValue({ data: ROWS, meta: { totalItems: 1 } });
    fetchAllUsers.mockResolvedValue(ROWS);
    fetchRoles.mockResolvedValue([
      role("r-1", "AGENT", "Agent"),
      role("r-2", "SUPERVISOR", "Supervisor"),
      role("r-3", "ADMIN", "Administrator"),
    ]);
    fetchBranches.mockResolvedValue({
      data: [
        { id: "b-1", code: "OU-A", name: "Regional Jawa Barat" },
        { id: "b-pusat", code: "PUSAT", name: "Pusat" },
      ],
    });
    updateUserStatus.mockResolvedValue({ ...ROWS[0], isActive: false });
    updateUserRole.mockResolvedValue({
      ...ROWS[0],
      roleId: "r-2",
      roleCode: "SUPERVISOR",
      roleName: "Supervisor",
    });
  });

  it("never renders a Reset Password action anywhere on the screen", async () => {
    renderWithProviders(<UserManagement />);
    await waitFor(() => expect(fetchAllUsers).toHaveBeenCalled());
    await screen.findByText("Member One");

    expect(
      screen.queryByRole("button", { name: /reset password/i }),
    ).toBeNull();
    expect(screen.queryByText(/temporary password/i)).toBeNull();
    expect(screen.queryByRole("button", { name: /^print$/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /^copy$/i })).toBeNull();
  });

  it("selecting a member never exposes a credential in the DOM", async () => {
    const user = userEvent.setup();
    renderWithProviders(<UserManagement />);
    await waitFor(() => expect(fetchAllUsers).toHaveBeenCalled());
    const row = await screen.findByText("Member One");
    await user.click(row);

    const preview = await screen.findByLabelText(/preview/i);
    expect(
      within(preview).queryByRole("button", { name: /reset password/i }),
    ).toBeNull();
    // Role and Status remain visible — membership data, not credentials.
    expect(within(preview).getByText(/Officer/i)).toBeInTheDocument();
    expect(within(preview).queryByText("member@example.com")).toBeNull();
  });

  it("still renders membership data (Role, Status) without any credential UI", async () => {
    renderWithProviders(<UserManagement />);
    await waitFor(() => expect(fetchAllUsers).toHaveBeenCalled());
    await screen.findByText("Member One");
    expect(document.body.textContent).not.toMatch(/temporary password/i);
  });

  it("shows Unit code and activates or deactivates from the preview", async () => {
    const user = userEvent.setup();
    renderWithProviders(<UserManagement />);
    await screen.findByText("Member One");

    expect(screen.getByText("OU-A")).toBeInTheDocument();
    expect(screen.getByText(/Role \/ Unit|Peran \/ Unit/i)).toBeInTheDocument();

    await user.click(screen.getByText("Member One"));
    const preview = await screen.findByLabelText(/preview/i);
    expect(within(preview).getByText("Unit")).toBeInTheDocument();
    expect(within(preview).getByText("OU-A")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Deactivate" }));
    const dialog = screen.getByRole("dialog");
    await user.click(within(dialog).getByRole("button", { name: "Deactivate" }));

    await waitFor(() =>
      expect(updateUserStatus).toHaveBeenCalledWith("u-1", false),
    );
    expect(screen.getAllByText("Inactive").length).toBeGreaterThan(0);
  });

  it("exposes status actions to SUPER_ADMIN", async () => {
    authRoles = ["SUPER_ADMIN"];
    const user = userEvent.setup();
    renderWithProviders(<UserManagement />);
    await user.click(await screen.findByText("Member One"));

    expect(
      screen.getByRole("button", { name: "Deactivate" }),
    ).toBeInTheDocument();
  });

  it("does not expose status actions to non-admin roles", async () => {
    authRoles = ["SUPERVISOR"];
    const user = userEvent.setup();
    renderWithProviders(<UserManagement />);
    await user.click(await screen.findByText("Member One"));

    expect(
      screen.queryByRole("button", { name: "Deactivate" }),
    ).toBeNull();
    expect(
      screen.queryByRole("button", { name: "Change role" }),
    ).toBeNull();
    expect(updateUserStatus).not.toHaveBeenCalled();
  });

  it("exposes status actions to Manager for a same-branch member, but not role change", async () => {
    // UM-BUG-007 — Member One is branchId "b-1"; Manager shares that branch.
    authRoles = ["MANAGER"];
    authBranchId = "b-1";
    const user = userEvent.setup();
    renderWithProviders(<UserManagement />);
    await user.click(await screen.findByText("Member One"));

    expect(
      screen.getByRole("button", { name: "Deactivate" }),
    ).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Change role" })).toBeNull();
  });

  it("does not expose status actions to Manager for a different branch", async () => {
    authRoles = ["MANAGER"];
    authBranchId = "b-other";
    const user = userEvent.setup();
    renderWithProviders(<UserManagement />);
    await user.click(await screen.findByText("Member One"));

    expect(screen.queryByRole("button", { name: "Deactivate" })).toBeNull();
    expect(updateUserStatus).not.toHaveBeenCalled();
  });

  it("changes a branch member's role and keeps their directory unit", async () => {
    const user = userEvent.setup();
    renderWithProviders(<UserManagement />);
    await user.click(await screen.findByText("Member One"));
    await user.click(screen.getByRole("button", { name: "Change role" }));

    const dialog = screen.getByRole("dialog");
    await user.selectOptions(within(dialog).getByLabelText("New role"), "r-2");
    await user.click(
      within(dialog).getByRole("button", { name: "Change role" }),
    );

    await waitFor(() =>
      expect(updateUserRole).toHaveBeenCalledWith("u-1", "r-2", "b-1"),
    );
  });

  it("hides head-office roles when changing role for a branch member", async () => {
    const user = userEvent.setup();
    renderWithProviders(<UserManagement />);
    await user.click(await screen.findByText("Member One"));
    await user.click(screen.getByRole("button", { name: "Change role" }));

    const dialog = screen.getByRole("dialog");
    const roleField = within(dialog).getByLabelText("New role");
    expect(within(roleField).getByRole("option", { name: /SUPERVISOR/ })).toBeInTheDocument();
    expect(within(roleField).queryByRole("option", { name: /ADMIN/ })).toBeNull();
  });

  it("offers operational roles when changing role for a Pusat member", async () => {
    fetchAllUsers.mockResolvedValue([
      {
        ...ROWS[0]!,
        id: "u-ho",
        username: "3100000000000001",
        fullName: "Pusat Admin",
        roleId: "r-3",
        roleCode: "ADMIN",
        roleName: "Administrator",
        branchId: null,
      },
    ]);
    const user = userEvent.setup();
    renderWithProviders(<UserManagement />);
    await user.click(await screen.findByText("Pusat Admin"));
    await user.click(screen.getByRole("button", { name: "Change role" }));

    const dialog = screen.getByRole("dialog");
    const roleField = within(dialog).getByLabelText("New role");
    // Pusat keeps operational personas; current ADMIN is excluded from the list.
    expect(within(roleField).getByRole("option", { name: /AGENT/ })).toBeInTheDocument();
    expect(within(roleField).getByRole("option", { name: /SUPERVISOR/ })).toBeInTheDocument();
  });

  it("does not render density or hide-email controls", async () => {
    renderWithProviders(<UserManagement />);
    await waitFor(() => expect(fetchAllUsers).toHaveBeenCalled());
    await screen.findByText("Member One");
    expect(screen.queryByRole("button", { name: /comfortable|nyaman/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /compact|padat/i })).toBeNull();
    expect(
      screen.queryByRole("button", { name: /hide email|sembunyikan email/i }),
    ).toBeNull();
    expect(screen.queryByText(/member@example.com/i)).toBeNull();
  });

  it("Register User modal never exposes Temporary Password UI", async () => {
    const user = userEvent.setup();
    renderWithProviders(<UserManagement />);
    await waitFor(() => expect(fetchAllUsers).toHaveBeenCalled());
    await user.click(screen.getByRole("button", { name: /register user/i }));
    await screen.findByLabelText(/Search candidate/i);
    expect(screen.queryByLabelText(/Temporary password/i)).toBeNull();
    expect(screen.queryByText(/temporary password/i)).toBeNull();
    expect(document.body.textContent).not.toMatch(/temporary password/i);
  });

  it("still shows own-branch members when the branch reference list 403s (Manager, BC-8.4)", async () => {
    // Manager has users:read but not complaints:read, which GET /api/v1/branches
    // requires. That must not blank out the primary member directory.
    fetchBranches.mockRejectedValue(
      Object.assign(new Error("Forbidden"), { status: 403, code: "FORBIDDEN" }),
    );
    renderWithProviders(<UserManagement />);
    await waitFor(() => expect(fetchAllUsers).toHaveBeenCalled());
    await screen.findByText("Member One");
    expect(screen.queryByText(/tidak memiliki izin|unable to load/i)).toBeNull();
  });

  it("paginates the directory with 10 / 20 / 50 page size", async () => {
    const user = userEvent.setup();
    const many = Array.from({ length: 25 }, (_, i) => ({
      ...ROWS[0]!,
      id: `u-${i + 1}`,
      username: `user${String(i + 1).padStart(2, "0")}`,
      fullName: `Member ${i + 1}`,
    }));
    fetchAllUsers.mockResolvedValue(many);

    renderWithProviders(<UserManagement />);
    await screen.findByText("Member 1");
    expect(screen.getByText("Member 10")).toBeInTheDocument();
    expect(screen.queryByText("Member 11")).not.toBeInTheDocument();

    const pageSize = screen.getByLabelText(/show per page|tampilkan per halaman/i);
    expect(within(pageSize).getByRole("option", { name: /10/ })).toBeInTheDocument();
    expect(within(pageSize).getByRole("option", { name: /20/ })).toBeInTheDocument();
    expect(within(pageSize).getByRole("option", { name: /50/ })).toBeInTheDocument();

    await user.selectOptions(pageSize, "20");
    await waitFor(() =>
      expect(screen.getByText("Member 20")).toBeInTheDocument(),
    );
    expect(screen.queryByText("Member 21")).not.toBeInTheDocument();

    const nav = screen.getByRole("navigation", { name: /pagination/i });
    await user.click(within(nav).getByRole("button", { name: /next|berikutnya/i }));
    await waitFor(() =>
      expect(screen.getByText("Member 21")).toBeInTheDocument(),
    );
    expect(screen.queryByText("Member 1")).not.toBeInTheDocument();
  });
});
