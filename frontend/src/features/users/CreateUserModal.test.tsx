/**
 * UX-CU-003 — Enterprise User Membership registration.
 *
 * Covers the four behaviours the milestone turns on: search the Mock Enterprise
 * Directory, select a user, keep Enterprise identity read-only, and save ECMP
 * authorization data (role / unit / status) with Unit taken from the
 * candidate's Enterprise Directory home unit rather than chosen.
 *
 * Temporary Password is not rendered — credential surfaces are outside ECMP
 * product UI (SEC-PWD-001 / UX-UM-001).
 */
import { cleanup, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";
import {
  MODULE_USER_CANDIDATES,
  isHeadOfficeCandidate,
} from "./moduleUserCandidates";

const ADMIN_BRANCH_ID = "b1111111-1111-1111-1111-111111111111";
const OTHER_BRANCH_ID = "b2222222-2222-2222-2222-222222222222";
/** ECMP branch matching the candidate's Enterprise Directory home unit code. */
const CANDIDATE_BRANCH_ID = "b3333333-3333-3333-3333-333333333333";
const PUSAT_BRANCH_ID = "b4444444-4444-4444-4444-444444444444";
const AGENT_ROLE_ID = "r1111111-1111-1111-1111-111111111111";
const ADMIN_ROLE_ID = "r2222222-2222-2222-2222-222222222222";
const SUPERVISOR_ROLE_ID = "r3333333-3333-3333-3333-333333333333";

const createUser = vi.fn();
const fetchRoles = vi.fn();
const fetchBranches = vi.fn();
const fetchUsers = vi.fn();

let adminBranchId: string | null = ADMIN_BRANCH_ID;

vi.mock("@/auth/AuthProvider", () => ({
  useAuth: () => ({
    user: { branchId: adminBranchId },
    hasPermission: () => true,
  }),
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    createUser: (...args: unknown[]) => createUser(...args),
    fetchRoles: (...args: unknown[]) => fetchRoles(...args),
    fetchBranches: (...args: unknown[]) => fetchBranches(...args),
    fetchUsers: (...args: unknown[]) => fetchUsers(...args),
  };
});

import { CreateUserModal, MODE_A_LAB_TEMP_PASSWORD } from "./CreateUserModal";

const CANDIDATE = MODULE_USER_CANDIDATES[0]!;
const HEAD_OFFICE_CANDIDATE = MODULE_USER_CANDIDATES.find(isHeadOfficeCandidate)!;

function renderModal() {
  const onCreated = vi.fn();
  const onClose = vi.fn();
  renderWithProviders(
    <CreateUserModal open onClose={onClose} onCreated={onCreated} />,
  );
  return { onCreated, onClose };
}

/** Search + select the first Mock Enterprise Directory row. */
async function selectCandidate(user: ReturnType<typeof userEvent.setup>) {
  const search = await screen.findByLabelText(/Search candidate/i);
  await user.type(search, CANDIDATE.username);
  const results = await screen.findByRole("listbox");
  await user.click(
    within(results).getByRole("button", { name: new RegExp(CANDIDATE.username) }),
  );
}

describe("CreateUserModal — Enterprise User membership", () => {
  afterEach(() => cleanup());

  beforeEach(() => {
    adminBranchId = ADMIN_BRANCH_ID;
    createUser.mockReset();
    fetchRoles.mockReset();
    fetchBranches.mockReset();
    fetchUsers.mockReset();

    fetchRoles.mockResolvedValue([
      {
        id: AGENT_ROLE_ID,
        code: "AGENT",
        name: "Agent",
        description: null,
        isSystem: false,
        isActive: true,
      },
      {
        id: ADMIN_ROLE_ID,
        code: "ADMIN",
        name: "Administrator",
        description: null,
        isSystem: false,
        isActive: true,
      },
      {
        id: SUPERVISOR_ROLE_ID,
        code: "SUPERVISOR",
        name: "Supervisor",
        description: null,
        isSystem: false,
        isActive: true,
      },
      {
        id: "r4444444-4444-4444-4444-444444444444",
        code: "MANAGER",
        name: "Manager",
        description: null,
        isSystem: false,
        isActive: true,
      },
      {
        id: "r5555555-5555-5555-5555-555555555555",
        code: "VIEWER",
        name: "Viewer",
        description: null,
        isSystem: false,
        isActive: true,
      },
      {
        id: "r6666666-6666-6666-6666-666666666666",
        code: "BRANCH_SUPERVISOR",
        name: "Branch Supervisor",
        description: null,
        isSystem: false,
        isActive: true,
      },
    ]);
    fetchBranches.mockResolvedValue({
      data: [
        { id: ADMIN_BRANCH_ID, code: "OU-A", name: "Regional Jawa Barat" },
        { id: OTHER_BRANCH_ID, code: "OU-B", name: "Regional Sumatera" },
        {
          id: CANDIDATE_BRANCH_ID,
          code: CANDIDATE.homeBranchCode,
          name: CANDIDATE.homeBranchName,
        },
        {
          id: PUSAT_BRANCH_ID,
          code: "PUSAT",
          name: "Pusat",
        },
      ],
    });
    fetchUsers.mockResolvedValue({ data: [], meta: { totalItems: 0 } });
    createUser.mockResolvedValue({
      username: CANDIDATE.username,
      fullName: CANDIDATE.displayName,
    });
  });

  it("never renders Temporary Password UI", async () => {
    const user = userEvent.setup();
    renderModal();
    await selectCandidate(user);

    expect(screen.queryByLabelText(/Temporary password/i)).toBeNull();
    expect(screen.queryByText(/temporary password/i)).toBeNull();
    expect(screen.queryByText(/force password change/i)).toBeNull();
    expect(document.body.textContent).not.toMatch(/temporary password/i);
  });

  it("searches the Mock Enterprise Directory and fills identity read-only", async () => {
    const user = userEvent.setup();
    renderModal();
    await selectCandidate(user);

    const employeeId = screen.getByLabelText(/Employee ID/i);
    const fullName = screen.getByLabelText(/Full name/i);
    const email = screen.getByLabelText(/^Email/i);

    expect(employeeId).toHaveValue(CANDIDATE.username);
    expect(fullName).toHaveValue(CANDIDATE.displayName);
    expect(email).toHaveValue(CANDIDATE.email);

    // Enterprise identity is displayed only — ECMP never edits it.
    for (const field of [employeeId, fullName, email]) {
      expect(field).toHaveAttribute("readonly");
      expect(field).toBeDisabled();
    }
  });

  it("hides head-office roles for a candidate based at a branch", async () => {
    const user = userEvent.setup();
    renderModal();
    await selectCandidate(user);

    const roleField = screen.getByLabelText(/Role/i);
    expect(within(roleField).getByRole("option", { name: /^Officer$/ })).toBeInTheDocument();
    expect(within(roleField).getByRole("option", { name: /^Supervisor$/ })).toBeInTheDocument();
    expect(within(roleField).getByRole("option", { name: /^Manager$/ })).toBeInTheDocument();
    expect(within(roleField).queryByRole("option", { name: /^Admin$/ })).toBeNull();
    expect(within(roleField).queryByRole("option", { name: /Viewer/i })).toBeNull();
    expect(within(roleField).queryByRole("option", { name: /Branch Supervisor/i })).toBeNull();
  });

  it("offers Admin plus operational roles for a Pusat candidate", async () => {
    const user = userEvent.setup();
    renderModal();
    const search = await screen.findByLabelText(/Search candidate/i);
    await user.type(search, HEAD_OFFICE_CANDIDATE.username);
    const results = await screen.findByRole("listbox");
    await user.click(
      within(results).getByRole("button", {
        name: new RegExp(HEAD_OFFICE_CANDIDATE.username),
      }),
    );

    const roleField = screen.getByLabelText(/Role/i);
    expect(within(roleField).getByRole("option", { name: /^Admin$/ })).toBeInTheDocument();
    expect(within(roleField).getByRole("option", { name: /^Officer$/ })).toBeInTheDocument();
    expect(within(roleField).getByRole("option", { name: /^Supervisor$/ })).toBeInTheDocument();
    expect(within(roleField).getByRole("option", { name: /^Manager$/ })).toBeInTheDocument();
    expect(within(roleField).queryByRole("option", { name: /Viewer/i })).toBeNull();
    expect(screen.getByLabelText(/^Unit/i)).toHaveValue("PUSAT — Pusat");
  });

  it("registers a Pusat officer against the PUSAT unit", async () => {
    const user = userEvent.setup();
    renderModal();
    const search = await screen.findByLabelText(/Search candidate/i);
    await user.type(search, HEAD_OFFICE_CANDIDATE.username);
    const results = await screen.findByRole("listbox");
    await user.click(
      within(results).getByRole("button", {
        name: new RegExp(HEAD_OFFICE_CANDIDATE.username),
      }),
    );

    await user.selectOptions(screen.getByLabelText(/Role/i), AGENT_ROLE_ID);
    await user.click(screen.getByRole("button", { name: /Register user/i }));

    await waitFor(() => expect(createUser).toHaveBeenCalledTimes(1));
    expect(createUser.mock.calls[0]![0]).toMatchObject({
      roleId: AGENT_ROLE_ID,
      branchId: PUSAT_BRANCH_ID,
    });
  });

  it("clears unit when registering a Pusat administrator", async () => {
    const user = userEvent.setup();
    renderModal();
    const search = await screen.findByLabelText(/Search candidate/i);
    await user.type(search, HEAD_OFFICE_CANDIDATE.username);
    const results = await screen.findByRole("listbox");
    await user.click(
      within(results).getByRole("button", {
        name: new RegExp(HEAD_OFFICE_CANDIDATE.username),
      }),
    );

    await user.selectOptions(screen.getByLabelText(/Role/i), ADMIN_ROLE_ID);
    expect(screen.getByLabelText(/^Unit/i)).toHaveValue("Head Office");
    await user.click(screen.getByRole("button", { name: /Register user/i }));

    await waitFor(() => expect(createUser).toHaveBeenCalledTimes(1));
    expect(createUser.mock.calls[0]![0]).toMatchObject({
      roleId: ADMIN_ROLE_ID,
      branchId: null,
    });
  });

  it("takes Unit from the candidate's directory home unit and locks it", async () => {
    const user = userEvent.setup();
    renderModal();
    await selectCandidate(user);

    const unit = screen.getByLabelText(/^Unit/i);
    expect(unit).toHaveValue(
      `${CANDIDATE.homeBranchCode} — ${CANDIDATE.homeBranchName}`,
    );
    expect(unit).toHaveAttribute("readonly");
    // Never a chooser: the unit is already decided by the Enterprise Directory.
    expect(unit.tagName).toBe("INPUT");
    expect(screen.queryByText("OU-B — Regional Sumatera")).toBeNull();
  });

  it("keeps Unit locked to the directory even for an all-units administrator", async () => {
    adminBranchId = null;
    const user = userEvent.setup();
    renderModal();
    await selectCandidate(user);

    await user.selectOptions(screen.getByLabelText(/Role/i), AGENT_ROLE_ID);
    const unit = screen.getByLabelText(/^Unit/i);
    expect(unit.tagName).toBe("INPUT");

    await user.click(screen.getByRole("button", { name: /Register user/i }));

    await waitFor(() => expect(createUser).toHaveBeenCalledTimes(1));
    expect(createUser.mock.calls[0]![0]).toMatchObject({
      branchId: CANDIDATE_BRANCH_ID,
    });
  });

  it("saves ECMP authorization data with the directory unit", async () => {
    const user = userEvent.setup();
    const { onCreated } = renderModal();
    await selectCandidate(user);

    await user.selectOptions(screen.getByLabelText(/Role/i), AGENT_ROLE_ID);
    await user.click(screen.getByRole("button", { name: /Register user/i }));

    await waitFor(() => expect(createUser).toHaveBeenCalledTimes(1));
    expect(createUser.mock.calls[0]![0]).toMatchObject({
      username: CANDIDATE.username,
      roleId: AGENT_ROLE_ID,
      branchId: CANDIDATE_BRANCH_ID,
      isActive: true,
    });
    expect(typeof createUser.mock.calls[0]![0].password).toBe("string");
    expect(createUser.mock.calls[0]![0].password).toBe(MODE_A_LAB_TEMP_PASSWORD);
    expect(onCreated).toHaveBeenCalledWith(CANDIDATE.displayName);
  });

  it("sends the administrator-chosen initial status", async () => {
    const user = userEvent.setup();
    renderModal();
    await selectCandidate(user);

    await user.selectOptions(screen.getByLabelText(/Role/i), AGENT_ROLE_ID);
    await user.selectOptions(screen.getByLabelText(/Initial status/i), "false");
    await user.click(screen.getByRole("button", { name: /Register user/i }));

    await waitFor(() => expect(createUser).toHaveBeenCalledTimes(1));
    expect(createUser.mock.calls[0]![0]).toMatchObject({ isActive: false });
  });

  it("blocks submission until a directory user is selected", async () => {
    renderModal();
    await waitFor(() => expect(fetchRoles).toHaveBeenCalled());
    expect(screen.getByRole("button", { name: /Register user/i })).toBeDisabled();
    expect(createUser).not.toHaveBeenCalled();
  });
});
