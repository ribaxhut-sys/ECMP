import { describe, expect, it } from "vitest";
import type { RoleRef, UserRef } from "@/lib/api";
import {
  directoryRoleFamily,
  directoryRoleLabel,
  filterRolesForHomeUnit,
  filterRolesForUserForm,
  matchesDirectoryFilter,
  matchesDirectorySearch,
  roleDisplayName,
  userInitials,
} from "./directoryHelpers";

function user(partial: Partial<UserRef>): UserRef {
  return {
    id: "1",
    username: "jdoe",
    email: "jdoe@example.com",
    fullName: "Jane Doe",
    roleId: "r1",
    roleCode: null,
    roleName: null,
    branchId: null,
    isActive: true,
    lastLoginAt: null,
    createdAt: "2026-01-01T00:00:00Z",
    updatedAt: "2026-01-02T00:00:00Z",
    ...partial,
  };
}

describe("userInitials", () => {
  it("uses two name parts", () => {
    expect(userInitials(user({ fullName: "Ada Lovelace" }))).toBe("AL");
  });

  it("falls back to username", () => {
    expect(userInitials(user({ fullName: "", username: "ops" }))).toBe("OP");
  });
});

describe("directoryRoleFamily", () => {
  it("classifies known families", () => {
    expect(directoryRoleFamily(user({ roleCode: "ADMIN" }))).toBe(
      "administrator",
    );
    expect(directoryRoleFamily(user({ roleName: "Supervisor Desk" }))).toBe(
      "supervisor",
    );
    expect(directoryRoleFamily(user({ roleCode: "AGENT" }))).toBe("agent");
    expect(directoryRoleFamily(user({ roleCode: "VIEWER" }))).toBe("viewer");
  });
});

describe("directoryRoleLabel", () => {
  it("prefers family label then raw role", () => {
    expect(
      directoryRoleLabel(
        user({ roleCode: "ADMIN" }),
        {
          administrator: "Administrator",
          supervisor: "Supervisor",
          agent: "Agent",
          viewer: "Viewer",
          other: "—",
        },
        "—",
      ),
    ).toBe("Administrator");

    expect(
      directoryRoleLabel(
        user({ roleName: "Custom Lead" }),
        {
          administrator: "Administrator",
          supervisor: "Supervisor",
          agent: "Agent",
          viewer: "Viewer",
          other: "—",
        },
        "—",
      ),
    ).toBe("Custom Lead");
  });
});

describe("matchesDirectoryFilter", () => {
  it("filters by status and role family", () => {
    const admin = user({ roleCode: "ADMIN", isActive: true });
    const inactive = user({ id: "2", isActive: false, roleCode: "AGENT" });
    expect(matchesDirectoryFilter(admin, "administrator")).toBe(true);
    expect(matchesDirectoryFilter(inactive, "active")).toBe(false);
    expect(matchesDirectoryFilter(inactive, "inactive")).toBe(true);
    expect(matchesDirectoryFilter(inactive, "agent")).toBe(true);
  });
});

describe("matchesDirectorySearch", () => {
  it("matches only name and employee ID", () => {
    const row = user({ roleName: "Supervisor" });
    expect(matchesDirectorySearch(row, "jane")).toBe(true);
    expect(matchesDirectorySearch(row, "jdoe")).toBe(true);
    expect(matchesDirectorySearch(row, "superv")).toBe(false);
    expect(matchesDirectorySearch(row, "jdoe@example.com")).toBe(false);
    expect(matchesDirectorySearch(row, "zzz")).toBe(false);
  });
});

describe("roleDisplayName", () => {
  function role(partial: Partial<RoleRef>): Pick<RoleRef, "code" | "name"> {
    return {
      code: "AGENT",
      name: "Agent",
      ...partial,
    };
  }

  it("overrides BRANCH_SUPERVISOR with the given label", () => {
    expect(
      roleDisplayName(
        role({ code: "BRANCH_SUPERVISOR", name: "Branch Supervisor" }),
        "Manager Cabang",
      ),
    ).toBe("Manager Cabang");
  });

  it("leaves every other role code as the raw role name", () => {
    expect(
      roleDisplayName(role({ code: "SUPERVISOR", name: "Supervisor" }), "Manager Cabang"),
    ).toBe("Supervisor");
    expect(
      roleDisplayName(role({ code: "ADMIN", name: "Administrator" }), "Manager Cabang"),
    ).toBe("Administrator");
  });
});

describe("filterRolesForUserForm", () => {
  function role(partial: Partial<RoleRef> & Pick<RoleRef, "code">): RoleRef {
    return {
      description: null,
      isSystem: true,
      isActive: true,
      ...partial,
      id: partial.id ?? partial.code,
      code: partial.code,
      name: partial.name ?? partial.code,
    };
  }

  it("keeps only canonical personas and sorts them", () => {
    const filtered = filterRolesForUserForm([
      role({ code: "VIEWER" }),
      role({ code: "BRANCH_OFFICER" }),
      role({ code: "ADMIN" }),
      role({ code: "HO_ENGINEER" }),
      role({ code: "AGENT" }),
      role({ code: "SUPERVISOR" }),
      role({ code: "BRANCH_SUPERVISOR" }),
      role({ code: "ADMINISTRATOR" }),
    ]);
    expect(filtered.map((row) => row.code)).toEqual([
      "ADMIN",
      "SUPERVISOR",
      "BRANCH_SUPERVISOR",
      "AGENT",
      "VIEWER",
    ]);
  });
});

describe("filterRolesForHomeUnit", () => {
  function role(code: string): RoleRef {
    return {
      id: code,
      code,
      name: code,
      description: null,
      isSystem: true,
      isActive: true,
    };
  }

  const pool = [
    role("ADMIN"),
    role("SUPERVISOR"),
    role("AGENT"),
    role("VIEWER"),
  ];

  it("hides head-office roles for branch members", () => {
    expect(filterRolesForHomeUnit(pool, false).map((r) => r.code)).toEqual([
      "SUPERVISOR",
      "AGENT",
      "VIEWER",
    ]);
  });

  it("offers the full persona set for Pusat members including Admin", () => {
    expect(filterRolesForHomeUnit(pool, true).map((r) => r.code)).toEqual([
      "ADMIN",
      "SUPERVISOR",
      "AGENT",
      "VIEWER",
    ]);
  });
});
